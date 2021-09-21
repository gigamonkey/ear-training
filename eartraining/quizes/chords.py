#!/usr/bin/env python

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
from eartraining.progressive import ProgressiveQuiz


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


def root_generator():
    while True:
        yield [random.randint(60 - 12, 60 + 12)]


if __name__ == "__main__":

    templates = [ChordTemplate(c) for c in chord_types.keys()]

    QuizUI("Chords", ProgressiveQuiz(templates, root_generator(), 3)).run()
