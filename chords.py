#!/usr/bin/env python

"Quiz of chord types."

from app import Question
from app import Quiz
from midi import Rest
from midi import play
from music import chord
from music import chord_types
from music import melody


class ChordQuestion(Question):
    def __init__(self, label, pattern):
        self.label = label
        self.pattern = pattern

    def play(self, midi_out):
        play(midi_out, chord(self.pattern).render(60, 120))

    def hint(self, midi_out):
        midi = melody(self.pattern).rhythm(1 / 8) + Rest(1 / 8) + chord(self.pattern)
        play(midi_out, midi.render(60, 120))


class ChordQuiz(Quiz):
    def make_universe(self):
        return [ChordQuestion(name, pattern) for pattern, name in chord_types.items()]


if __name__ == "__main__":

    ChordQuiz("Chord types").run()
