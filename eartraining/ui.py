#!/usr/bin/env python

"""
UI elements.
"""

from enum import Enum
from enum import auto

import pygame
import pygame.freetype
import pygame.midi
import pygame.time

from eartraining import keyboard

initial_button_color = (127, 127, 255)

disabled_button_color = (127, 127, 127)

wrong_button_color = (64, 64, 255)

status_color = (16 * 10, 16 * 10, 255)

quit_keys = {pygame.K_ESCAPE, pygame.K_q}


def is_mouse_click_event(e):
    return e.type in {pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP}


def is_mouse_event(e):
    return e.type in {pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION}


def is_key_event(e):
    return e.type in {pygame.KEYDOWN, pygame.KEYUP}


def is_quit(e):
    return e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and (e.key in quit_keys))


def is_replay(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE


def is_replay_with_hint(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_h


def is_establish_key(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_k


class ButtonState(Enum):
    DISABLED = auto()
    ACTIVE = auto()
    WRONG = auto()


class Button:
    def __init__(self, surface, font, pos, size, question, state):
        self.surface = surface
        self.font = font
        self.rect = pygame.Rect(pos, size)
        self.question = question
        self.state = state

    def color(self):
        if self.state == ButtonState.DISABLED:
            return disabled_button_color
        elif self.state == ButtonState.ACTIVE:
            return initial_button_color
        elif self.state == ButtonState.WRONG:
            return wrong_button_color

    def draw(self):
        surface = pygame.Surface(self.rect.size)
        pygame.draw.rect(
            surface,
            self.color(),
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
        )
        text, text_rect = self.font.render(self.question.label, (0, 0, 0))

        x = (self.rect.width - text_rect.width) / 2
        y = (self.rect.height - text_rect.height) / 2

        surface.blit(text, (x, y))
        self.surface.blit(surface, (self.rect.x, self.rect.y))

    def is_hit(self, pos):
        return self.rect.collidepoint(pos)

    def handle_event(self, event):
        if self.state is not ButtonState.DISABLED:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.is_hit(event.pos):
                    # Probably highlight the button
                    pass

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.is_hit(event.pos):
                    # Unhighlight the button and fire a button_press event.
                    pygame.event.post(
                        pygame.event.Event(Buttons.BUTTON_PRESSED, button=self)
                    )


class Buttons:

    BUTTON_PRESSED = pygame.event.custom_type()

    def __init__(self, surface, font, rect, gap):
        self.surface = surface
        self.font = font
        self.rect = rect
        self.gap = gap
        self.buttons = []

    def set_questions(self, possible, active):
        self.possible = possible
        self.active = active

        h = ((self.rect.height + self.gap) / len(self.possible)) - self.gap

        def make_button(q, i):
            return Button(
                self.surface,
                self.font,
                (0, self.rect.top + (i * (h + self.gap))),
                (self.rect.width, h),
                q,
                ButtonState.ACTIVE if q in active else ButtonState.DISABLED,
            )

        self.buttons = [make_button(q, i) for i, q in enumerate(possible)]

    def draw(self):
        if self.buttons:
            ((self.rect.height + self.gap) / len(self.buttons)) - self.gap
            for b in self.buttons:
                b.draw()

    def handle_event(self, event):
        "Dispatch mouseclick events to the appropriate button."
        if is_mouse_click_event(event):
            for b in self.buttons:
                if b.is_hit(event.pos):
                    b.handle_event(event)


class Status:
    def __init__(self, quiz, pos, size, font, surface, clock):
        self.quiz = quiz
        self.rect = pygame.Rect(pos, size)
        self.font = font
        self.surface = surface
        self.clock = clock

    def draw(self):
        surface = pygame.Surface(self.rect.size)
        pygame.draw.rect(
            surface,
            status_color,
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
        )

        self.draw_clock(surface, self.clock.elapsed())
        self.draw_status(surface, self.quiz.status_text())

        self.surface.blit(surface, (self.rect.x, self.rect.y))
        pygame.display.update(self.rect)

    def handle_event(self, event):
        # Gets TICK events.
        self.draw()

    def draw_clock(self, surface, elapsed_ticks):
        text, text_rect = self.font.render(self.time_label(elapsed_ticks), (0, 0, 0))
        x = self.rect.width - (text_rect.width + 5)
        y = (self.rect.height - text_rect.height) / 2
        surface.blit(text, (x, y))

    def draw_status(self, surface, text):
        text, text_rect = self.font.render(text, (0, 0, 0))
        x = 5
        y = (self.rect.height - text_rect.height) / 2
        surface.blit(text, (x, y))

    def time_label(self, elapsed_ticks):
        minutes, seconds = divmod(elapsed_ticks // 1000, 60)
        if minutes >= 60:
            hours, minutes = divmod(minutes, 60)
        else:
            hours = 0
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class ChromaticKeyboard:

    "Abstracted one-octave piano keyboard widget."

    keys = range(12)

    white_keys = [0, 2, 4, 5, 7, 9, 11]

    number_keys = [
        pygame.K_1,
        pygame.K_2,
        pygame.K_3,
        pygame.K_4,
        pygame.K_5,
        pygame.K_6,
        pygame.K_7,
    ]

    def __init__(self, labels, rect, font, gap):
        self.rect = rect
        self.font = font
        self.gap = gap

        max_width = ((rect.width + gap) / len(ChromaticKeyboard.white_keys)) - gap
        max_height = ((rect.height + gap) / 2) - gap

        size = (min(max_width, max_height),) * 2
        self.keys = [
            Key(k, labels[k], self.key_rect(k, size), self.font)
            for k in ChromaticKeyboard.keys
        ]

    @classmethod
    def preferred_size(self, key_size, gap):
        width = (key_size * len(ChromaticKeyboard.white_keys)) + (gap * 6)
        height = (key_size * 2) + gap
        return (width, height)

    def key_rect(self, note, size):
        return pygame.Rect(self.key_pos(note, size), size)

    def key_pos(self, note, size):
        if note in ChromaticKeyboard.white_keys:
            i = ChromaticKeyboard.white_keys.index(note)
            x = self.rect.x + (i * (size[0] + self.gap))
            y = self.rect.y + size[1] + self.gap
            return (x, y)
        else:
            x, y = self.key_pos(note - 1, size)
            return (x + size[0] / 2, y - (size[1] + self.gap))

    def draw(self, parent):
        for k in self.keys:
            k.draw(parent)

    def handle_event(self, e, ui):
        key = None

        if is_mouse_event(e):
            for k in self.keys:
                if k.rect.collidepoint(e.pos):
                    key = k
                    break

        elif (note := keyboard.get_note(e)) is not None:
            key = self.keys[note % 12]

        elif is_key_event(e) and e.key in ChromaticKeyboard.number_keys:
            i = Scale.major[ChromaticKeyboard.number_keys.index(e.key)]
            key = self.keys[i]

        if key is not None:
            if e.type in {pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN}:
                key.lowlight()
                ui.fire_key_played(key)
            elif e.type in {pygame.MOUSEBUTTONUP, pygame.KEYUP}:
                key.unlight()
                ui.fire_key_released(key)


class DiatonicKeyboard:

    "Abstracted one-octave diatonic keyboard widget."

    keys = range(7)

    number_keys = [
        pygame.K_1,
        pygame.K_2,
        pygame.K_3,
        pygame.K_4,
        pygame.K_5,
        pygame.K_6,
        pygame.K_7,
    ]

    def __init__(self, labels, rect, font, gap):
        self.rect = rect
        self.font = font
        self.gap = gap

        max_width = ((rect.width + gap) / len(DiatonicKeyboard.keys)) - gap
        max_height = rect.height

        size = (min(max_width, max_height),) * 2
        self.keys = [
            Key(k, labels[k], self.key_rect(k, size), self.font)
            for k in DiatonicKeyboard.keys
        ]

    @classmethod
    def preferred_size(self, key_size, gap):
        width = (key_size * len(DiatonicKeyboard.keys)) + (gap * 6)
        height = key_size
        return (width, height)

    def key_rect(self, note, size):
        return pygame.Rect(self.key_pos(note, size), size)

    def key_pos(self, note, size):
        x = self.rect.x + (note * (size[0] + self.gap))
        return (x, self.rect.y)

    def draw(self, parent):
        for k in self.keys:
            k.draw(parent)

    def handle_event(self, e, ui):
        key = None

        if is_mouse_event(e):
            for k in self.keys:
                if k.rect.collidepoint(e.pos):
                    key = k
                    break

        elif (note := keyboard.get_diatonic_note(e)) is not None:
            key = self.keys[note % 7]

        elif is_key_event(e) and e.key in DiatonicKeyboard.number_keys:
            key = self.keys[DiatonicKeyboard.number_keys.index(e.key)]

        if key is not None:
            if e.type in {pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN}:
                key.lowlight()
                ui.fire_key_played(key)
            elif e.type in {pygame.MOUSEBUTTONUP, pygame.KEYUP}:
                key.unlight()
                ui.fire_key_released(key)


class Key:
    def __init__(self, note, label, rect, font):
        self.note = note
        self.label = label
        self.rect = rect
        self.font = font
        self.color = (127, 127, 255)

    def draw(self, parent):

        surface = pygame.Surface(self.rect.size)
        pygame.draw.rect(surface, self.color, pygame.Rect((0, 0), self.rect.size))

        text, text_rect = self.font.render(self.label, (0, 0, 0))
        x = (self.rect.size[0] - text_rect.width) / 2
        y = (self.rect.size[1] - text_rect.height) / 2
        surface.blit(text, (x, y))

        parent.blit(surface, self.rect.topleft)

    def unlight(self):
        self.color = (127, 127, 255)

    def highlight(self):
        self.color = (156, 156, 255)

    def lowlight(self):
        self.color = (64, 64, 255)
