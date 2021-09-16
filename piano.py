#!/usr/bin/env python

"Trivial computer keyboard based piano keyboard."

import pygame
import pygame.midi

from eartraining import keyboard
from eartraining.events import is_quit

if __name__ == "__main__":

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
            elif (note := keyboard.get_note(e)) is not None:
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
