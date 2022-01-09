#!/usr/bin/env python

"Quiz of diatonic chords."

from dataclasses import dataclass
from typing import Tuple

from eartraining.grid import Question
from eartraining.grid import QuestionGrid
from eartraining.grid import Quiz
from eartraining.grid import QuizUI
from eartraining.grid import Row
from eartraining.midi import play
from eartraining.music import Scales
from eartraining.music import chord
from eartraining.music import melody
from eartraining.music import rest


@dataclass
class DiatonicChordQuestion(Question):

    label: str
    notes: Tuple[int, ...]

    def play(self, midi_out, root):
        play(midi_out, chord(self.notes).render(root, 120))

    def hint(self, midi_out, root):
        seq = (
            melody(self.notes).rhythm(1 / 8)
            + rest(1 / 8)
            + chord(self.notes).rhythm(1 / 4)
        )
        play(midi_out, seq.render(root, 120))


class DiatonicChordQuiz(Quiz):
    def __init__(self, scale, root):
        self.scale = scale
        self.root = root
        super().__init__()

    def make_grid(self):
        return QuestionGrid(
            [
                self.make_row(["I", "ii", "iii", "IV", "V", "vi", "vii°"], 3),
                self.make_row(
                    ["IΔ7", "ii7", "iii7", "IVΔ7", "V7", "vi7", "viim7♭5"], 4
                ),
            ]
        )

    def make_row(self, labels, notes):
        chords = [self.scale.diatonic_chord(d, notes) for d in self.scale.degrees]
        return Row(
            [DiatonicChordQuestion(label, c) for label, c in zip(labels, chords)]
        )


if __name__ == "__main__":

    QuizUI("GridTest", DiatonicChordQuiz(Scales.major, 60)).run()
