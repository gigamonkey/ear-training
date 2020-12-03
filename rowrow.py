from midi import *
import pygame
import pygame.midi

if __name__ == "__main__":

    et = triplet(0.5)

    row_row = Line(
        [
            Note(1, 60),
            Note(1, 60),
            Note(0.75, 60),
            Note(0.25, 62),
            Note(1, 64),
            Note(0.75, 64),
            Note(0.25, 62),
            Note(0.75, 64),
            Note(0.25, 65),
            Note(2, 67),
            Note(et, 72),
            Note(et, 72),
            Note(et, 72),
            Note(et, 67),
            Note(et, 67),
            Note(et, 67),
            Note(et, 64),
            Note(et, 64),
            Note(et, 64),
            Note(et, 60),
            Note(et, 60),
            Note(et, 60),
            Note(0.75, 67),
            Note(0.25, 65),
            Note(0.75, 64),
            Note(0.25, 62),
            Note(2, 60),
        ]
    )

    row_row_round = [
        row_row.transpose(12),
        Line().rest(4) + row_row,
        Line().rest(8) + row_row.transpose(-12),
        Line().rest(12) + row_row.transpose(-24),
    ]

    pygame.init()
    pygame.midi.init()

    port = pygame.midi.get_default_output_id()

    midi_out = pygame.midi.Output(port, 0)

    try:
        midi_out.set_instrument(0)
        play(midi_out, parallel(row_row_round, 120))

    finally:
        del midi_out
        pygame.midi.quit()
