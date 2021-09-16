#!/usr/bin/env python

import random

import pygame
import pygame.freetype
import pygame.midi

import eartraining.keyboard
from eartraining.events import is_quit
from eartraining.events import is_replay
from eartraining.midi import play
from eartraining.music import Note
from eartraining.music import Scale
from eartraining.music import Sequence
from eartraining.music import chord
from eartraining.music import melody
from eartraining.music import silence


def is_mouse_event(e):
    return e.type in {pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION}


def is_key_event(e):
    return e.type in {pygame.KEYDOWN, pygame.KEYUP}


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

        elif (note := eartraining.keyboard.get_note(e)) is not None:
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

        elif (note := eartraining.keyboard.get_diatonic_note(e)) is not None:
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


class Quiz:

    """
    Keyboard driven quiz: questions are somehow tied to keys on a
    keyboard. One or more questions are played and then the user needs
    to identify them via the keyboard widget.
    """

    def __init__(self, labels, player):
        self.labels = labels
        self.player = player
        self.asked = None
        self.answered = []

    def start(self):
        self.player.establish_key()

    def next_question(self, num):
        self.asked = [random.choice(range(len(self.labels))) for i in range(num)]

    def play(self):
        self.player.play(self.asked)

    def handle_event(self, e, ui):
        if self.check_answer(e.key):
            ui.fire_next_question()

    def check_answer(self, key):
        self.answered.append(key.note)

        if len(self.answered) == len(self.asked):
            # print(f"Asked: {' '.join([self.labels[i] for i in self.asked])}")
            # print(f"Answered: {' '.join([self.labels[i] for i in self.answered])}")
            if self.asked == self.answered:
                # maybe indicate correct answer somehow.
                self.asked = []
                self.answered = []
                return True
            else:
                self.player.blonk(self.asked, self.answered)
                self.answered = []

        else:
            note = key.note
            to_go = len(self.asked) - len(self.answered)
            print(f"Got key {note}; waiting for {to_go} more.")

        return False


class Player:

    """
    Player knows how to translate from the Quiz indices (which are
    mapped to Keyboard keys) to actual questions, maybe actual notes
    of a scale or chords or whatever.
    """

    def establish_key(self):
        "Play something to establish the key."

    def play(self, elements):
        "Play a sequence of questions. Elements are indexes into the labels array."


class ScalePlayer(Player):
    def __init__(self, midi_out, scale):
        self.midi_out = midi_out
        self.scale = scale

    def establish_key(self):
        play(self.midi_out, melody([0, 12]).render(60, 60))

    def note(self, i):
        return self.scale[i]

    def play(self, elements):
        play(self.midi_out, melody([self.note(i) for i in elements]).render(60, 60))

    def blonk(self, asked, answered):
        def x(a, b):
            if a != b:
                return chord([self.note(a), self.note(b)])
            else:
                return Note(self.note(a))

        blonk = Sequence([x(a, b) for a, b in zip(asked, answered)])
        play(self.midi_out, (blonk + silence(0.25)).render(60, 120))


class UI:

    KEY_PLAYED = pygame.USEREVENT
    KEY_RELEASED = KEY_PLAYED + 1
    NEXT_QUESTION = KEY_RELEASED + 1

    def __init__(self, name, quiz, box_size, gap, padding):
        pygame.init()
        pygame.display.set_caption(name)
        pygame.event.set_blocked(None)  # Block everything.
        pygame.event.set_allowed(
            [
                UI.KEY_PLAYED,
                UI.KEY_RELEASED,
                UI.NEXT_QUESTION,
                pygame.KEYDOWN,
                pygame.KEYUP,
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                pygame.QUIT,
            ]
        )

        keyboard_class = (
            DiatonicKeyboard if len(quiz.labels) == 7 else ChromaticKeyboard
        )

        kb_size = keyboard_class.preferred_size(box_size, gap)
        kb_pos = (padding, padding)

        self.size = ((padding * 2) + kb_size[0], (padding * 2) + kb_size[1])

        font = pygame.freetype.SysFont("helveticaneue", 32)

        self.running = False
        self.screen = pygame.display.set_mode(self.size)
        self.keyboard = keyboard_class(
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
                self.quiz.play()
            elif is_mouse_event(e) or is_key_event(e):
                self.keyboard.handle_event(e, self)
            elif e.type == UI.KEY_PLAYED:
                self.quiz.handle_event(e, self)
            elif e.type == UI.KEY_RELEASED:
                pass
            elif e.type == UI.NEXT_QUESTION:
                self.quiz.next_question(2)
                self.quiz.play()

    def run(self):

        try:
            # For some reason when we block events this seems
            # necessary for mouse up/down events to get through. Not
            # sure what's going on there
            pygame.event.clear()
            self.draw()
            self.quiz.start()

            # Kick off the first note.
            self.fire_next_question()

            self.running = True
            while self.running:
                self.draw()
                self.dispatch_events()

        finally:
            pygame.midi.quit()

    def fire_next_question(self):
        pygame.event.post(pygame.event.Event(UI.NEXT_QUESTION))

    def fire_key_played(self, key):
        pygame.event.post(pygame.event.Event(UI.KEY_PLAYED, key=key))

    def fire_key_released(self, key):
        pygame.event.post(pygame.event.Event(UI.KEY_RELEASED, key=key))


def open_midi_out():
    pygame.midi.init()
    port = pygame.midi.get_default_output_id()
    midi_out = pygame.midi.Output(port, 0)
    midi_out.set_instrument(0)
    return midi_out


if __name__ == "__main__":

    midi_out = open_midi_out()

    quiz = Quiz(
        ("Do", "Re", "Mi", "Fa", "Sol", "La", "Ti"),
        ScalePlayer(midi_out, Scale.major),
    )

    chromatic_quiz = Quiz(
        ("Do", "Di", "Re", "Ri", "Mi", "Fa", "Fe", "Sol", "Si", "La", "Li", "Ti"),
        ScalePlayer(midi_out, list(range(12))),
    )

    UI("Solfege", quiz, 100, 10, 20).run()
