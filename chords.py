#!/usr/bin/env python

from midi import Chord, play, sequence

from itertools import islice
from time import sleep
import sys
import os

import pygame as pg
import pygame.midi

chord_degrees = ("i", "ii", "iii", "iv", "v", "vi", "vii")

triads = {
    (3, 3): "diminished",
    (3, 4): "minor",
    (4, 3): "major",
    (4, 4): "augmented",
}


chords = {s: i for i, s in enumerate(chord_degrees)}

major_scale = (0, 2, 4, 5, 7, 9, 11)
minor_scale = (0, 2, 3, 5, 7, 8, 10)


class Progression:
    def __init__(self, progression, scale=major_scale):
        self.progression = progression
        self.scale = scale

    def play(self, midi_out, root, bpm):
        pitches = [
            triad(root, self.scale, chords[c.lower()])
            for c in self.progression.split("-")
        ]
        play(midi_out, sequence([Chord(1, c, 127) for c in pitches], bpm))


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
    starting at the given degree of the scale.
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

        Progression("I-IV-V-I").play(midi_out, 60, 120)
        Progression("I-ii-iii-IV-V-vi-vii-I").play(midi_out, 60, 180)

    finally:
        del midi_out
        pygame.midi.quit()


if __name__ == "__main__":

    device_id = int(sys.argv[1]) if len(sys.argv) > 1 else None

    run(device_id)
