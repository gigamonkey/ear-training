#!/usr/bin/env python

"Quiz of chord types."

from app import Question
from app import Quiz
from chords import ChordType
from chords import chord_types
from midi import play


class ChordQuestion(Question):
    def __init__(self, label, pattern):
        self.label = label
        self.chord = ChordType(label, pattern)

    def play(self, midi_out):
        play(midi_out, self.chord.render_chord(60, 120))

    def hint(self, midi_out):
        play(midi_out, self.chord.render_arpeggio_and_chord(60, 120))


class ChordQuiz(Quiz):
    def make_universe(self):
        return [ChordQuestion(name, pattern) for name, pattern in chord_types.items()]


if __name__ == "__main__":

    ChordQuiz("Chord types").run()
