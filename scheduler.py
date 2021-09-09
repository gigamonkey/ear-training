import random
from collections import defaultdict
from dataclasses import dataclass


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
            print(f"{a:.4f} -> {b.label}")

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


@dataclass
class QuestionData:

    score: float = 0.0
    last_asked: int = 0

    def weight(self, s):
        base_weight = s.limit - self.score
        age = s.questions_asked - self.last_asked
        age_adjustment = s.age_weighting ** age
        weight = base_weight * age_adjustment
        return weight

    def stats(self, s):
        base_weight = s.limit - self.score
        age = s.questions_asked - self.last_asked
        age_adjustment = s.age_weighting ** age
        weight = base_weight * age_adjustment
        return f"weight {weight}. score: {self.score}; base_weight: {base_weight}; age: {age}; age_adjustment: {age_adjustment}"

    def ok(self, threshold):
        return self.score > threshold


class SetQuestionScheduler:

    """
    Like QuestionScheduler but adds questions in sets rather than one
    at a time.
    """

    def __init__(self, question_sets, score_decay, age_weighting, correct_required):
        self.question_sets = iter(question_sets)
        self.questions = dict()
        self.score_decay = score_decay
        self.age_weighting = age_weighting
        self.limit = 1 / (1 - score_decay)
        self.threshold = self.limit - (score_decay ** (correct_required - 1))
        self.questions_asked = 0

    def draw(self):

        if self.needs_new_questions():
            self.add_questions()

        qs = list(self.questions.keys())
        weights = [self.questions[q].weight(self) for q in qs]

        print("")
        print(f"{len(qs)} current questions.")
        for a, b in sorted(
            zip(weights, qs), key=lambda x: (x[0], x[1].label), reverse=True
        ):
            qd = self.questions[b]
            print(f"{a:.4f} -> {b.label} {qd.stats(self)}")

        self.questions_asked += 1
        q = random.choices(qs, weights, k=1)[0]
        self.questions[q].last_asked = self.questions_asked
        return q

    def options(self, expected):
        return expected.options(self.questions.keys())

    def update(self, got, expected):
        if got == expected:
            self.questions[got].score *= self.score_decay
            self.questions[got].score += 1
        else:
            self.questions[got].score *= self.score_decay
            self.questions[got].score -= 1
            self.questions[expected].score *= self.score_decay
            self.questions[expected].score -= 1

    def needs_new_questions(self):
        """
        When all the current questions' scores are above our threshold,
        then we add in the next set of questions.
        """
        return all(q.ok(self.threshold) for q in self.questions.values())

    def add_questions(self):
        try:
            qs = next(self.question_sets)
            for q in qs:
                print(f"Adding {q.label} {q}")
                self.questions[q] = QuestionData()
        except StopIteration:
            return None
