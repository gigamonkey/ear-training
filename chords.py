#!/usr/bin/env python

import random
import sys
from itertools import islice
from itertools import permutations
from itertools import product

import pygame as pg
import pygame.midi

from midi import Chord
from midi import Note
from midi import parallel
from midi import play
from midi import sequence

chord_degrees = ("i", "ii", "iii", "iv", "v", "vi", "vii")

triads = {
    (3, 3): "diminished",
    (3, 4): "minor",
    (4, 3): "major",
    (4, 4): "augmented",
}

roman = {
    "major": str.upper,
    "minor": str.lower,
    "diminished": lambda d: d.lower() + "°",
    "augmented": lambda d: d.upper + "⁺",
}

chords = {s: i for i, s in enumerate(chord_degrees)}

major_scale = (0, 2, 4, 5, 7, 9, 11)
minor_scale = (0, 2, 3, 5, 7, 8, 10)


def roman_letters(scale):
    return [
        roman[kind_of_triad(t)](chord_degrees[i])
        for i, t in [(i, triad(0, scale, i)) for i in range(7)]
    ]


class Progression:
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

    def play_random_bass(self, midi_out, root, bpm):
        triads = [Chord(1, triad(root, self.scale, d)) for d in self.progression]
        bass = [Note(1, random.choice(c.pitches) - 12) for c in triads]
        play(midi_out, parallel([triads, bass], bpm))

    def play_random_voicing(self, midi_out, root, bpm):
        triads = [list(triad(root, self.scale, d)) for d in self.progression]
        for t in triads:
            random.shuffle(t)
            t.append(random.choice(t) - 12)
            t.append(random.choice(t) + 12)
        play(midi_out, sequence([Chord(1, t) for t in triads], bpm))


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
