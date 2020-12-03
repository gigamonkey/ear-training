#!/usr/bin/env python

import random
from itertools import permutations

from app import Quiz
from chords import Progression
from chords import random_voicing
from midi import play


class Question:
    def __init__(self, label, progression):
        self.label = label
        self.progression = progression
        self.midi = self.progression.render(60, random_voicing, 120)

    def play(self, midi_out):
        play(midi_out, self.midi)

    def hint(self, midi_out):
        self.play(midi_out)


class ProgressionQuiz(Quiz):
    def make_universe(self):
        return [Progression((0,) + p + (0,)) for p in permutations(range(1, 7), 2)]

    def make_questions(self, progressions):

        seed = random.choice(progressions)

        def p(x, y):
            return Progression((0, x, y, 0), seed.scale)

        a, b = seed.progression[1:3]
        fake_a, fake_b = random.sample(set(range(1, 7)) - {a, b}, 2)

        ps = [seed, p(fake_a, b), p(a, fake_b), p(fake_a, fake_b)]
        random.shuffle(ps)
        return [Question(p.name(), p) for p in ps]


if __name__ == "__main__":

    ProgressionQuiz("Progressions").run()
