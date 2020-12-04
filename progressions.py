#!/usr/bin/env python

"Quiz of chord progressions."

import random
import sys
from itertools import permutations

from app import Question
from app import Quiz
from chords import major_scale
from chords import random_voicing
from chords import roman_letters
from midi import play
from music import Sequence
from music import chord


class Progression:

    """
    A slightly abstracted chord progression, expressed in terms of
    degrees of a given scale. Chords are built out of the notes of the
    scale.
    """

    def __init__(self, progression, scale=major_scale):
        self.progression = progression
        self.scale = scale
        names = roman_letters(scale)
        self.name = "-".join(names[d] for d in self.progression)

    def render(self, root, voicing, bpm):
        midi = Sequence([chord(voicing(0, self.scale, d)) for d in self.progression])
        return midi.render(root, bpm)


class ProgressionQuestion(Question):
    def __init__(self, progression):
        self.label = progression.name
        self.progression = progression
        self.midi = self.progression.render(60, random_voicing, 120)

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

        questions = [ProgressionQuestion(make_progression(m)) for m in sample]
        random.shuffle(questions)
        return questions


def make_progression(middle):
    return Progression((0, *middle, 0))


def similar(p1, p2):
    return sum(x1 == x2 for x1, x2 in zip(p1, p2)) == (len(p1) - 1)


if __name__ == "__main__":

    num_chords = int(sys.argv[1]) if len(sys.argv) > 1 else 4

    ProgressionQuiz("Progressions", num_chords).run()
