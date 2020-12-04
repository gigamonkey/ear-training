#!/usr/bin/env python

"Quiz of chord progressions."

import random
import sys
from itertools import permutations

from app import Question
from app import Quiz
from chords import major_scale
from chords import random_inversion
from chords import roman_letters
from chords import triad
from midi import play
from music import Sequence
from music import chord


class ProgressionQuestion(Question):
    def __init__(self, progression, scale=major_scale):
        names = roman_letters(scale)
        chords = [triad(0, scale, d) for d in progression]

        self.label = "-".join(names[d] for d in progression)
        self.midi = Sequence([random_voicing(c) for c in chords]).render(60, 120)

    def play(self, midi_out):
        play(midi_out, self.midi)


class ProgressionQuiz(Quiz):
    def __init__(self, name, number):
        super().__init__(name)
        self.number = number

    def make_universe(self):
        return list(permutations(range(1, 7), self.number - 2))

    def make_questions(self, universe):

        seed = random.choice(universe)
        sample = random.sample([m for m in universe if similar(seed, m)], 4)

        questions = [ProgressionQuestion((0, *m, 0)) for m in sample]
        random.shuffle(questions)
        return questions


def similar(p1, p2):
    return sum(x1 == x2 for x1, x2 in zip(p1, p2)) == (len(p1) - 1)


def random_voicing(notes):
    t = random_inversion(notes)
    t.append(random.choice(t) - 12)
    t.append(random.choice(t) + 12)
    if random.choice((True, False)):
        t = [n - 12 for n in t]
    return chord(t)


if __name__ == "__main__":

    num_chords = int(sys.argv[1]) if len(sys.argv) > 1 else 4

    ProgressionQuiz("Progressions", num_chords).run()
