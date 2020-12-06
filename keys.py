#!/usr/bin/env python

import pygame
import pygame.freetype

from app import is_quit


class SimpleKeyboard:

    "Abstracted one-octave piano keyboard widget."

    keys = range(12)

    white_keys = [0, 2, 4, 5, 7, 9, 11]

    def __init__(self, rect, font, gap):
        self.rect = rect
        self.font = font
        self.gap = gap

        self.pressed = set()

        max_width = ((rect.width + gap) / len(SimpleKeyboard.white_keys)) - gap
        max_height = ((rect.height + gap) / 2) - gap

        size = (min(max_width, max_height),) * 2
        self.keys = [
            Key(k, str(k), self.key_rect(k, size), self.font)
            for k in SimpleKeyboard.keys
        ]

    def key_rect(self, note, size):
        return pygame.Rect(self.key_pos(note, size), size)

    def key_pos(self, note, size):
        if note in SimpleKeyboard.white_keys:
            i = SimpleKeyboard.white_keys.index(note)
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
        for k in self.keys:
            if k.rect.collidepoint(e.pos):
                k.handle_event(e, ui)
                break


class Key:
    def __init__(self, note, label, rect, font):
        self.note = note
        self.label = label
        self.rect = rect
        self.font = font
        self.pressed = False

    def draw(self, parent):
        color = (127, 127, 255) if not self.pressed else (64, 64, 255)

        surface = pygame.Surface(self.rect.size)
        pygame.draw.rect(surface, color, pygame.Rect((0, 0), self.rect.size))

        text, text_rect = self.font.render(self.label, (0, 0, 0))
        x = (self.rect.size[0] - text_rect.width) / 2
        y = (self.rect.size[1] - text_rect.height) / 2
        surface.blit(text, (x, y))

        parent.blit(surface, self.rect.topleft)

    def handle_event(self, e, ui):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.pressed = True
            ui.fire_key_played(self)
        elif e.type == pygame.MOUSEBUTTONUP:
            self.pressed = False
            ui.fire_key_released(self)


class UI:

    KEY_PLAYED = pygame.USEREVENT
    KEY_RELEASED = KEY_PLAYED + 1

    def __init__(self, name, box_size, gap, padding):
        pygame.init()
        pygame.display.set_caption(name)

        keyboard_width = (box_size * len(SimpleKeyboard.white_keys)) + (gap * 6)
        keyboard_height = (box_size * 2) + gap
        self.size = ((padding * 2) + keyboard_width, (padding * 2) + keyboard_height)

        kb_pos = (padding, padding)
        kb_size = (keyboard_width, keyboard_height)
        font = pygame.freetype.SysFont("helveticaneue", 32)

        self.running = False
        self.screen = pygame.display.set_mode(self.size)
        self.keyboard = SimpleKeyboard(pygame.Rect(kb_pos, kb_size), font, gap)

    def draw(self):
        background = pygame.Surface(self.size)
        background.fill(pygame.Color("#cccccc"))
        self.screen.blit(background, (0, 0))
        self.keyboard.draw(self.screen)

    def dispatch_event(self, e):
        if is_quit(e):
            self.running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            self.keyboard.handle_event(e, self)
        elif e.type == pygame.MOUSEBUTTONUP:
            self.keyboard.handle_event(e, self)
        elif e.type == UI.KEY_PLAYED:
            print(f"Key {e.key.note} played.")
        elif e.type == UI.KEY_RELEASED:
            print(f"Key {e.key.note} released.")
        return True

    def run(self):
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        self.running = True
        while self.running:
            self.draw()
            pygame.display.update()
            self.dispatch_event(pygame.event.wait())

    def fire_key_played(self, key):
        pygame.event.post(pygame.event.Event(UI.KEY_PLAYED, key=key))

    def fire_key_released(self, key):
        pygame.event.post(pygame.event.Event(UI.KEY_RELEASED, key=key))


if __name__ == "__main__":

    UI("Test", 100, 10, 20).run()
