#!/usr/bin/env python

import pygame
import pygame.freetype

from app import is_quit


class SimpleKeyboard:

    "Abstracted one-octave piano keyboard widget."

    keys = range(12)

    white_keys = [0, 2, 4, 5, 7, 9, 11]

    black_keys = set(keys) - set(white_keys)

    def __init__(self, rect, font, gap):
        self.rect = rect
        self.font = font
        self.gap = gap

        self.pressed = set()

        max_width = ((rect.width + gap) / 7) - gap
        max_height = ((rect.height + gap) / 2) - gap

        s = min(max_width, max_height)
        size = (s, s)

        self.keys = [
            pygame.Rect(self.key_pos(k, size), size) for k in SimpleKeyboard.keys
        ]
        self.rect = pygame.Rect(rect.center, (0, 0)).unionall(self.keys)

    def render_key(self, size, label, pressed):
        color = (127, 127, 255) if not pressed else (64, 64, 255)

        surface = pygame.Surface(size)
        pygame.draw.rect(surface, color, pygame.Rect((0, 0), size))

        text, text_rect = self.font.render(label, (0, 0, 0))
        x = (size[0] - text_rect.width) / 2
        y = (size[1] - text_rect.height) / 2
        surface.blit(text, (x, y))

        return surface

    def key_pos(self, note, size):
        if note not in SimpleKeyboard.black_keys:
            i = SimpleKeyboard.white_keys.index(note)
            x = self.rect.x + (i * (size[0] + self.gap))
            y = self.rect.y + size[1] + self.gap
            return (x, y)
        else:
            x, y = self.key_pos(note - 1, size)
            return (x + size[0] / 2, y - (size[1] + self.gap))

    def draw(self, parent):
        for k in range(12):
            r = self.keys[k]
            s = self.render_key(r.size, str(k), k in self.pressed)
            parent.blit(s, r.topleft)

    def handle_event(self, e, ui):
        for i in range(12):
            if self.keys[i].collidepoint(e.pos):
                self.pressed.add(i)
                ui.key_played(i)


class UI:

    KEY_PLAYED = pygame.USEREVENT

    def __init__(self, name, box_size, gap, padding):
        pygame.init()
        pygame.display.set_caption(name)

        keyboard_width = (box_size * 7) + (gap * 6)
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
        elif e.type == UI.KEY_PLAYED:
            print(f"Key {e.note} played.")
        return True

    def run(self):
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        self.running = True
        while self.running:
            self.draw()
            pygame.display.update()
            self.dispatch_event(pygame.event.wait())

    def key_played(self, note):
        pygame.event.post(pygame.event.Event(UI.KEY_PLAYED, note=note))


if __name__ == "__main__":

    UI("Test", 100, 10, 20).run()
