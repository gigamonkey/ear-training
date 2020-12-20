import random
from collections import defaultdict


class QuestionScheduler:

    """
    From a iterator of questions, keep track of which ones have been
    answered with a moving average of correct and incorrect answers.
    Add new questions to the pool when needed.
    """

    def __init__(self, questions, decay):
        self.questions = iter(questions)
        self.scores = defaultdict(float)
        self.decay = decay
        self.limit = 1 / (1 - decay)

    def draw(self):

        if self.needs_new_question():
            self.add_next_question()

        pop = list(self.scores.keys())
        weights = [(self.limit - self.scores[q]) ** 2 for q in pop]

        print("")
        print(f"{len(self.scores.keys())} current questions.")
        for a, b in sorted(
            zip(weights, pop), key=lambda x: (x[0], x[1].label), reverse=True
        ):
            print(f"{a:.4f} -> {b.label} {b}")

        return random.choices(pop, weights, k=1)[0]

    def options(self, expected):
        return expected.options(self.scores.keys())

    def update(self, got, expected):
        if got == expected:
            self.scores[got] *= self.decay
            self.scores[got] += 1
        else:
            self.scores[got] *= self.decay
            self.scores[got] -= 1
            self.scores[expected] *= self.decay
            self.scores[expected] -= 1

    def needs_new_question(self):
        return all(s > 0.0 for s in self.scores.values())

    def add_next_question(self):
        try:
            q = next(self.questions)
            print(f"Adding {q.label} {q}")
            self.scores[q] = 0.0
            return q
        except StopIteration:
            return None
