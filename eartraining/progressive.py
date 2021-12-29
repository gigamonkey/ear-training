#!/usr/bin/env python

import random
from collections import defaultdict

from eartraining.app import Quiz


class FixedQuiz(Quiz):

    "A quiz that just randomly asks a fixed set of questions."

    def __init__(self, templates, arg_generator):
        self.templates = templates
        self.arg_generator = arg_generator
        self.right = 0
        self.asked = 0
        self.first_answer = True

    def status_text(self):
        if self.asked < 2:
            return ""
        else:
            return f"{self.right}/{self.asked - 1} ({round(100 * self.right/(self.asked - 1))}%)"

    def make_choices(self):
        args = next(self.arg_generator)
        self.first_answer = True
        ts = enumerate(self.templates)
        return [t.instantiate(i, *args) for i, t in ts]

    def make_questions(self, choices):
        idx = random.randrange(len(choices))
        self.asked += 1
        # FIXME: align may only apply to chords.
        return choices[idx], [choices[idx].align(c) for c in choices]

    def update(self, choice, question):
        if question.idx == choice.idx:
            if self.first_answer:
                # Only increment scores on the first answer.
                self.right += 1
        self.first_answer = False


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
        return f"To go: {self.to_go()}"

    def make_choices(self):
        args = next(self.arg_generator)
        self.first_answer = True
        return [
            t.instantiate(i, *args)
            for i, t in enumerate(self.templates)
            if i in self.active
        ]

    def make_questions(self, choices):
        # FIXME: align may only apply to chords.
        choice = random.choice(choices)
        return choice, [choice.align(c) for c in choices]

    def to_add(self):
        return self.deactivated.pop() if self.deactivated else 1 + max(self.active)

    def to_go(self):
        return sum(
            self.score_threshold - self.scores[i]
            for i in self.active
            if self.scores[i] < self.score_threshold
        )

    def average_to_go(self):
        return self.to_go() / len(self.active)

    def update(self, choice, question):
        if question.idx == choice.idx:
            if self.first_answer:
                # Only increment scores on the first answer.
                self.scores[question.idx] += 1
        else:
            # But can lose points on any wrong answer.
            self.scores[question.idx] -= 1
            self.scores[choice.idx] -= 1

        scores = "|".join(
            str(self.scores[i]) for i in range(len(self.templates)) if i in self.active
        )

        print(f"scores: {scores}; to go: {self.to_go()} (avg. {self.average_to_go()})")

        if all(self.scores[i] >= self.score_threshold for i in self.active):
            # If all questions are above postive threshold, add the
            # next available question which will either be the most
            # recently deactivated question or the next
            # never-activated question.
            if self.deactivated:
                reactivate = self.deactivated.pop()
                self.active.add(reactivate)
                self.scores = defaultdict(int)
                # self.scores[reactivate] = 0
            else:
                self.active.add(1 + max(self.active))
                self.scores = defaultdict(int)

        elif len(self.active) > 2:
            # If we have more than two active questions we may want to
            # deactivate one to focus on questions that we're having
            # trouble with.

            s, i = max((self.scores[i], i) for i in self.active)

            if any(self.scores[i] <= -self.score_threshold for i in self.active):
                # If any question is below the negative threshold
                # (i.e. we've gotten it wrong too many times)
                # deactivate the highest scoring currently active
                # question unless there are only two questions left.
                # Reset scores so we won't deactivate any more
                # questions until some question gets below the
                # negative threshold again.
                self.deactivated.append(i)
                self.active.remove(i)
                self.scores = defaultdict(int)
                # elif s >= 2 * self.score_threshold and self.to_go() > self.score_threshold:
            elif s > 2 * self.to_go():
                self.deactivated.append(i)
                self.active.remove(i)
                self.scores = defaultdict(int)

        self.first_answer = False
