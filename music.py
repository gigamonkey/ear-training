"Abstracted collections of notes in sequence and parallel."

from collections import Counter
from dataclasses import dataclass
from dataclasses import replace
from itertools import cycle
from typing import List


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

    "Fake event to advance time in sequences."

    time: float


@dataclass
class Playable:
    def __add__(self, other):
        return Sequence(self.sequential + other.sequential)

    def __or__(self, other):
        return Parallel(self.parallel + other.parallel)

    def transpose(self, transposition):
        return replace(
            self, children=[c.transpose(transposition) for c in self.children]
        )

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


@dataclass(frozen=True)
class Note(Playable):
    """
    A single note. Pitch is abstracted until notes are rendered to
    MIDI with a specific root which will be mapped to pitch 0.
    Velocity is the MIDI velocity. And duration is in absract quarter
    notes with the actual duration to be determined when rendering to
    MIDI.
    """

    pitch: int
    duration: float = 1 / 4
    velocity: int = 127

    def midi(self, start, root, whole_note):
        note = root + self.pitch
        yield NoteOn(note, self.velocity, start)
        yield NoteOff(note, start + (self.duration * whole_note))

    def transpose(self, transposition):
        return replace(self, pitch=self.pitch + transposition)

    def rhythm(self, duration):
        return replace(self, duration=duration)

    @property
    def sequential(self):
        return [self]

    @property
    def parallel(self):
        return [self]


@dataclass(frozen=True)
class Rest(Playable):

    duration: float = 1 / 4

    def midi(self, start, root, whole_note):
        yield Time(start + (self.duration * whole_note))

    def transpose(self, transposition):
        return self

    def rhythm(self, duration):
        return replace(self, duration=duration)

    @property
    def sequential(self):
        return [self]

    @property
    def parallel(self):
        return []


@dataclass
class Sequence(Playable):

    """
    A sequence of playable things. When rendering to MIDI each child
    starts after it preceeding sibling. So we need to keep track of
    when the last note off event
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

    @property
    def sequential(self):
        return self.children

    @property
    def parallel(self):
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

    @property
    def sequential(self):
        return [self]

    @property
    def parallel(self):
        return self.children


def chord(notes):
    return Parallel([Note(n) for n in notes])


def melody(notes):
    return Sequence([Note(n) for n in notes])


def dotted(d):
    return d * 1.5


def tuplet(base, numerator, denominator):
    """
    Define a tuplet duration as numerator notes in the duration of
    denominator. E.g. a eight-note triplet is three notes in the space
    of two eight notes, so tuplet(1/8, 3, 2) gives us the duration of
    one note of an eigth-note triplet.
    """
    return (base * denominator) / numerator


def triplet(base):
    return tuplet(base, 3, 2)


if __name__ == "__main__":

    I = chord((0, 4, 7))
    IV = I.transpose(5)
    V = I.transpose(7)

    m1 = melody((0, 7, 0, 7, 5, 4, 2, 0))

    m = m1.rhythm(1 / 8) + Rest(1) + m1.rhythm([1 / 4 * 2 / 3, 1 / 4 * 1 / 3])
    h = I + (V + IV).rhythm(1 / 8) + I.rhythm(1 / 2)

    x = m.transpose(12) | h.transpose(-12)

    stacked = chord((0, 4, 7)) | chord((0, 4, 7)).transpose(12)

    for e in stacked.render(60, 60):
        print(e)
