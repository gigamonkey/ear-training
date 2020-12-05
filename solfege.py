#!/usr/bin/env python

"Quiz of scale degrees."


from app import Question
from app import Quiz
from midi import play
from music import Note
from music import major_scale
from music import melody
from music import scale

solfege = ("Do", "Re", "Mi", "Fa", "Sol", "La", "Ti", "Do")


class SolfegeQuestion(Question):
    def __init__(self, label, degree, scale_pattern=major_scale):
        self.label = label
        self.degree = degree
        self.scale = scale(scale_pattern)

    def play(self, midi_out):
        play(midi_out, melody((0, self.scale.note(self.degree))).render(60, 120))

    def after_correct(self, midi_out):
        pitches = [self.scale.note(d) for d in range(self.degree, -1, -1)]
        midi = melody(pitches).rhythm(1 / 8) + Note(0, 1 / 4, 0)
        play(midi_out, midi.render(60, 120))


class SolfegeQuiz(Quiz):
    def make_universe(self):
        return [SolfegeQuestion(name, i) for i, name in enumerate(solfege)]


if __name__ == "__main__":

    SolfegeQuiz("Solfege").run()
