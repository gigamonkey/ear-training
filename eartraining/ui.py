#!/usr/bin/env python

"""
UI elements.
"""


import pygame
import pygame.freetype
import pygame.midi
import pygame.time

initial_button_color = (127, 127, 255)

wrong_button_color = (64, 64, 255)

status_color = (16 * 10, 16 * 10, 255)


class Button:
    def __init__(self, question, pos, size, is_wrong):
        self.question = question
        self.rect = pygame.Rect(pos, size)
        self.is_wrong = is_wrong

    def render(self, screen, font):
        surface = pygame.Surface(self.rect.size)
        pygame.draw.rect(
            surface,
            initial_button_color if not self.is_wrong else wrong_button_color,
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
        )
        text, text_rect = font.render(self.question.label, (0, 0, 0))

        x = (self.rect.width - text_rect.width) / 2
        y = (self.rect.height - text_rect.height) / 2

        surface.blit(text, (x, y))
        screen.blit(surface, (self.rect.x, self.rect.y))

    def is_hit(self, pos):
        return self.rect.collidepoint(pos)


class Status:
    def __init__(self, quiz, pos, size, font, screen):
        self.quiz = quiz
        self.rect = pygame.Rect(pos, size)
        self.font = font
        self.screen = screen
        self.start_tick = pygame.time.get_ticks()

    def update(self):
        surface = pygame.Surface(self.rect.size)
        pygame.draw.rect(
            surface,
            status_color,
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
        )

        self.draw_clock(surface)
        self.draw_status(surface)

        self.screen.blit(surface, (self.rect.x, self.rect.y))
        pygame.display.update()

    def draw_clock(self, surface):
        text, text_rect = self.font.render(self.time_label(), (0, 0, 0))
        x = self.rect.width - (text_rect.width + 5)
        y = (self.rect.height - text_rect.height) / 2
        surface.blit(text, (x, y))

    def draw_status(self, surface):
        text, text_rect = self.font.render(self.quiz.status_text(), (0, 0, 0))
        x = 5
        y = (self.rect.height - text_rect.height) / 2
        surface.blit(text, (x, y))

    def time_label(self):
        ticks = pygame.time.get_ticks()
        minutes, seconds = divmod((ticks - self.start_tick) // 1000, 60)
        if minutes >= 60:
            hours, minutes = divmod(minutes, 60)
        else:
            hours = 0
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def render_buttons(surface, quiz, rect, font, wrong, gap=5):

    h = ((rect.height + gap) / len(quiz)) - gap

    def make_button(q, i):
        b = Button(
            q, (0, rect.top + (i * (h + gap))), (rect.width, h), q.label in wrong
        )
        b.render(surface, font)
        return b

    return [make_button(q, i) for i, q in enumerate(quiz)]
