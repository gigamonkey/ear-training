#!/usr/bin/env python

import random
from dataclasses import dataclass
from dataclasses import replace
from typing import Tuple

from app import Question
from app import Quiz
from midi import play
from music import chord
from music import chord_types
from music import melody

class ProgressiveQuiz(Quiz):

    "A quiz that adds questions as we get existing questions right."

    def __init__(self, name, templates, arg_generator, score_threshold):
        super().__init__(name)
        self.templates = templates
        self.arg_generator = arg_generator
        self.score_threshold = score_threshold
        self.active = 2  # hardwire for now
        self.scores = [0] * self.active
        self.first_answer = True
        self.asked = [0] * self.active

    def status_text(self):
        to_go = sum(
            self.score_threshold - s for s in self.scores if s < self.score_threshold
        )
        return f"At least {to_go} to get to next."

    def make_choices(self, universe):
        "Ignore the universe."
        args = next(self.arg_generator)
        self.first_answer = True
        return [t.instantiate(*args) for t in self.templates[: self.active]]

    def make_questions(self, choices):
        idx = random.randrange(len(choices))
        self.asked[idx] += 1
        return choices[idx], [choices[idx].align(c) for c in choices]

    def update(self, choice, question):
        correct_idx = self.index_of(question)
        choice_idx = self.index_of(choice)

        if correct_idx == choice_idx:
            if self.first_answer:
                # Only increment scores on the first answer.
                self.scores[correct_idx] += 1
        else:
            # But can lose points on any wrong answer.
            self.scores[correct_idx] -= 1
            self.scores[choice_idx] -= 1

        if all(s >= self.score_threshold for s in self.scores):
            self.active += 1
            # self.scores.append(0)
            self.scores = [0] * self.active
            self.asked = [0] * self.active

        self.first_answer = False

    def index_of(self, q):
        for i, t in enumerate(self.templates):
            if t.notes == q.notes:
                return i
        raise Exception(f"Can't find {q}")


@dataclass
class ChordTemplate:
    "To be instantiated with a root note."

    notes: Tuple[int, ...]

    def instantiate(self, root):
        return ChordQuestion(self.notes, root)


@dataclass
class ChordQuestion(Question):

    notes: Tuple[int]
    root: int

    @property
    def label(self):
        return chord_types[self.notes]

    def play(self, midi_out):
        play(midi_out, chord(self.notes).render(self.root, 120))

    def hint(self, midi_out):
        play(midi_out, melody(self.notes).render(self.root, 120))

    def after_correct(self, midi_out):
        pass

    def align(self, other):
        # Find the root for the other chord such that common
        # structures line up. E.g. if self is a major triad (0, 4, 7)
        # and other is a minor 7th (0, 3, 7, 10) we want the root of
        # the other to be three semi-tones below the root of self so
        # that the notes of its top triad lines up with the notes of
        # our triad.
        #
        # Conversely, if self is the m7 and other is the major triad,
        # we want to shift the root of other up three semitones to
        # line up the notes.

        self_len = len(self.notes)
        other_len = len(other.notes)

        if self_len < other_len:
            # print("other longer")
            # Shift other down and see if we can line it up with self.
            for i in range((other_len - self_len) + 1):
                other_shifted = tuple(n - other.notes[i] for n in other.notes)
                # print(f"other_shifted: {other_shifted}")
                if other_shifted[i : i + self_len] == self.notes:
                    return replace(other, root=self.root - other.notes[i])
        elif self_len > other_len:
            # print("other shorter")
            # Shift other up
            for i in range((self_len - other_len) + 1):
                other_shifted = tuple(n + self.notes[i] for n in other.notes)
                # print(f"other_shifted: {other_shifted}")
                if other_shifted == self.notes[i : i + other_len]:
                    return replace(other, root=self.root + self.notes[i])

        # Same length or couldn't find alignment
        return other


def root_generator():
    while True:
        yield [random.randint(60 - 12, 60 + 12)]


if __name__ == "__main__":

    templates = [ChordTemplate(c) for c in chord_types.keys()]

    ProgressiveQuiz("Chords", templates, root_generator(), 3).run()
