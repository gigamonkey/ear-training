#!/usr/bin/env python

"Quiz of chord types."

from app import Question
from app import Quiz
from midi import Rest
from midi import play
from music import chord
from music import melody

chord_types = {
    "Major": (0, 4, 7),
    "Minor": (0, 3, 7),
    "Diminished": (0, 3, 6),
    "Augmented": (0, 4, 8),
    "Major 7": (0, 4, 7, 11),
    "Minor 7": (0, 3, 7, 10),
    "Dominant 7": (0, 4, 7, 10),
    "Minor 7♭5": (0, 3, 6, 10),
    "Diminished 7": (0, 3, 6, 9),
}


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
