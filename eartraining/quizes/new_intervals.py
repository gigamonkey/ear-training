#!/usr/bin/env python

"""
Quiz of intervals using scheduler that weights questions that
you've gotten wrong more heavily and adds new questions when you have
gotten all current questions more right than wrong.
"""

import dataclasses
from dataclasses import dataclass

from eartraining.app import Quiz
from eartraining.midi import play
from eartraining.music import Scale
from eartraining.music import intervals
from eartraining.music import melody
from eartraining.scheduler import QuestionScheduler


@dataclass(frozen=True)
class IntervalQuestion:

    root: int
    steps: int
    ascending: bool

    def for_steps(self, steps):
        return dataclasses.replace(self, steps=steps)

    @property
    def label(self):
        return intervals[self.steps]

    @property
    def notes(self):
        return [self.root, self.root + (self.steps * (1 if self.ascending else -1))]

    def options(self, in_play):
        return [self.for_steps(s) for s in sorted({x.steps for x in in_play})]

    def play(self, midi_out):
        play(midi_out, melody(self.notes).render(0, 120))

    def hint(self, midi_out):
        play(midi_out, melody(reversed(self.notes)).render(0, 120))

    def after_correct(self, midi_out):
        pass


class IntervalQuiz(Quiz):
    def __init__(self, name, scale):
        super().__init__(name)
        intervals = range(1, 13)
        fourths = [n % 12 for n in range(0, (5 * 12), 5)]
        octaves = [0] + [i * s for i in range(1, 5) for s in (1, -1)]
        roots = [(r + 60) + (o * 12) for o in octaves for r in fourths]
        questions = [IntervalQuestion(r, s, True) for r in roots for s in intervals]
        self.scheduler = QuestionScheduler(questions, 0.5)

    def make_questions(self, _):
        expected = self.scheduler.draw()
        return expected, self.scheduler.options(expected)

    def update(self, choice, question):
        self.scheduler.update(choice, question)


if __name__ == "__main__":

    IntervalQuiz("Intervals", Scale.major).run()
