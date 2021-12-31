#!/usr/bin/env python

"Quiz of chord progressions."


from eartraining.grid import Question
from eartraining.grid import QuestionGrid
from eartraining.grid import Quiz
from eartraining.grid import QuizUI
from eartraining.grid import Row


class DiatonicChordQuestion(Question):
    def __init__(self, q):
        self.label = q

    def play(self, midi_out):
        print(f"Playing {self.label}")


class DiatonicChordQuiz(Quiz):
    def make_grid(self):
        return QuestionGrid(
            [
                Row([DiatonicChordQuestion(q) for q in ["foo", "bar", "baz"]]),
                Row([DiatonicChordQuestion(q) for q in ["biff", "baam", "boom"]]),
            ]
        )


if __name__ == "__main__":

    QuizUI("GridTest", DiatonicChordQuiz()).run()
