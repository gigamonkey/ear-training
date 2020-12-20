import random
from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Tuple


@dataclass
class Dimension:

    value: Any
    children: List["Dimension"]

    decay: float = 0.5
    score: float = 0.0
    enabled: bool = False

    def __post_init__(self):
        self.limit = 1 / (1 - self.decay)

    def fill(self, question):
        self.set_dimension(question)
        return (self,) + self.fill_other_dimensions(question)

    def fill_other_dimensions(self, question):
        if self.children:
            self.maybe_enable_dimension()
            options = [d for d in self.children if d.enabled]
            weights = [(d.limit - d.score) ** 2 for d in options]
            next_dim = random.choices(options, weights, k=1)[0]
            return next_dim.fill(question)
        else:
            return ()

    def set_dimension(self, question):
        "Implement to set particular value on question."

    def get_dimension(self, question):
        "Extract the value for this dimension from the question."

    def maybe_enable_dimension(self):
        "If all the enabled dimensions are positive, enable the next dimension."
        for c in self.children:
            if c.enabled:
                if c.score <= 0.0:
                    # Still have work to do with currently enabled children.
                    break
            else:
                c.enabled = True
                break

    def update_score(self, correct):
        self.score *= self.decay
        self.score += 1 if correct else -1

    def show(self, indent=0):
        if self.enabled:
            print(f"{' ' * 2 * indent}{self.value}: {self.score}")
            if self.children:
                for c in self.children:
                    c.show(indent + 1)


class RootDimension(Dimension):

    value = None
    enabled = True

    def in_play(self):
        return [x.value for x in self.children if x.enabled]

    def fill(self, question):
        dims = self.fill_other_dimensions(question)
        question.dimensions = dims
        return dims

    def update(self, got, expected):
        correct = got == expected
        self.update_score(correct)
        for d in expected.dimensions:
            d.update_score(correct)

        if not correct:
            for c in self.children:
                if c.get_dimension(got) == c.value:
                    c.update_score(False)


class ChordTypeDimension(Dimension):
    def set_dimension(self, question):
        question.chord_type = self.value

    def get_dimension(self, question):
        return question.chord_type


class RootNoteDimension(Dimension):
    def set_dimension(self, question):
        question.root_note = self.value

    def get_dimension(self, question):
        return question.root_note


class OctaveDimension(Dimension):
    def set_dimension(self, question):
        question.octave = self.value

    def get_dimension(self, question):
        return question.octave


class ChordVoicingDimension(Dimension):
    def set_dimension(self, question):
        question.chord_voicing = self.value

    def get_dimension(self, question):
        return question.chord_voicing


@dataclass
class ChordTypeQuestion:

    chord_type: Tuple[int] = None
    root_note: int = None
    octave: int = None
    chord_voicing: Tuple[int] = None


if __name__ == "__main__":

    chord_types = [(0, 4, 7), (0, 3, 7), (0, 3, 6), (0, 4, 8)]
    root_notes = range(12)
    octave_numbers = [0] + [i * s for i in range(1, 5) for s in (1, -1)]
    chord_voicings = [0, 1, 2]

    def chords():
        return [ChordTypeDimension(c, roots()) for c in chord_types]

    def roots():
        return [RootNoteDimension(r, octaves()) for r in root_notes]

    def octaves():
        return [OctaveDimension(o, voicings()) for o in octave_numbers]

    def voicings():
        return [ChordVoicingDimension(v, None) for v in chord_voicings]

    root = RootDimension(None, chords(), enabled=True)

    for i in range(20):
        q = ChordTypeQuestion()
        root.fill(q)
        got = random.choice((q, None))
        print(f"{q} -> {got == q}")
        root.update(got, q)
        root.show()
        print(root.in_play())
        print()
