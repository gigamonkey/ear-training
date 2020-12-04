#!/usr/bin/env python

"Code for dealing with abstracted musical structures."

import random
from itertools import islice

from midi import Note
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


def scale_up_down(scale, root, bpm):
    pitches = list(islice(notes(root, scale), len(scale) + 1))
    return list(
        sequence([Note(0.5, p) for p in pitches + list(reversed(pitches))], bpm)
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


class Solfege:
    def __init__(self, name, degree, scale=major_scale):
        self.name = name
        self.degree = degree
        self.scale = scale

    def render(self, root, bpm):
        pitch = next(islice(notes(root, self.scale), self.degree - 1, self.degree))
        return list(sequence([Note(1, root), Note(1, pitch)], bpm))

    def render_walk_back_to_do(self, root, bpm):
        pitches = list(reversed(list(islice(notes(root, self.scale), self.degree))))
        return list(sequence([Note(0.5, p) for p in pitches] + [Note(1, root, 0)], bpm))


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


def chord_intervals(chord):
    return [intervals[chord[i] - chord[0]] for i in range(1, len(chord))]


def kind_of_triad(triad):
    a, b, c = triad
    return triads[(b - a, c - b)]
