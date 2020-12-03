#!/usr/bin/env python

import random
from itertools import permutations
from itertools import product

import pygame
import pygame.freetype
import pygame.midi

from chords import Progression
from chords import random_voicing
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


def render_buttons(surface, labels, rect, font, wrong, gap=5):

    h = ((rect.height + gap) / len(labels)) - gap

    buttons = [
        Button(label, (0, i * (h + gap)), (rect.width, h), label in wrong)
        for i, label in enumerate(labels)
    ]
    for b in buttons:
        b.render(surface, font)

    return buttons


def four_chord_progressions():
    return [Progression((0,) + p + (0,)) for p in permutations(range(1, 7), 2)]


def get_answer(buttons, replay):
    while True:
        event = pygame.event.wait()
        if is_quit(event):
            return False, None
        elif is_replay(event):
            replay()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for b in buttons:
                if b.rect.collidepoint(event.pos):
                    return True, b.label


def choices(to_play):
    a, b = to_play.progression[1:3]
    fake_a, fake_b = random.sample(set(range(1, 7)) - {a, b}, 2)
    ps = [
        Progression((0, a, b, 0), to_play.scale),
        Progression((0, fake_a, b, 0), to_play.scale),
        Progression((0, a, fake_b, 0), to_play.scale),
        Progression((0, fake_a, fake_b, 0), to_play.scale),
    ]
    random.shuffle(ps)
    return ps


def run():

    progressions = four_chord_progressions()

    pygame.init()
    pygame.midi.init()

    font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 32)

    pygame.display.set_caption("Progressions")

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
                to_play = random.choice(progressions)
                quiz = choices(to_play)
                midi = to_play.render(60, random_voicing, 120)

                def play_progression():
                    play(midi_out, midi)

            # Draw the screen with the buttons.
            screen.blit(background, (0, 0))
            buttons = render_buttons(
                screen, [str(p) for p in quiz], pygame.Rect(0, 0, 300, 500), font, wrong
            )
            pygame.display.update()

            # Play the progression
            pygame.event.clear()
            play_progression()

            # Wait for events until we get a button click; check the answer.
            running, answer = get_answer(buttons, play_progression)

            if running:
                if answer == to_play.name():
                    play(midi_out, sequence(chirp, 120))
                    wrong = set()
                else:
                    play(midi_out, sequence(blat, 120))
                    wrong.add(answer)

    finally:
        del midi_out
        pygame.midi.quit()


if __name__ == "__main__":

    run()
