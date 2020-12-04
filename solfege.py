#!/usr/bin/env python

"Quiz of scale degrees."

from itertools import islice

from app import Question
from app import Quiz
from chords import major_scale
from chords import notes
from midi import play
from music import Note
from music import melody

solfege = ("Do", "Re", "Mi", "Fa", "Sol", "La", "Ti", "Do")


class SolfegeQuestion(Question):
    def __init__(self, label, degree, scale=major_scale):
        self.label = label
        self.degree = degree
        self.scale = scale

    def play(self, midi_out):
        pitch = next(islice(notes(0, self.scale), self.degree - 1, self.degree))
        play(midi_out, melody((0, pitch)).render(60, 120))

    def after_correct(self, midi_out):
        pitches = list(reversed(list(islice(notes(0, self.scale), self.degree))))
        midi = melody(pitches).rhythm(1 / 8) + Note(0, 1 / 4, 0)
        play(midi_out, midi.render(60, 120))


class SolfegeQuiz(Quiz):
    def make_universe(self):
        return [SolfegeQuestion(name, i + 1) for i, name in enumerate(solfege)]


if __name__ == "__main__":

    SolfegeQuiz("Solfege").run()
