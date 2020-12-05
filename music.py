"API for manipulating musical elements."

from dataclasses import dataclass
from typing import Tuple

from midi import Note
from midi import Parallel
from midi import Sequence


def chord(pitches):
    "Build a chord out of the given pitches."
    return Parallel([Note(n) for n in pitches])


def melody(pitches):
    "Build a melody line out of the given pitches."
    return Sequence([Note(n) if n is not None else Rest() for n in pitches])


#
# Scales - scales are defined by a pattern of notes of one octave
# represented by a tuple of semitones above the root. E.g. (0, 2, 4,
# 5, 7, 9, 11) is a major scale. We
#


def scale(pattern, root=0):
    return Scale(pattern, root)


@dataclass
class Scale:

    pattern: Tuple[int]
    root: int

    def note(self, n):
        "Return the note of the scale at the given degree, optionally transposed up or down by octaves."
        octave, degree = divmod(n, len(self.pattern))
        return self.root + self.pattern[degree] + (octave * 12)

    def triad(self, n):
        return tuple(self.note(d) for d in range(n, n + 6, 2))

    def seventh(self, n):
        return tuple(self.note(d) for d in range(n, n + 8, 2))


def inversion(chord, inversion):
    return tuple(chord[inversion:]) + tuple(n + 12 for n in chord[:inversion])


#
# Rhythmic elements. Durations are expressed in terms of whole notes
# so 1/4 is a quarter note.
#


def dotted(d):
    "The duration of a dotted value."
    return d * 1.5


def tuplet(base, numerator, denominator):
    """
    Duration of one element of a tuplet of N notes in the space of D
    base notes. E.g. tuplet(1/8, 3, 2) returns the length of one note
    in an eighth note triplet (three notes in the space of two eighth
    notes).
    """
    return base * (denominator / numerator)


def triplet(base):
    return tuplet(base, 3, 2)


#
# Utilities
#

major_scale = (0, 2, 4, 5, 7, 9, 11)
minor_scale = (0, 2, 3, 5, 7, 8, 10)
pentatonic_major_scale = (0, 2, 4, 7, 9)

chord_degrees = ("i", "ii", "iii", "iv", "v", "vi", "vii")

romanization_fns = {
    "major": str.upper,
    "minor": str.lower,
    "diminished": lambda d: d.lower() + "°",
    "augmented": lambda d: d.upper + "⁺",
}


def roman(d, triad):
    return romanization_fns[kind_of_triad(triad)](chord_degrees[d % 7])


triads = {
    (3, 3): "diminished",
    (3, 4): "minor",
    (4, 3): "major",
    (4, 4): "augmented",
}


def kind_of_triad(triad):
    a, b, c = triad
    return triads[(b - a, c - b)]


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


def chord_intervals(chord):
    return [intervals[chord[i] - chord[0]] for i in range(1, len(chord))]


if __name__ == "__main__":

    s = scale((0, 2, 4, 5, 7, 9, 11))

    for i in range(24):
        triad = s.triad(i)
        print(
            f"{i}: {s.note(i)} -> {triad} / {s.seventh(i)} ({roman(i, triad)}) ({chord_intervals(triad)})"
        )
