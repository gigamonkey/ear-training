import random
from dataclasses import dataclass
from itertools import permutations, product

import pygame
import pygame.freetype

from chords import Progression

size = (300, 500)

pygame.init()

pygame.display.set_caption("Quick Start")

window_surface = pygame.display.set_mode(size)

background = pygame.Surface(size)
background.fill(pygame.Color("#dddddd"))

clock = pygame.time.Clock()

font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 32)


class Button:
    def __init__(self, label, pos, size):
        self.label = label
        self.rect = pygame.Rect(pos, size)

    def render(self, screen):
        surface = pygame.Surface(self.rect.size)
        pygame.draw.rect(
            surface,
            (127, 127, 255),
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
        )
        text, text_rect = font.render(self.label, (0, 0, 0))

        x = (self.rect.width - text_rect.width) / 2
        y = (self.rect.height - text_rect.height) / 2

        surface.blit(text, (x, y))
        screen.blit(surface, (self.rect.x, self.rect.y))

def is_quit(e):
    return e.type == pygame.QUIT or (
        e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE
    )


def render_buttons(surface, labels, rect, gap=5):

    h = ((rect.height + gap) / len(labels)) - gap

    buttons = [
        Button(label, (0, i * (h + gap)), (rect.width, h))
        for i, label in enumerate(labels)
    ]
    for b in buttons:
        b.render(surface)

    return buttons


def four_chord_progressions():
    return [
        Progression((0,) + p + (0,)) for p in permutations(range(1, 7), 2)
    ]

all_progressions = four_chord_progressions()

quiz = random.sample(four_chord_progressions(), 4)


pygame.event.set_blocked(pygame.MOUSEMOTION)

running = True

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if is_quit(event):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for b in buttons:
                if b.rect.collidepoint(event.pos):
                    print(b.label)

    window_surface.blit(background, (0, 0))

    buttons = render_buttons(
        window_surface,
        [str(p) for p in quiz],
        pygame.Rect(0, 0, 300, 500),
    )

    pygame.display.update()
