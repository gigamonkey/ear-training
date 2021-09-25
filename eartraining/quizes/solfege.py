#!/usr/bin/env python

"Quiz of scale degrees."


from eartraining.app import Question
from eartraining.app import Quiz
from eartraining.app import QuizUI
from eartraining.midi import play
from eartraining.music import Scale
from eartraining.music import melody
from eartraining.music import silence

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
    def __init__(self):
        self.choices = [SolfegeQuestion(name, i + 1) for i, name in enumerate(solfege)]

    def make_choices(self):
        return self.choices


if __name__ == "__main__":

    QuizUI("Solfege", SolfegeQuiz()).run()
