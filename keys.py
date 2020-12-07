#!/usr/bin/env python


import random

import pygame
import pygame.freetype

from app import is_quit
from app import is_replay
from midi import play
from music import Scale
from music import melody


def is_mouse_event(e):
    return e.type in {pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION}


def is_key_event(e):
    return e.type in {pygame.KEYDOWN, pygame.KEYUP}


class SimpleKeyboard:

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

        max_width = ((rect.width + gap) / len(SimpleKeyboard.white_keys)) - gap
        max_height = ((rect.height + gap) / 2) - gap

        size = (min(max_width, max_height),) * 2
        self.keys = [
            Key(k, labels[k], self.key_rect(k, size), self.font)
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
        key = None

        if is_mouse_event(e):
            for k in self.keys:
                if k.rect.collidepoint(e.pos):
                    key = k
                    break
        elif is_key_event(e) and e.key in SimpleKeyboard.number_keys:
            i = Scale.major[SimpleKeyboard.number_keys.index(e.key)]
            key = self.keys[i]

        if key is not None:
            if e.type in {pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN}:
                ui.fire_key_played(key)
            elif e.type in {pygame.MOUSEBUTTONUP, pygame.KEYUP}:
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


class Quiz:
    def __init__(self, labels):
        self.labels = labels
        self.asked = []
        self.retry = None
        self.last_key = None

    def start(self):
        pygame.midi.init()
        port = pygame.midi.get_default_output_id()
        self.midi_out = pygame.midi.Output(port, 0)
        self.midi_out.set_instrument(0)
        self.play_note(0)

    def play(self):
        if self.retry:
            note = self.retry
            self.retry = None
        else:
            note = random.choice(Scale.major)

        self.asked.append(note)
        self.play_note(note)

    def play_note(self, note):
        play(self.midi_out, melody([note]).render(60, 60))

    def replay(self):
        note = self.asked[0]
        play(self.midi_out, melody([note]).render(60, 60))

    def quit(self):
        pygame.midi.quit()

    def handle_event(self, e, ui):
        self.check_answer(e.key)
        ui.fire_next_note()

    def check_answer(self, key):
        expected = self.asked.pop(0)
        if self.last_key is not None:
            self.last_key.unlight()
        self.last_key = key
        if expected == key.note:
            # key.highlight()
            pass
        else:
            # play(self.midi_out, blat)
            key.lowlight()
            self.last_key = key
            self.retry = expected


class UI:

    KEY_PLAYED = pygame.USEREVENT
    KEY_RELEASED = KEY_PLAYED + 1
    NEXT_NOTE = KEY_RELEASED + 1

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
        self.keyboard = SimpleKeyboard(
            quiz.labels, pygame.Rect(kb_pos, kb_size), font, gap
        )
        self.quiz = quiz

    def draw(self):
        background = pygame.Surface(self.size)
        background.fill(pygame.Color("#cccccc"))
        self.screen.blit(background, (0, 0))
        self.keyboard.draw(self.screen)
        pygame.display.update()

    def dispatch_events(self):
        for e in pygame.event.get():
            if is_quit(e):
                self.running = False
            elif is_replay(e):
                self.quiz.replay()
            elif is_mouse_event(e) or is_key_event(e):
                self.keyboard.handle_event(e, self)
            elif e.type == UI.KEY_PLAYED:
                self.quiz.handle_event(e, self)
            elif e.type == UI.KEY_RELEASED:
                pass
            elif e.type == UI.NEXT_NOTE:
                self.quiz.play()

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
                UI.KEY_PLAYED,
                UI.KEY_RELEASED,
                UI.NEXT_NOTE,
                pygame.KEYDOWN,
                pygame.KEYUP,
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                pygame.QUIT,
            ]
        )

        try:
            self.draw()
            self.quiz.start()

            # Kick off the first note.
            self.fire_next_note()

            self.running = True
            while self.running:
                self.draw()
                self.dispatch_events()

        finally:
            self.quiz.quit()

    def fire_next_note(self):
        pygame.event.post(pygame.event.Event(UI.NEXT_NOTE))

    def fire_key_played(self, key):
        pygame.event.post(pygame.event.Event(UI.KEY_PLAYED, key=key))

    def fire_key_released(self, key):
        pygame.event.post(pygame.event.Event(UI.KEY_RELEASED, key=key))


if __name__ == "__main__":

    solfege = ("Do", "Di", "Re", "Ri", "Mi", "Fa", "Fe", "Sol", "Si", "La", "Li", "Ti")

    UI("Test", Quiz(solfege), 100, 10, 20).run()
