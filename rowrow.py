#!/usr/bin/env python

"For no particular reason an implementation of Row Row Row your boat as a round."


import pygame
import pygame.midi

from eartraining.midi import Rest
from eartraining.midi import play
from eartraining.music import dotted
from eartraining.music import melody
from eartraining.music import triplet


def make_melody():
    p1 = melody((0, 0, 0, 2, 4, 4, 2, 4, 5, 7)).rhythm(
        (
            1 / 4,
            1 / 4,
            dotted(1 / 8),
            1 / 16,
            1 / 4,
            dotted(1 / 8),
            1 / 16,
            dotted(1 / 8),
            1 / 16,
            1 / 2,
        )
    )
    t = melody((12, 12, 12)).rhythm(triplet(1 / 8))
    p2 = t + t.down(5) + t.down(8) + t.down(12)
    p3 = melody((7, 5, 4, 2)).rhythm((dotted(1 / 8), 1 / 16)) + melody((0,)).rhythm(
        1 / 2
    )

    return p1 + p2 + p3


def run():

    m = make_melody()

    round = (
        m.transpose(12)
        | (Rest(1) + m)
        | (Rest(2) + m.transpose(-12))
        | (Rest(3) + m.transpose(-24))
    )

    pygame.init()
    pygame.midi.init()

    port = pygame.midi.get_default_output_id()

    midi_out = pygame.midi.Output(port, 0)

    try:
        midi_out.set_instrument(0)
        play(midi_out, round.render(60, 120))
    finally:
        pygame.midi.quit()


if __name__ == "__main__":

    run()
