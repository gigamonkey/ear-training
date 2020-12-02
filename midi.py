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


from dataclasses import dataclass
from typing import List
import pygame
import pygame.midi
import time


@dataclass(frozen=True)
class NoteOn:

    pitch: int
    velocity: int
    time: float

    def emit(self, midi_out):
        midi_out.note_on(self.pitch, self.velocity)


@dataclass(frozen=True)
class NoteOff:

    pitch: int
    time: float

    def emit(self, midi_out):
        midi_out.note_off(self.pitch)


@dataclass(frozen=True)
class Playable:

    duration: float

    def note_ons(self, t):
        return []

    def note_offs(self, t):
        return []


@dataclass(frozen=True)
class Note(Playable):

    pitch: int
    velocity: int

    def note_ons(self, t):
        yield NoteOn(self.pitch, self.velocity, t)

    def note_offs(self, t):
        yield NoteOff(self.pitch, t)


@dataclass(frozen=True)
class Chord(Playable):

    pitches: List[int]
    velocity: int

    def note_ons(self, t):
        for p in self.pitches:
            yield NoteOn(p, self.velocity, t)

    def note_offs(self, t):
        for p in self.pitches:
            yield NoteOff(p, t)


class Line:

    def __init__(self):
        self.playables = []

    def note(self, pitch, duration=1, velocity=127):
        self.playables.append(Note(duration, pitch, velocity))
        return self

    def rest(self, duration=1):
        self.playables.append(Rest(duration))
        return self

    def chord(self, pitches, duration=1, velocity=127):
        self.playables.append(Chord(duration, pitches, velocity))
        return self


class Rest(Playable):

    pass


def play(midi_out, events):

    t_zero = time.monotonic()

    for e in events:
        # TODO: check accuracy of sleep timing
        t = time.monotonic()
        at = t_zero + e.time
        if at > t:
            time.sleep(at - t)
        e.emit(midi_out)


def sequence(midi: List[Playable], bpm: float):

    "Render a sequence of Playables into note on/off events at a given tempo."

    # BPM is quarter notes per minute and durations are in quarter
    # notes, therefore each quarter note is 60 / bpm seconds long.

    per_quarter_note = 60 / bpm

    t = 0

    for m in midi:
        yield from m.note_ons(t)
        t += m.duration * per_quarter_note
        yield from m.note_offs(t)


def parallel(midi: List[List[Playable]], bpm: float):

    "Render multiple sequences of Playables in parallel into note on/off events at a given tempo."

    return merge((sequence(s, bpm) for s in midi), key=lambda e: e.time)


def merge(iterables, key):

    "Merge separate sorted iterators into a single sorted iterator."

    to_merge = []

    def insert_next(s):
        if (o := next(s, None)) is not None:
            i = next(
                (i for i, (n, _) in enumerate(to_merge) if key(n) > key(o)),
                len(to_merge),
            )
            to_merge.insert(i, (o, s))

    for s in iterables:
        insert_next(iter(s))

    while to_merge:
        o, s = to_merge.pop(0)
        yield o
        insert_next(s)

def triplet(base):

    return (base * 2) / 3


if __name__ == "__main__":

    quarter_triplet = triplet(1)

    click = Line().note(96, duration=quarter_triplet/2).rest(quarter_triplet/2).playables * 6
    midi = Line().note(60 - 12).rest().chord([60, 64, 67], duration=2, velocity=120).playables

    together = parallel([click, midi], 120.0)

    pygame.init()
    pygame.midi.init()

    port = pygame.midi.get_default_output_id()

    midi_out = pygame.midi.Output(port, 0)

    try:
        midi_out.set_instrument(0)

        play(midi_out, parallel([click, midi], 120.0))
        play(midi_out, parallel([click, midi], 180.0))

    finally:
        del midi_out
        pygame.midi.quit()
