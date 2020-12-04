#!/usr/bin/env python

"Quiz of chord types."

from app import Question
from app import Quiz
from chords import chord_types
from midi import play
from music import Rest
from music import chord
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
        return [ChordQuestion(name, pattern) for name, pattern in chord_types.items()]


if __name__ == "__main__":

    ChordQuiz("Chord types").run()
