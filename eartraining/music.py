"API for manipulating musical elements."

from dataclasses import dataclass
from typing import Tuple

from eartraining.midi import Note
from eartraining.midi import Parallel
from eartraining.midi import Sequence


def chord(pitches):
    "Build a chord out of the given pitches."
    return Parallel([Note(n) for n in pitches])


def melody(pitches):
    "Build a melody line out of the given pitches."
    return Sequence([Note(n) if n is not None else Rest() for n in pitches])


def silence(duration):
    "Since rests get smooshed out at the end of lines."
    return Note(0, duration, 0)


#
# Scales - scales are defined by a pattern of notes of one octave
# represented by a tuple of semitones above the root. E.g. (0, 2, 4,
# 5, 7, 9, 11) is a major scale. Using a Scale object we can translate
# from numbers of degrees (1-7 for a normal seven note scale like the
# major scale; 1-5 for pentatonic scales, and so on) to notes relative
# to a root. If we're using the Scale to get notes which we are going
# to turn into MIDI via the chord() and melody() functions we can use
# a root of 0 and then let the actual root be set in the MIDI
# rendering process.
#


def scale(pattern, root=0):
    return Scale(pattern, root)


@dataclass
class Scale:

    pattern: Tuple[int]
    root: int = 0

    major = (0, 2, 4, 5, 7, 9, 11)
    minor = (0, 2, 3, 5, 7, 8, 10)
    pentatonic_major = (0, 2, 4, 7, 9)

    @property
    def one_octave(self):
        return self.notes(range(1, len(self.pattern) + 1))

    def note(self, n):
        "Return the note of the scale at a given degree."
        octave, degree = divmod(n - 1, len(self.pattern))
        return self.root + self.pattern[degree] + (octave * 12)

    def notes(self, steps):
        return [self.note(s) for s in steps]

    def triad(self, n):
        return tuple(self.note(d) for d in range(n, n + 6, 2))

    def seventh_chord(self, n):
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


roman_numerals = (None, "i", "ii", "iii", "iv", "v", "vi", "vii")

romanization_fns = {
    "major": str.upper,
    "minor": str.lower,
    "diminished": lambda d: d.lower() + "°",
    "augmented": lambda d: d.upper + "⁺",
}


def roman(d, triad):
    assert 1 <= d <= 7
    numeral = roman_numerals[d]
    fn = romanization_fns[kind_of_triad(triad)]
    return fn(numeral)


triads = {
    (3, 3): "diminished",
    (3, 4): "minor",
    (4, 3): "major",
    (4, 4): "augmented",
}


def kind_of_triad(triad):
    a, b, c = triad
    return triads[(b - a, c - b)]


def classify_interval(a, b):
    return intervals[b - a]


intervals = [
    "Perfect unison",
    "Minor second",
    "Major second",
    "Minor third",
    "Major third",
    "Perfect fourth",
    "Tritone",
    "Perfect fifth",
    "Minor sixth",
    "Major sixth",
    "Minor seventh",
    "Major seventh",
    "Perfect eighth",
]


chord_types = {
    (0, 4, 7): "Major",
    (0, 3, 7): "Minor",
    (0, 3, 6): "Diminished",
    (0, 4, 8): "Augmented",
    (0, 4, 7, 10): "Dominant 7",
    (0, 4, 7, 11): "Major 7",
    (0, 3, 7, 10): "Minor 7",
    (0, 3, 6, 10): "Minor 7♭5",
    (0, 3, 6, 9): "Diminished 7",
}


def chord_intervals(chord):
    return [intervals[chord[i] - chord[0]] for i in range(1, len(chord))]


if __name__ == "__main__":

    s = scale((0, 2, 4, 5, 7, 9, 11))

    for i in range(24):
        triad = s.triad(i)
        print(
            f"{i}: {s.note(i)} -> {triad} / {s.seventh_chord(i)} ({roman(i, triad)}) ({chord_intervals(triad)})"
        )
