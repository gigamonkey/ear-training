#!/usr/bin/env python

"""
Quiz of chords using set scheduler that weights questions that
you've gotten wrong more heavily and adds new questions when you have
gotten all current questions more right than wrong.
"""

import dataclasses
from dataclasses import dataclass
from typing import Tuple

from eartraining.app import Quiz
from eartraining.midi import play
from eartraining.music import chord
from eartraining.music import chord_types
from eartraining.music import melody
from eartraining.scheduler import SetQuestionScheduler


@dataclass(frozen=True)
class ChordQuestion:

    chord_pattern: Tuple[int]
    root_note: int

    def for_type(self, chord_pattern):
        return dataclasses.replace(self, chord_pattern=chord_pattern)

    @property
    def label(self):
        return chord_types[self.chord_pattern]

    @property
    def notes(self):
        return [self.root_note + i for i in self.chord_pattern]

    def options(self, in_play):
        return [self.for_type(s) for s in sorted({q.chord_pattern for q in in_play})]

    def play(self, midi_out):
        play(midi_out, chord(self.notes).render(0, 120))

    def hint(self, midi_out):
        play(midi_out, melody(self.notes).render(0, 120))

    def after_correct(self, midi_out):
        pass


class ChordsQuiz(Quiz):
    def __init__(self, name, kinds):
        super().__init__(name)

        def question_set(root):
            return [ChordQuestion(pattern, root) for pattern in kinds]

        fourths = [n % 12 for n in range(0, (5 * 12), 5)]
        octaves = [0] + [i * s for i in range(1, 5) for s in (1, -1)]
        roots = [(r + 60) + (o * 12) for o in octaves for r in fourths]
        question_sets = [question_set(r) for r in roots]
        self.scheduler = SetQuestionScheduler(question_sets, 0.5, 1.01, 5)

    def make_questions(self, _):
        expected = self.scheduler.draw()
        return expected, self.scheduler.options(expected)

    def update(self, choice, question):
        self.scheduler.update(choice, question)


if __name__ == "__main__":

    seventh_chords = [
        (0, 4, 7),  # "Major",
        (0, 3, 7),  # "Minor",
        (0, 3, 6),  # "Diminished",
        (0, 4, 8),  # "Augmented",
        # (0, 3, 6, 10),
        # (0, 3, 6, 9),
        # (0, 3, 7, 10),
        # (0, 4, 7, 10),
        # (0, 4, 7, 11),
    ]

    ChordsQuiz("Chords", seventh_chords).run()
