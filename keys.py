#!/usr/bin/env python

import random

import pygame
import pygame.freetype

from app import blat
from app import chirp
from app import is_quit
from app import is_replay
from midi import play
from music import melody


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


class Quiz:
    def __init__(self):
        pygame.midi.init()
        port = pygame.midi.get_default_output_id()
        self.midi_out = pygame.midi.Output(port, 0)
        self.asked = []

    def start(self):
        self.midi_out.set_instrument(0)

    def play(self):
        note = random.choice(range(12))
        self.asked.append(note)
        play(self.midi_out, melody([note]).render(60, 60))

    def replay(self):
        note = self.asked[0]
        play(self.midi_out, melody([note]).render(60, 60))

    def quit(self):
        pygame.midi.quit()

    def check_answer(self, key):
        expected = self.asked.pop(0)
        if expected == key.note:
            print(f"Key {key.note} played. That is correct.")
            play(self.midi_out, chirp)
        else:
            print(
                f"Key {key.note} played. That is incorrect. Correct answer was {expected}"
            )
            play(self.midi_out, blat)

        self.play()

        # Pop expected answer off queue. If matches, either generate a
        # new question or do nothing (if running on a timer). If not
        # correct, then play blat and restart quiz.


class UI:

    KEY_PLAYED = pygame.USEREVENT
    KEY_RELEASED = KEY_PLAYED + 1

    def __init__(self, name, quiz, box_size, gap, padding):
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
        self.quiz = quiz

    def draw(self):
        background = pygame.Surface(self.size)
        background.fill(pygame.Color("#cccccc"))
        self.screen.blit(background, (0, 0))
        self.keyboard.draw(self.screen)

    def dispatch_events(self):
        for e in pygame.event.get():
            if is_quit(e):
                self.running = False
            elif is_replay(e):
                self.quiz.replay()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                self.keyboard.handle_event(e, self)
            elif e.type == pygame.MOUSEBUTTONUP:
                self.keyboard.handle_event(e, self)
            elif e.type == UI.KEY_PLAYED:
                self.quiz.check_answer(e.key)
            elif e.type == UI.KEY_RELEASED:
                pass

    def run(self):

        # Basic quiz loop:
        # 1. Play the quiz question.
        # 2. Treat the next key pressed event as the answer.
        # 3a. If correct, flash key and move to next question.
        # 3b. If incorrect. flash the correct key and start over.
        #
        # Advanced generalization: can play more than one question and
        # expected key presses are queued and actual key presses clear
        # the queue if they are correct. Questions can be presented on
        # a timer and queued until we get too far behind.

        pygame.event.set_blocked(None)  # Block everything.
        pygame.event.set_allowed(
            [
                pygame.QUIT,
                pygame.KEYDOWN,
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                UI.KEY_PLAYED,
                UI.KEY_RELEASED,
            ]
        )

        try:
            self.quiz.start()
            self.quiz.play()

            self.running = True
            while self.running:
                self.draw()
                pygame.display.update()
                self.dispatch_events()

        finally:
            self.quiz.quit()

    def fire_key_played(self, key):
        pygame.event.post(pygame.event.Event(UI.KEY_PLAYED, key=key))

    def fire_key_released(self, key):
        pygame.event.post(pygame.event.Event(UI.KEY_RELEASED, key=key))


if __name__ == "__main__":

    UI("Test", Quiz(), 100, 10, 20).run()
