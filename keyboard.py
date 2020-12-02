#!/usr/bin/env python

import sys
import os

import pygame
import pygame.midi


# Keycodes ignoring keybooard layout.

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
]


def run(device_id=None):

    start_note = 60

    key_mapping = make_key_mapping(chromatic_scancodes, start_note)

    pygame.init()
    pygame.midi.init()

    if device_id is None:
        port = pygame.midi.get_default_output_id()
    else:
        port = device_id

    midi_out = pygame.midi.Output(port, 0)
    try:
        midi_out.set_instrument(0)

        on_notes = set()
        while True:
            e = pygame.event.wait()
            if e.type == pygame.QUIT:
                break
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    break

                if e := key_mapping.get(e.scancode):
                    note, velocity = e
                    if note not in on_notes:
                        midi_out.note_on(note, velocity)
                        on_notes.add(note)

            elif e.type == pygame.KEYUP:
                if e := key_mapping.get(e.scancode):
                    note, _ = e
                    if note in on_notes:
                        midi_out.note_off(note, 0)
                        on_notes.remove(note)

    finally:
        del midi_out
        pygame.midi.quit()


def make_key_mapping(scancodes, start_note):
    return {code: (start_note + i, 127) for i, code in enumerate(scancodes)}


if __name__ == "__main__":

    try:
        device_id = int(sys.argv[-1])
    except ValueError:
        device_id = None

    run(device_id)
