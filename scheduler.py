import dataclasses
import random
from collections import defaultdict
from dataclasses import dataclass

# There are two ways we can have a pool of questions: First, there are
# multiple base questions, e.g. different degrees of a scale,
# different chord types, etc. Second, for each base question there can
# be many variants of that question. For degrees of a scale the same
# degree can be played at different octaves. For chord types, the same
# type (major triad, for instance) can be played on different notes,
# at different octaves, and in different voicings.
#
# When it is time to draw a new question from the pool there are two
# ways to include variations:
#
# 1. Make concrete questions for different variations which are each
# counted separately. This means that the specific variations that are
# easier will end up getting asked less frequently and the more
# troublesome ones will get asked more often.
#
# 2. Only keep track of platonic ideals of a given question (e.g. can
# you identify a major triad) and then as the questions score gets
# better (i.e. right more) generate more and more complex variations
# (e.g. play in different octaves, revoice). Adding harder variations
# will increase the number of incorrect answers bringing the base
# question into rotation. (Though that does mean that if the
# complexity of the variation is determined by the current score when
# it starts getting asked more it will always be the simpler
# variations. Which doesn't seem like what you want.)
#
# Number 1 seems better but that raises the question of when it is
# time to draw a new question should the new question be related to
# the current questions. For simplicity we can arrange the questions
# in a deterministic order that makes some pedagogic sense.
#
# For instance, for chord types:
#   - different types with the same root in root position
#   - all the types with each of the other possible roots in root position
#   - keep going but different roots in diferent octaves
#   - finally all the same roots across many octaves now with different voicings.
#


# On an incorrect answer we need to mark the item that was the correct
# answer but also the item representing the wrong answer. This makes
# the whole question of variants a bit trickier: given that the
# options presented are in terms of base questions, if we're tracking
# every variant separately, which variont of the wrong answer should
# be docked? E.g. if we are doing chord types and play a G Major triad
# and the user chooses "Minor triad" then we probably want to make the
# G Minor triad more likely to be asked. But what if that question
# hasn't even been added yet?

# Pick a question at random. QuestionVariant object knows how to make
# a specific variant for each of the base questions in the quiz. Each
# of those variants should be possible questions so presumably

# Adding a new base type, e.g. a new esoteric chord type, run through
# all the current questions and extract the other dimensions (root
# note, octave, voicing) and make a new question for each unique
# tuple. So if we have C1 Major in root position and C1 Minor in root
# position and we're adding Diminished as a new base type then we see
# that we need to make C1 Diminished in root

# Adding a new variant (e.g. a root note) we similarly run through all
# the current questions and extract the unique sets of values
# excluding the root note so Minor in root position, Major in root
# position, Diminished in root postion


@dataclass(frozen=True)
class IntervalQuestion:

    root: int
    steps: int
    ascending: bool

    names = [
        "P1",
        "m2",
        "M2",
        "m3",
        "M3",
        "P4",
        "Tritone",
        "P5",
        "m6",
        "M6",
        "m7",
        "M7",
        "P8",
    ]

    def for_steps(self, steps):
        return dataclasses.replace(self, steps=steps)

    @property
    def name(self):
        return IntervalQuestion.names[self.steps]

    def options(self, in_play):
        return [self.for_steps(s) for s in sorted({x.steps for x in in_play})]


class QuestionScheduler:
    def __init__(self, questions, decay):
        self.questions = iter(questions)
        self.scores = defaultdict(float)
        self.decay = decay
        self.limit = 1 / (1 - decay)

    def draw(self):

        if self.needs_new_question():
            self.add_next_question()

        pop = list(self.scores.keys())
        weights = [self.limit - self.scores[q] for q in pop]

        for a, b in zip(pop, weights):
            print(f"{a} -> {b}")

        return random.choices(pop, weights, k=1)[0]

    def options(self, expected):
        return expected.options(self.scores.keys())

    def update(self, got, expected):
        if got == expected:
            self.right(got)
        else:
            self.wrong(got)
            self.wrong(expected)

    def right(self, question):
        "This was the question and the user got it right."
        self.scores[question] = (self.scores[question] * self.decay) + 1

    def wrong(self, question):
        """
        Either this was the question and the user got it wrong or it was
        the wrong choice, in both case we want to reduce the score and
        thus increase the chance that this question will be asked.
        """
        self.scores[question] = (self.scores[question] * self.decay) - 1

    def needs_new_question(self):
        return all((self.limit - s) < 1.0 for s in self.scores.values())

    def add_next_question(self):
        try:
            q = next(self.questions)
            self.scores[q] = 0.0
            return q
        except StopIteration:
            return None


if __name__ == "__main__":

    intervals = range(1, 13)
    fourths = [n % 12 for n in range(0, (5 * 12), 5)]
    octaves = [0] + [i * s for i in range(1, 5) for s in (1, -1)]
    roots = [(r + 60) + (o * 12) for o in octaves for r in fourths]
    questions = [IntervalQuestion(r, s, True) for r in roots for s in intervals]

    s = QuestionScheduler(questions, 0.5)

    # Draw random question. Make equivalent variants of other base questions.
    # Present base questions Get user choice. Update scores.

    while True:
        expected = s.draw()

        options = s.options(expected)

        for i, option in enumerate(options):
            print(f"{i}: {option.name}")

        if n := input(f"{expected.name}>: "):
            got = options[int(n)]
            s.update(got, expected)
        else:
            break
