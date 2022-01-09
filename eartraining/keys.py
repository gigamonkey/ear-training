#!/usr/bin/env python

import random

import pygame
import pygame.freetype
import pygame.midi

from eartraining.midi import play
from eartraining.music import Note
from eartraining.music import Scale
from eartraining.music import Sequence
from eartraining.music import chord
from eartraining.music import melody
from eartraining.music import rest
from eartraining.ui import ChromaticKeyboard
from eartraining.ui import DiatonicKeyboard
from eartraining.ui import is_key_event
from eartraining.ui import is_mouse_event
from eartraining.ui import is_quit
from eartraining.ui import is_replay


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
        self.midi_out = None

    def start(self, midi_out):
        self.midi_out = midi_out
        self.player.establish_key(self.midi_out)

    def next_question(self, num):
        self.asked = [random.choice(range(len(self.labels))) for i in range(num)]

    def play(self):
        self.player.play(self.asked, self.midi_out)

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
                self.player.blonk(self.asked, self.answered, self.midi_out)
                self.answered = []

        else:
            note = key.note
            to_go = len(self.asked) - len(self.answered)
            print(f"Got key {note}; waiting for {to_go} more.")

        return False


class ScalePlayer:
    def __init__(self, scale):
        self.scale = scale

    def establish_key(self, midi_out):
        play(midi_out, melody([0, 12]).render(60, 60))

    def note(self, i):
        return self.scale[i]

    def play(self, elements, midi_out):
        play(midi_out, melody([self.note(i) for i in elements]).render(60, 60))

    def blonk(self, asked, answered, midi_out):
        def x(a, b):
            if a != b:
                return chord([self.note(a), self.note(b)])
            else:
                return Note(self.note(a))

        blonk = Sequence([x(a, b) for a, b in zip(asked, answered)])
        play(midi_out, (blonk + rest(0.25)).render(60, 120))


class UI:

    KEY_PLAYED = pygame.event.custom_type()
    KEY_RELEASED = pygame.event.custom_type()
    NEXT_QUESTION = pygame.event.custom_type()

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
                self.quiz.play(self.midi_out)
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
            self.open_midi_out()

            # For some reason when we block events this seems
            # necessary for mouse up/down events to get through. Not
            # sure what's going on there
            pygame.event.clear()
            self.draw()
            self.quiz.start(self.midi_out)

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

    def open_midi_out(self):
        pygame.midi.init()
        port = pygame.midi.get_default_output_id()
        self.midi_out = pygame.midi.Output(port, 0)
        self.midi_out.set_instrument(0)


if __name__ == "__main__":

    diatonic_labels = ("Do", "Re", "Mi", "Fa", "Sol", "La", "Ti")
    chromatic_labels = (
        "Do",
        "Di",
        "Re",
        "Ri",
        "Mi",
        "Fa",
        "Fe",
        "Sol",
        "Si",
        "La",
        "Li",
        "Ti",
    )

    diatonic_quiz = Quiz(
        diatonic_labels,
        ScalePlayer(Scale.major),
    )
    chromatic_quiz = Quiz(
        chromatic_labels,
        ScalePlayer(list(range(12))),
    )

    UI("Solfege", diatonic_quiz, 100, 10, 20).run()
