#!/usr/bin/env python

import argparse
import random
from dataclasses import dataclass
from dataclasses import replace
from typing import Tuple

from eartraining.app import Question
from eartraining.app import QuizUI
from eartraining.midi import play
from eartraining.music import chord
from eartraining.music import chord_types
from eartraining.music import melody
from eartraining.progressive import FixedQuiz


@dataclass
class ChordTemplate:
    "To be instantiated with a root note."

    notes: Tuple[int, ...]

    def instantiate(self, idx, root):
        return ChordQuestion(idx, self.notes, root)


@dataclass
class ChordQuestion(Question):

    idx: int
    notes: Tuple[int, ...]
    root: int

    @property
    def label(self):
        return chord_types[self.notes]

    def play(self, midi_out):
        play(midi_out, chord(self.notes).render(self.root, 120))

    def hint(self, midi_out):
        play(midi_out, melody(self.notes).render(self.root, 120))

    def align(self, other):
        # Find the root for the other chord such that common
        # structures line up. E.g. if self is a major triad (0, 4, 7)
        # and other is a minor 7th (0, 3, 7, 10) we want the root of
        # the other to be three semi-tones below the root of self so
        # that the notes of its top triad lines up with the notes of
        # our triad.
        #
        # Conversely, if self is the m7 and other is the major triad,
        # we want to shift the root of other up three semitones to
        # line up the notes.

        self_len = len(self.notes)
        other_len = len(other.notes)

        if self_len < other_len:
            # Shift other down and see if we can line it up with self.
            for i in range((other_len - self_len) + 1):
                other_shifted = tuple(n - other.notes[i] for n in other.notes)
                # print(f"other_shifted: {other_shifted}")
                if other_shifted[i : i + self_len] == self.notes:
                    return replace(other, root=self.root - other.notes[i])
        elif self_len > other_len:
            # Shift other up
            for i in range((self_len - other_len) + 1):
                other_shifted = tuple(n + self.notes[i] for n in other.notes)
                # print(f"other_shifted: {other_shifted}")
                if other_shifted == self.notes[i : i + other_len]:
                    return replace(other, root=self.root + self.notes[i])

        # Same length or couldn't find alignment
        return other


def growing_root_generator():
    low = random.randrange(60, 60 + 12)
    high = low
    count = 0
    while True:
        count += 1
        yield [random.randint(low, high)]
        if count % 10 == 0:
            if random.choice((True, False)):
                low -= 1
            else:
                high += 1
            print(f"range {low} to {high} ({high - low} notes)")


def root_generator(octaves):

    down = octaves // 2
    up = octaves - down

    low = 60 - (12 * down)
    high = 60 + (12 * up)

    print(f"low: {low}; high: {high}")
    while True:
        yield [random.randint(low, high)]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("quiz", help="Which quiz to run.")
    parser.add_argument("--octaves", type=int, default=1, help="Number of octaves.")

    args = parser.parse_args()

    match args.quiz:
        case "m7M7":
            to_ask = [(0, 4, 7, 11), (0, 3, 7, 10)]
        case "triads":
            to_ask = [c for c in chord_types if len(c) == 3]
        case "sevenths":
            to_ask = [c for c in chord_types if len(c) == 4]
        case other:
            exit(f"No quiz {other}")

    # templates = [ChordTemplate(c) for c in chord_types.keys()]
    templates = [ChordTemplate(c) for c in sorted(to_ask, reverse=True)]

    # QuizUI("Chords", PlusMinusProgressiveQuiz(templates, root_generator(), 3)).run()
    QuizUI("Chords", FixedQuiz(templates, root_generator(args.octaves))).run()
