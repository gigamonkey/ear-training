"Abstracted collections of notes in sequence and parallel."


import dataclasses
from collections import Counter
from dataclasses import dataclass
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
        midi_out.note_on(self.pitch, self.velocity)


@dataclass
class NoteOff:

    """
    A MIDI note off event that should be emitted at a given time
    relative to zero time.
    """

    note: int
    time: float

    def emit(self, midi_out):
        midi_out.note_off(self.pitch)


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

    def render(self, root, quarter_note):
        on_off = sorted(
            self.midi(0, root, quarter_note),
            key=lambda e: (e.time, isinstance(e, NoteOn), e.note),
        )

        on = Counter()
        filtered = []
        for e in on_off:
            if isinstance(e, NoteOn):
                if on[e.note] == 0:
                    filtered.append(e)
                on[e.note] += 1
            elif isinstance(e, NoteOff):
                on[e.note] -= 1
                if on[e.note] == 0:
                    filtered.append(e)

        return filtered


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
    velocity: int = 127
    duration: float = 1.0

    def midi(self, start, root, quarter_note):
        note = root + self.pitch
        yield NoteOn(note, self.velocity, start)
        yield NoteOff(note, start + (self.duration * quarter_note))

    def transpose(self, transposition):
        return dataclasses.replace(self, pitch=self.pitch + transposition)

    @property
    def sequential(self):
        return [self]

    @property
    def parallel(self):
        return [self]


@dataclass(frozen=True)
class Rest(Playable):

    duration: float = 1.0

    def midi(self, start, root, quarter_note):
        yield Time(start + (self.duration * quarter_note))

    def transpose(self, transposition):
        return self

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

    sequential: List[Playable]

    def midi(self, start, root, quarter_note):
        t = start
        for c in self.sequential:
            # The child may emit multiple MIDI events but it is over
            # whenever the last event is. We don't assume that the
            # events are necessarily emitted in order.
            for e in c.midi(t, root, quarter_note):
                t = max(t, e.time)
                if not isinstance(e, Time):
                    yield e

    def transpose(self, transposition):
        return dataclasses.replace(
            self, sequential=[c.transpose(transposition) for c in self.sequential]
        )

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

    parallel: List[Playable]

    def midi(self, start, root, quarter_note):
        for c in self.parallel:
            yield from c.midi(start, root, quarter_note)

    def transpose(self, transposition):
        return dataclasses.replace(
            self, parallel=[c.transpose(transposition) for c in self.parallel]
        )

    @property
    def sequential(self):
        return [self]


def chord(notes):
    return Parallel([Note(n) for n in notes])


def melody(notes):
    return Sequence([Note(n) for n in notes])


if __name__ == "__main__":

    I = chord((0, 4, 7))
    IV = I.transpose(5)
    V = I.transpose(7)

    m = melody((0, 7, 0, 7, 5, 4, 2, 0)) + Rest(4) + melody((0, 7, 0, 7, 5, 4, 2, 0))
    h = I + V + IV + I

    # x = m.transpose(12) | h.transpose(-12)
    x = m | h

    for e in x.render(60, 60 / 120):
        print(e)
