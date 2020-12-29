#!/usr/bin/env python

"""
Generate all scales following a few rules:

  - Only steps of 1, 2, or 3 semi-tones are allowed.

  - No consecutive half-steps.

  - No minor thirds after a whole step.

  - Only a half step after a minor third.

Or to put it another way, every *two* steps must be either a minor or
major third apart.
"""

from functools import reduce

steps = (1, 2, 3)

can_follow = {
    1: (2, 3),
    2: (1, 2),
    3: (1,),
}


def scales():
    def patterns(so_far):
        next = can_follow[so_far[-1]] if so_far else (1, 2, 3)

        for s in next:
            total = sum(so_far) + s
            if total == 12 and so_far[0] in can_follow[s]:
                yield so_far
            elif total < 12:
                yield from patterns(so_far + [s])

    for p in patterns([]):
        yield reduce(lambda notes, step: notes + (notes[-1] + step,), p, (0,))


for s in scales():

    print(" ".join(f"{x:2}" for x in s))
