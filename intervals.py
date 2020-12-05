#!/usr/bin/env python

"Quiz of intervals."

import random
from itertools import permutations

from app import Question
from app import Quiz
from midi import play
from music import Scale
from music import intervals
from music import melody


class IntervalQuestion(Question):
    def __init__(self, label, notes):
        self.label = label
        self.notes = notes

    def play(self, midi_out):
        play(midi_out, melody(self.notes).render(60, 120))

    def hint(self, midi_out):
        play(midi_out, melody(reversed(self.notes)).render(60, 120))


class IntervalQuiz(Quiz):
    def __init__(self, name, scale):
        super().__init__(name)
        self.scale = Scale(scale)

    def make_universe(self):
        "Universe is the set of intervals that can be created using notes of the scale."

        def g():
            for a, b in permutations(self.scale.one_octave, 2):
                if a > b:
                    yield a - 12, b
                    yield a, b + 12
                else:
                    yield a, b

            for n in self.scale.one_octave:
                yield a - 12, a
                yield a, a + 12

        return list(g())

    def make_questions(self, universe):
        """
        Not all the choices here are possible answers as we want every
        choice to be rooted at the same note.
        """
        low, high = random.choice(universe)

        ascending = random.choice((True, False))

        choices = [
            IntervalQuestion(
                name, (low, low + size) if ascending else (low + size, low)
            )
            for size, name in enumerate(intervals)
        ]
        return choices[high - low], choices[1:]


if __name__ == "__main__":

    IntervalQuiz("Intervals", Scale.major).run()
