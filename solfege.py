#!/usr/bin/env python

"Quiz of scale degrees."

from app import Question
from app import Quiz
from chords import Solfege
from midi import play

solfege = ("Do", "Re", "Mi", "Fa", "Sol", "La", "Ti", "Do")


class SolfegeQuestion(Question):
    def __init__(self, label, degree):
        self.label = label
        self.note = Solfege(label, degree)

    def play(self, midi_out):
        play(midi_out, self.note.render(60, 120))

    def after_correct(self, midi_out):
        play(midi_out, self.note.render_walk_back_to_do(60, 120))


class SolfegeQuiz(Quiz):
    def make_universe(self):
        return [SolfegeQuestion(name, i + 1) for i, name in enumerate(solfege)]


if __name__ == "__main__":

    SolfegeQuiz("Solfege").run()
