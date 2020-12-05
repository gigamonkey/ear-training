#!/usr/bin/env python

"Quiz of scale degrees."


from app import Question
from app import Quiz
from app import silence
from midi import play
from music import Scale
from music import melody

solfege = ("Do", "Re", "Mi", "Fa", "Sol", "La", "Ti", "Do")


class SolfegeQuestion(Question):
    def __init__(self, label, degree, scale=Scale.major):
        self.label = label
        self.degree = degree
        self.scale = Scale(scale)

    def play(self, midi_out):
        play(midi_out, melody((0, self.scale.note(self.degree))).render(60, 120))

    def after_correct(self, midi_out):
        pitches = [self.scale.note(d) for d in range(self.degree, 0, -1)]
        midi = melody(pitches).rhythm(1 / 8) + silence(1 / 4)
        play(midi_out, midi.render(60, 120))


class SolfegeQuiz(Quiz):
    def make_universe(self):
        return [SolfegeQuestion(name, i + 1) for i, name in enumerate(solfege)]


if __name__ == "__main__":

    SolfegeQuiz("Solfege").run()
