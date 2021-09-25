#!/usr/bin/env python

import random

from eartraining.app import Quiz


class ProgressiveQuiz(Quiz):

    "A quiz that adds questions as we get existing questions right."

    def __init__(self, templates, arg_generator, score_threshold):
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

    def make_choices(self):
        args = next(self.arg_generator)
        self.first_answer = True
        ts = enumerate(self.templates[: self.active])
        return [t.instantiate(i, *args) for i, t in ts]

    def make_questions(self, choices):
        idx = random.randrange(len(choices))
        self.asked[idx] += 1
        # FIXME: align may only apply to chords.
        return choices[idx], [choices[idx].align(c) for c in choices]

    def update(self, choice, question):
        if question.idx == choice.idx:
            if self.first_answer:
                # Only increment scores on the first answer.
                self.scores[question.idx] += 1
        else:
            # But can lose points on any wrong answer.
            self.scores[question.idx] -= 1
            self.scores[choice.idx] -= 1

        if all(s >= self.score_threshold for s in self.scores):
            self.active += 1
            # self.scores.append(0)
            self.scores = [0] * self.active
            self.asked = [0] * self.active

        self.first_answer = False
