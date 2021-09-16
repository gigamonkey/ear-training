#!/usr/bin/env python

import random
from dataclasses import dataclass

from eartraining.app import Question
from eartraining.midi import play
from eartraining.music import intervals
from eartraining.music import melody
from eartraining.progressive import ProgressiveQuiz


@dataclass
class IntervalTemplate:

    distance: int

    def instantiate(self, idx, root, ascending):
        return IntervalQuestion(idx, self.distance, root, ascending)


@dataclass
class IntervalQuestion(Question):

    idx: int
    distance: int
    root: int
    ascending: bool

    @property
    def label(self):
        return intervals[self.distance]

    def play(self, midi_out):
        second_note = self.distance if self.ascending else -self.distance
        play(midi_out, melody((0, second_note)).render(self.root, 120))

    def hint(self, midi_out):
        second_note = -self.distance if self.ascending else self.distance
        play(midi_out, melody((0, second_note)).render(self.root, 120))

    def align(self, other):
        return other


def arg_generator():
    while True:
        yield (random.randint(60 - 12, 60 + 12), random.choice((True, False)))


if __name__ == "__main__":

    templates = [IntervalTemplate(d) for d in range(1, 13)]

    ProgressiveQuiz("Intervals", templates, arg_generator(), 3).run()
