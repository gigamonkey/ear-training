#!/usr/bin/env python

import random

import pygame
import pygame.freetype
import pygame.midi

from chords import ChordType
from chords import chord_types
from midi import Line
from midi import Note
from midi import play
from midi import sequence

size = (300, 500)

# Played when we get it right.
chirp = Line([Note(1 / 16, 96 + n) for n in (0, 5, 7, 12, 17, 19, 24)]).note(60, 1, 0)

# Played when we get it wrong.
blat = Line().chord([30, 31, 32, 33, 34], 1 / 8).note(60, 2, 0)

initial_button_color = (127, 127, 255)
wrong_button_color = (64, 64, 255)


class Button:
    def __init__(self, label, pos, size, is_wrong):
        self.label = label
        self.rect = pygame.Rect(pos, size)
        self.is_wrong = is_wrong

    def render(self, screen, font):
        surface = pygame.Surface(self.rect.size)
        pygame.draw.rect(
            surface,
            initial_button_color if not self.is_wrong else wrong_button_color,
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
        )
        text, text_rect = font.render(self.label, (0, 0, 0))

        x = (self.rect.width - text_rect.width) / 2
        y = (self.rect.height - text_rect.height) / 2

        surface.blit(text, (x, y))
        screen.blit(surface, (self.rect.x, self.rect.y))


def is_quit(e):
    return e.type == pygame.QUIT or (
        e.type == pygame.KEYDOWN and (e.key in {pygame.K_ESCAPE, pygame.K_q})
    )


def is_replay(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE


def is_replay_with_arepeggio(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_a


def render_buttons(surface, labels, rect, font, wrong, gap=5):

    h = ((rect.height + gap) / len(labels)) - gap

    buttons = [
        Button(label, (0, i * (h + gap)), (rect.width, h), label in wrong)
        for i, label in enumerate(labels)
    ]
    for b in buttons:
        b.render(surface, font)

    return buttons


def get_answer(buttons, replay, replay_with_arpeggio):
    while True:
        event = pygame.event.wait()
        if is_quit(event):
            return False, None
        elif is_replay(event):
            replay()
        elif is_replay_with_arepeggio(event):
            replay_with_arpeggio()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for b in buttons:
                if b.rect.collidepoint(event.pos):
                    return True, b.label


def run():

    questions = [ChordType(name, pattern) for name, pattern in chord_types.items()]

    pygame.init()
    pygame.midi.init()

    # font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 32)
    font = pygame.freetype.SysFont("helveticaneue", 32)

    pygame.display.set_caption("Chord types")

    screen = pygame.display.set_mode(size)

    background = pygame.Surface(size)
    background.fill(pygame.Color("#dddddd"))

    pygame.time.Clock()

    pygame.event.set_blocked(pygame.MOUSEMOTION)

    port = pygame.midi.get_default_output_id()
    midi_out = pygame.midi.Output(port, 0)

    try:
        midi_out.set_instrument(0)

        running = True

        wrong = set()

        while running:

            if not wrong:
                # New question
                to_play = random.choice(questions)
                quiz = questions
                first_midi = to_play.render_chord(60, 120)
                second_midi = to_play.render_arpeggio_and_chord(60, 120)

                play_question = lambda: play(midi_out, first_midi)

            # Draw the screen with the buttons.
            screen.blit(background, (0, 0))
            buttons = render_buttons(
                screen, [str(p) for p in quiz], pygame.Rect(0, 0, 300, 500), font, wrong
            )
            pygame.display.update()

            # Play the progression
            pygame.event.clear()
            play_question()

            # Wait for events until we get a button click; check the answer.
            running, answer = get_answer(
                buttons, play_question, lambda: play(midi_out, second_midi)
            )
            if running:
                if answer == str(to_play):
                    play(midi_out, sequence(chirp, 120))
                    wrong = set()
                else:
                    play(midi_out, sequence(blat, 120))
                    wrong.add(answer)

    finally:
        pygame.midi.quit()


if __name__ == "__main__":

    run()
