import random
from collections import defaultdict

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
