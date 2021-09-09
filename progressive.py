import random
from dataclasses import dataclass
from typing import Tuple

from app import Quiz
from midi import play
from music import chord
from music import chord_types
from music import melody


@dataclass
class UpDown:
    "Simple score keeper that goes up on correct answers and down on incorrect."

    value: int = 0

    def update(self, correct: bool):
        self.value += 1 if correct else -1

    def reset(self):
        self.value = 0


@dataclass
class ExponentialMovingAverage:
    "Score keeper that maintains an exponential moving average."

    decay: float
    value: float = 0

    def update(self, correct: bool):
        self.value *= self.decay
        self.value += 1 if correct else -1


class ProgressiveQuiz(Quiz):

    # List of question templates for all possible questions (e.g.
    # Major, Minor, Diminished, Augmented, Dominant, Maj7, Min7, etc.)

    # Method to render templates into actual questions. (E.g. template
    # is chord, rendered by providing a root.)

    # Maintain list of currently applicable templates.

    # Randomly generate instantiation values (root or whatever).

    # Randomly pick one of the currently applicable templates: that's the question.

    # Play the question and get answer.

    # On correct, update score and move on.
    # On incorrect, update score and (possibly) play choice, and wait for another answer.

    # (As question templates are added, the score threshold to add
    # another should probably go up or we should only count the
    # answers on the newest question.

    # If score is high enough (~ 10), add a new template to the applicable set.

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
        return choices[idx], choices

    def update(self, choice, question):
        correct_idx = self.index_of(question)
        choice_idx = self.index_of(choice)

        print(f"Stats: {self.asked}")

        if correct_idx == choice_idx:
            if self.first_answer:
                # Only increment scores on the first answer.
                self.scores[correct_idx] += 1
                print(f"Increased score at {correct_idx}: {self.scores}")
        else:
            # But can lose points on any wrong answer.
            self.scores[correct_idx] -= 1
            self.scores[choice_idx] -= 1
            print(f"Decreased scores at {correct_idx} and {choice_idx}: {self.scores}")

        if all(s >= self.score_threshold for s in self.scores):
            print(f"Adding question.")
            self.active += 1
            self.scores.append(0)
            self.asked = [0] * self.active
            # self.scores = [0] * self.active

        self.first_answer = False

    def index_of(self, q):
        for i, t in enumerate(self.templates):
            if t.notes == q.notes:
                return i
        raise Exception(f"Can't find {q}")

    def is_newest(self, question):
        "Is the question asked the most recently added question."
        print(
            f"Checking newest. Question: {question.notes}; latest: {self.templates[self.active - 1]}"
        )
        return question.notes == self.templates[self.active - 1].notes


@dataclass
class ChordTemplate:
    "To be instantiated with a root note."

    notes: Tuple[int, ...]

    def instantiate(self, root):
        return ChordQuestion(self.notes, root)


@dataclass
class ChordQuestion:

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


def root_generator():
    while True:
        yield [random.randint(60 - 12, 60 + 12)]


if __name__ == "__main__":

    templates = [ChordTemplate(c) for c in chord_types.keys()]

    ProgressiveQuiz("Chords", templates, root_generator(), 3).run()
