#!/usr/bin/env python

"Quiz of chord types."

import dataclasses
from dataclasses import dataclass
from typing import Optional

from app import Quiz
from dimensions import Dimension
from dimensions import RootDimension
from midi import play
from music import chord
from music import chord_types
from music import melody


@dataclass
class ChordQuestion:

    chord_type: Optional[int] = None
    root_note: Optional[int] = None
    octave: Optional[int] = None

    def for_type(self, chord_type):
        return dataclasses.replace(self, chord_type=chord_type)

    @property
    def label(self):
        return chord_types[self.chord_type]

    @property
    def notes(self):
        root = (self.octave * 12) + self.root_note
        return [root + i for i in self.chord_type]

    def options(self, in_play):
        return [self.for_type(s) for s in in_play]

    def play(self, midi_out):
        play(midi_out, chord(self.notes).render(0, 120))

    def hint(self, midi_out):
        play(midi_out, melody(self.notes).render(0, 120))

    def after_correct(self, midi_out):
        pass


class ChordQuiz(Quiz):
    def __init__(self, name):
        super().__init__(name)

        octave_numbers = [5] + [5 + (i * s) for i in range(1, 5) for s in (1, -1)]
        fourths = [n % 12 for n in range(0, (5 * 12), 5)]

        def types():
            # decay = 0.25
            # threshold = sum(0.25 ** i for i in range(4))

            return [Dimension("chord_type", c, roots()) for c in chord_types.keys()]

        def roots():
            return [Dimension("root_note", r, octaves()) for r in fourths]

        def octaves():
            return [Dimension("octave", o, None) for o in octave_numbers]

        self.root = RootDimension(None, None, types(), enabled=True)

    def make_questions(self, _):
        expected = ChordQuestion()
        self.root.fill(expected)
        return expected, expected.options(self.root.in_play())

    def update(self, choice, question):
        self.root.update(choice, question)
        # print("Updated")
        # self.root.show()
        # print("")


if __name__ == "__main__":

    ChordQuiz("Chords").run()
