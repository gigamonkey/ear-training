#!/usr/bin/env python

import random

from collections import defaultdict

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


class PlusMinusProgressiveQuiz(Quiz):

    """
    A quiz that adds questions as we get existing questions right and
    takes out the ones that we've gotten right too many times.
    """

    def __init__(self, templates, arg_generator, score_threshold):
        self.templates = templates
        self.arg_generator = arg_generator
        self.score_threshold = score_threshold
        self.active = {0, 1}  # hardwire for now
        self.scores = defaultdict(int)
        self.deactivated = []
        self.first_answer = True

    def status_text(self):
        return f"Status: {sum(self.scores[x] for x in self.active)}"

    def make_choices(self):
        args = next(self.arg_generator)
        self.first_answer = True
        return [t.instantiate(i, *args) for i, t in enumerate(self.templates) if i in self.active]

    def make_questions(self, choices):
        # FIXME: align may only apply to chords.
        choice = random.choice(choices)
        return choice, [choice.align(c) for c in choices]

    def to_add(self):
        return self.deactivated.pop() if self.deactivated else 1 + max(self.active)

    def update(self, choice, question):
        if question.idx == choice.idx:
            if self.first_answer:
                # Only increment scores on the first answer.
                self.scores[question.idx] += 1
        else:
            # But can lose points on any wrong answer.
            self.scores[question.idx] -= 1
            self.scores[choice.idx] -= 1

        print(self.scores)

        if all(self.scores[i] >= self.score_threshold for i in self.active):
            # If all questions are above postive threshold, add the next
            # available question which will either be the deactivated
            # question with the worst score or the next never-activated
            # question.
            self.active.add(self.to_add())
            self.scores = defaultdict(int)
        elif any(self.scores[i] <= -self.score_threshold for i in self.active):
            # If any question is below the negative threshold (i.e. we've
            # gotten it wrong too many times) deactivate the highest
            # scoring currently active question unless there are only two
            # questions left. Reset scores so we won't deactivate any more
            # questions until some question gets below the negative
            # threshold again.
            if len(self.active) > 2:
                _, i = max((self.scores[i], i) for i in self.active)
                self.deactivated.append(i)
                self.active.remove(i)
                self.scores = defaultdict(int)

        self.first_answer = False
