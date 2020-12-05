#!/usr/bin/env python

"Quiz of chord progressions."

import random
import sys
from itertools import permutations

from app import Question
from app import Quiz
from midi import play
from music import Sequence
from music import chord
from music import inversion
from music import major_scale
from music import roman
from music import scale


class ProgressionQuestion(Question):
    def __init__(self, progression, scale_pattern=major_scale):
        s = scale(scale_pattern)
        chords = [s.triad(d) for d in progression]
        self.label = "-".join(roman(d, c) for d, c in zip(progression, chords))
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
    "Take a chord in basic form and randomly revoice it."
    t = list(inversion(notes, random.randrange(len(notes))))
    t.append(random.choice(t) - 12)
    t.append(random.choice(t) + 12)
    if random.choice((True, False)):
        t = [n - 12 for n in t]
    return chord(t)


if __name__ == "__main__":

    num_chords = int(sys.argv[1]) if len(sys.argv) > 1 else 4

    ProgressionQuiz("Progressions", num_chords).run()
