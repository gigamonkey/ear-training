#!/usr/bin/env python

"Trivial computer keyboard based piano keyboard."

import pygame
import pygame.midi

from app import is_quit

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


key_mapping = {code: i for i, code in enumerate(chromatic_scancodes)}


def get_note(e):
    if e.type in {pygame.KEYDOWN, pygame.KEYUP}:
        return key_mapping.get(e.scancode)


def main():

    start_note = 60

    pygame.init()
    pygame.midi.init()

    port = pygame.midi.get_default_output_id()
    midi_out = pygame.midi.Output(port, 0)

    try:
        midi_out.set_instrument(0)

        on_notes = set()

        while True:
            e = pygame.event.wait()

            if is_quit(e):
                break
            elif (note := get_note(e)) is not None:
                note += start_note
                if e.type == pygame.KEYDOWN:
                    if note not in on_notes:
                        print(note)
                        midi_out.note_on(note, 127)
                        on_notes.add(note)
                    else:
                        print(e.scancode)
                elif e.type == pygame.KEYUP:
                    if note in on_notes:
                        midi_out.note_off(note, 0)
                        on_notes.remove(note)

    finally:
        pygame.midi.quit()


if __name__ == "__main__":

    main()
