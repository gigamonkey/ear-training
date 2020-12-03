#!/usr/bin/env python

import random
import sys
from itertools import islice
from itertools import permutations

import pygame as pg
import pygame.midi

from midi import Chord
from midi import Note
from midi import Rest
from midi import play
from midi import sequence

chord_degrees = ("i", "ii", "iii", "iv", "v", "vi", "vii")

chord_types = {
    "Major": (0, 4, 7),
    "Minor": (0, 3, 7),
    "Diminished": (0, 3, 6),
    "Augmented": (0, 4, 8),
    "Major 7": (0, 4, 7, 11),
    "Minor 7": (0, 3, 7, 10),
    "Dominant 7": (0, 4, 7, 10),
    "Minor 7♭5": (0, 3, 6, 10),
    "Diminished 7": (0, 3, 6, 9),
}


triads = {
    (3, 3): "diminished",
    (3, 4): "minor",
    (4, 3): "major",
    (4, 4): "augmented",
}

intervals = [
    "P1",
    "m2",
    "M2",
    "m3",
    "M3",
    "P4",
    "A4",
    "P5",
    "m6",
    "M6",
    "m7",
    "M7",
    "P8",
]


roman = {
    "major": str.upper,
    "minor": str.lower,
    "diminished": lambda d: d.lower() + "°",
    "augmented": lambda d: d.upper + "⁺",
}

chords = {s: i for i, s in enumerate(chord_degrees)}

major_scale = (0, 2, 4, 5, 7, 9, 11)
minor_scale = (0, 2, 3, 5, 7, 8, 10)
pentatonic_major_scale = (0, 2, 4, 7, 9)


def roman_letters(scale):
    return [
        roman[kind_of_triad(t)](chord_degrees[i])
        for i, t in [(i, triad(0, scale, i)) for i in range(7)]
    ]


class Progression:

    """
    A slightly abstracted chord progression, expressed in terms of
    degrees of a given scale. Chords are built out of the notes of the
    scale.
    """

    def __init__(self, progression, scale=major_scale):
        self.progression = progression
        self.scale = scale
        self.names = roman_letters(scale)

    def name(self):
        return str(self)

    def __str__(self):
        return "-".join(self.names[d] for d in self.progression)

    def play(self, midi_out, root, bpm):
        triads = [Chord(1, triad(root, self.scale, d)) for d in self.progression]
        play(midi_out, sequence(triads, bpm))

    def render(self, root, voicing, bpm):
        return list(
            sequence(
                [Chord(1, voicing(root, self.scale, d)) for d in self.progression], bpm
            )
        )


class ChordType:

    """
    A slightly abstracted chord expressed in terms of a pattern of
    intervals from the root. E.g. (0, 4, 7) is a major triad."
    """

    def __init__(self, name, pattern):
        self.name = name
        self.pattern = pattern

    def __str__(self):
        return self.name

    def play(self, midi_out, root, bpm):
        play(midi_out, sequence([Chord(1, chord(root, self.pattern))], bpm))

    def render_chord(self, root, bpm):
        return list(sequence([Chord(1, chord(root, self.pattern))], bpm))

    def render_arpeggio_up(self, root, bpm):
        return list(sequence([Note(1 / 2, root + p) for p in self.pattern], bpm))

    def render_arpeggio_and_chord(self, root, bpm):
        notes = chord(root, self.pattern)
        return list(
            sequence(
                [Note(0.5, n) for n in notes] + [Rest(0.5), Chord(1, notes)],
                bpm,
            )
        )


def random_voicing(root, scale, d):
    t = triad(root, scale, d)
    t = random_inversion(t)
    t.append(random.choice(t) - 12)
    t.append(random.choice(t) + 12)
    if random.choice((True, False)):
        t = [n - 12 for n in t]
    return t


def random_inversion(notes):
    inversion = random.randrange(len(notes))
    return list(notes[inversion:]) + list(n + 12 for n in notes[:inversion])


def notes(root, one_octave):
    "Yield infinite octaves of a given pattern (e.g. a mode) starting from a root note."
    octave = 0
    while True:
        for n in one_octave:
            yield root + n + (octave * 12)
        octave += 1


def triad(root, scale, degree):
    """
    Build a triad on the notes of the given scale, rooted at root,
    starting at the given zero-indexed degree of the scale.
    """
    return tuple(islice(notes(root, scale), degree, degree + 6, 2))


def chord(root, pattern):
    return tuple(root + p for p in pattern)


def reroot(chord):
    return tuple(x - chord[0] for x in chord)


def chord_intervals(chord):
    return [intervals[chord[i] - chord[0]] for i in range(1, len(chord))]


def kind_of_triad(triad):
    a, b, c = triad
    return triads[(b - a, c - b)]


def run(device_id=None):

    pg.init()
    pygame.midi.init()

    port = pygame.midi.get_default_output_id() if device_id is None else device_id

    midi_out = pygame.midi.Output(port, 0)

    try:
        midi_out.set_instrument(0)

        all_progressions = [
            p for p in permutations(range(7), 4) if p[0] == 0 or p[-1] == 0
        ]

        p = Progression(random.choice(all_progressions))
        p.play(midi_out, 60, 120)
        print(p)

    finally:
        del midi_out
        pygame.midi.quit()


if __name__ == "__main__":

    device_id = int(sys.argv[1]) if len(sys.argv) > 1 else None

    run(device_id)
