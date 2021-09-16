#!/usr/bin/env python

"Quiz of intervals."

import dataclasses
from dataclasses import dataclass
from typing import Optional

from eartraining.app import Quiz
from eartraining.dimensions import Dimension
from eartraining.dimensions import RootDimension
from eartraining.midi import play
from eartraining.music import intervals
from eartraining.music import melody


@dataclass
class IntervalQuestion:

    steps: Optional[int] = None
    root_note: Optional[int] = None
    octave: Optional[int] = None
    ascending: bool = True

    def for_steps(self, steps):
        return dataclasses.replace(self, steps=steps)

    @property
    def label(self):
        return intervals[self.steps]

    @property
    def notes(self):
        root = (self.octave * 12) + self.root_note
        return [root, root + (self.steps * (1 if self.ascending else -1))]

    def options(self, in_play):
        return [self.for_steps(s) for s in sorted(in_play)]

    def play(self, midi_out):
        play(midi_out, melody(self.notes).render(0, 120))

    def hint(self, midi_out):
        play(midi_out, melody(reversed(self.notes)).render(0, 120))

    def after_correct(self, midi_out):
        pass


class IntervalQuiz(Quiz):
    def __init__(self, name):
        super().__init__(name)

        octave_numbers = [5] + [5 + (i * s) for i in range(1, 5) for s in (1, -1)]
        fourths = [n % 12 for n in range(0, (5 * 12), 5)]

        def steps():
            return [Dimension("steps", c, roots()) for c in range(1, 13)]

        def roots():
            return [Dimension("root_note", r, ascending()) for r in fourths]

        def ascending():
            return [Dimension("ascending", v, octaves()) for v in (True, False)]

        def octaves():
            return [Dimension("octave", o, None) for o in octave_numbers]

        self.root = RootDimension(None, None, steps(), enabled=True)

    def make_questions(self, _):
        expected = IntervalQuestion()
        self.root.fill(expected)
        return expected, expected.options(self.root.in_play())

    def update(self, choice, question):
        self.root.update(choice, question)
        # print("Updated")
        # self.root.show()
        # print("")


if __name__ == "__main__":

    IntervalQuiz("Intervals").run()
