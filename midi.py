"""
Abstracted representation of notes, chords, and rests and
functions for rendering them into note on/note off events.

Notes, chords, and rests have only a duration, expressed in terms of
(possibly fractional) quarter notes but can be arranged in a list
which can then be rendered as a sorted list of note on and note off
events.

Multiple sequences can be combined in parallel to allow overlapping
notes.
"""

import time
from collections import Counter
from dataclasses import dataclass
from dataclasses import replace
from itertools import cycle
from typing import List


def play(midi_out, events):

    "Play a sorted series of NoteOn/NoteOff events."

    t_zero = time.monotonic()

    for e in events:
        # TODO: check accuracy of sleep timing
        t = time.monotonic()
        at = t_zero + e.time
        if at > t:
            time.sleep(at - t)
        e.emit(midi_out)


@dataclass
class NoteOn:

    """
    A MIDI note on event that should be emitted at a given time
    relative to zero time.
    """

    note: int
    velocity: int
    time: float

    def emit(self, midi_out):
        midi_out.note_on(self.note, self.velocity)


@dataclass
class NoteOff:

    """
    A MIDI note off event that should be emitted at a given time
    relative to zero time.
    """

    note: int
    time: float

    def emit(self, midi_out):
        midi_out.note_off(self.note)


@dataclass
class Time:

    "Fake event used to advance time in sequences to implement rests."

    time: float


@dataclass
class Playable:

    """
    Anything that can be rendered into MIDI events and combined with
    other Playables either as part of a sequence or in parallel. They
    can also be manipulated in various ways.
    """

    def __add__(self, other):
        return Sequence(self.for_sequence() + other.for_sequence())

    def __mul__(self, other):
        return Sequence(self.for_sequence() * other)

    def __or__(self, other):
        return Parallel(self.for_parallel() + other.for_parallel())

    def transpose(self, steps):
        return replace(self, children=[c.transpose(steps) for c in self.children])

    def up(self, steps):
        return self.transpose(steps)

    def down(self, steps):
        return self.transpose(-steps)

    def rhythm(self, duration):
        "Apply a rhythmic value to the Playable."

    def render(self, root, bpm):
        def ordering(e):
            return ((e.time, isinstance(e, NoteOn), e.note),)

        def filter(events):
            on = Counter()
            for e in sorted(events, key=ordering):
                if isinstance(e, NoteOn):
                    if on[e.note] == 0:
                        yield e
                    on[e.note] += 1
                elif isinstance(e, NoteOff):
                    on[e.note] -= 1
                    if on[e.note] == 0:
                        yield e

        return list(filter(self.midi(0, root, (60 / bpm) * 4)))


@dataclass
class Note(Playable):
    """
    A single note.

    Pitch is abstracted until notes are rendered to MIDI with a
    specific root which will be mapped to pitch 0.

    Duration is in absract whole notes with the actual duration to be
    determined when rendering to MIDI at a specific bpm.

    Velocity is the MIDI velocity (0-127). And
    """

    pitch: int
    duration: float = 1 / 4
    velocity: int = 127

    def midi(self, start, root, whole_note):
        note = root + self.pitch
        yield NoteOn(note, self.velocity, start)
        yield NoteOff(note, start + (self.duration * whole_note))

    def transpose(self, steps):
        return replace(self, pitch=self.pitch + steps)

    def rhythm(self, duration):
        return replace(self, duration=duration)

    def for_sequence(self):
        return [self]

    def for_parallel(self):
        return [self]


@dataclass
class Rest(Playable):

    """
    A rest. Takes up time before the next NoteOn in a Sequence.
    """

    duration: float = 1 / 4

    def midi(self, start, root, whole_note):
        yield Time(start + (self.duration * whole_note))

    def transpose(self, steps):
        return self

    def rhythm(self, duration):
        return replace(self, duration=duration)

    def for_sequence(self):
        return [self]

    def for_parallel(self):
        return []


@dataclass
class Sequence(Playable):

    """
    A sequence of Playable things. When rendering to MIDI each child
    starts after its preceeding sibling finishes, i.e. after the last
    note off event.
    """

    children: List[Playable]

    def midi(self, start, root, whole_note):
        t = start
        for c in self.children:
            # The child may emit multiple MIDI events but it is over
            # whenever the last event is. We don't assume that the
            # events are necessarily emitted in order.
            for e in c.midi(t, root, whole_note):
                t = max(t, e.time)
                if not isinstance(e, Time):
                    yield e

    def rhythm(self, durations):

        """
        When applied to a sequence the duration can be either a single
        value which is then applied to each child or an iterable of
        values which are applied in a cycle to the children.
        """

        try:
            iterable = iter(durations)
        except TypeError:
            iterable = [durations]

        return replace(
            self, children=[c.rhythm(d) for c, d in zip(self.children, cycle(iterable))]
        )

    def for_sequence(self):
        return self.children

    def for_parallel(self):
        return [self]


@dataclass
class Parallel(Playable):

    """
    Children are played in parallel so each child starts at the same
    time. They don't have to end at the same time however--each one
    can take however long it takes.
    """

    children: List[Playable]

    def midi(self, start, root, whole_note):
        for c in self.children:
            yield from c.midi(start, root, whole_note)

    def rhythm(self, duration):
        return replace(self, children=[c.rhythm(duration) for c in self.children])

    def for_sequence(self):
        return [self]

    def for_parallel(self):
        return self.children
