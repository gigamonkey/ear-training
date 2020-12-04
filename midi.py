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
from dataclasses import dataclass
from typing import List


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
    velocity: int = 127

    def transpose(self, steps):
        return Note(self.duration, self.pitch + steps, self.velocity)

    def note_ons(self, t):
        yield NoteOn(self.pitch, self.velocity, t)

    def note_offs(self, t):
        yield NoteOff(self.pitch, t)


@dataclass(frozen=True)
class Chord(Playable):

    pitches: List[int]
    velocity: int = 127

    def transpose(self, steps):
        return Chord(self.duration, [p + steps for p in self.pitches], velocity)

    def note_ons(self, t):
        for p in self.pitches:
            yield NoteOn(p, self.velocity, t)

    def note_offs(self, t):
        for p in self.pitches:
            yield NoteOff(p, t)


class Line:
    def __init__(self, playables=None):
        self.playables = playables or []

    def __iter__(self):
        return iter(self.playables)

    def __add__(self, other):
        return Line(self.playables + other.playables)

    def transpose(self, steps):
        l = Line()
        l.playables = [x.transpose(steps) for x in self.playables]
        return l

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
    def transpose(self, steps):
        return self


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

    t = 0.0

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


def tuplet(base, numerator, denominator):
    """
    Define a tuplet duration as numerator notes in the duration of
    denominator. E.g. a eight-note triplet is three notes in the space
    of two eight notes.
    """

    return (base * denominator) / numerator


def triplet(base):

    return tuplet(base, 3, 2)
