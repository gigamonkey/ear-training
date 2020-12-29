import random
from dataclasses import dataclass
from dataclasses import replace
from typing import Any
from typing import List
from typing import Tuple


@dataclass
class Dimension:

    field: str
    value: Any
    children: List["Dimension"]

    decay: float = 0.5
    score: float = 0.0
    threshold: float = 0.5
    enabled: bool = False

    def __post_init__(self):
        self.limit = 1 / (1 - self.decay)

    def fill(self, question):
        self.set_dimension(question)
        return (self,) + self.fill_other_dimensions(question)

    def fill_other_dimensions(self, question):
        if self.children:
            self.maybe_enable_variant()
            options = [d for d in self.children if d.enabled]
            weights = [(d.limit - d.score) ** 2 for d in options]
            next_dim = random.choices(options, weights, k=1)[0]
            return next_dim.fill(question)
        else:
            return ()

    def set_dimension(self, question):
        "Set the value of our dimension on the question."
        setattr(question, self.field, self.value)

    def get_dimension(self, question):
        "Extract the value for this dimension from the question."
        getattr(question, self.field)

    def maybe_enable_variant(self):
        "If all the enabled variants of this dimension are positive, enable the next variant."
        for c in self.children:
            print(f"Checking {c.field} {c.value}")
            if c.enabled:
                print(
                    f"{c.field} {c.value}: {c.score} {'needs work' if c.score <= c.threshold else 'ok'}"
                )
                if c.score <= c.threshold:
                    print("Breaking")
                    break
            else:
                print(f"Enabling {c.field} {c.value}")
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
        return [Dimension("chord_type", c, roots()) for c in chord_types]

    def roots():
        return [Dimension("root_note", r, octaves()) for r in root_notes]

    def octaves():
        return [Dimension("octave", o, voicings()) for o in octave_numbers]

    def voicings():
        return [Dimension("chord_voicing", v, None) for v in chord_voicings]

    root = RootDimension(None, None, chords(), enabled=True)

    for i in range(20):
        q = ChordTypeQuestion()
        root.fill(q)
        got = replace(q, chord_type=random.choice(chord_types))
        print(f"{q} -> {got == q}")
        root.update(got, q)
        root.show()
        print(root.in_play())
        print()
