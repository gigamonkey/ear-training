#!/usr/bin/env python

"Mapping from keyboard scancodes to chromatic and diatonic notes."

import pygame

from music import Scale

#
# Keycodes ignoring keybooard layout (Qwerty vs Dvorak). No doubt this
# will break on certain keyboards. Goal is to make a piano like
# keyboard like in Ableton. On Qwerty it looks like this:
#
#  -------------------------------------------------------
#    | | # | # | | | # | # | # | | | # | # | | | # | # |
#    | | # | # | | | # | # | # | | | # | # | | | # | # |
#    | | W | E | | | T | Y | U | | | O | P | | | ] | \ |
#    | | # | # | | | # | # | # | | | # | # | | | # | # |
#    | | # | # | | | # | # | # | | | # | # | | | # | # |
#    | +---+---+ | +---+---+---+ | +---+---+ | +---+---+
#    |   |   |   |   |   |   |   |   |   |   |   |   |
#    |   |   |   |   |   |   |   |   |   |   |   | r |
#    | A | S | D | F | G | H | J | K | L | ; | ' | e |
#    |   |   |   |   |   |   |   |   |   |   |   | t |
#    |   |   |   |   |   |   |   |   |   |   |   |   |
#    +---+---+---+---+---+---+---+---+---+---+---+---+
#

chromatic_scancodes = [
    4,
    26,
    22,
    8,
    7,
    9,
    23,
    10,
    28,
    11,
    24,
    13,
    14,
    18,
    15,
    19,
    51,
    52,
    48,
    40,
    49,
]

diatonic_scancodes = [
    sc for i, sc in enumerate(chromatic_scancodes) if i % 12 in Scale.major
]

chomatic_key_mapping = {code: i for i, code in enumerate(chromatic_scancodes)}

diatonic_key_mapping = {code: i for i, code in enumerate(diatonic_scancodes)}


def get_note(e):
    if e.type in {pygame.KEYDOWN, pygame.KEYUP}:
        return chomatic_key_mapping.get(e.scancode)


def get_diatonic_note(e):
    if e.type in {pygame.KEYDOWN, pygame.KEYUP}:
        return diatonic_key_mapping.get(e.scancode)
