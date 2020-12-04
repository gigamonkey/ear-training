#!/usr/bin/env python

"""
Basic structure for an ear training app.

Customize by providing an implementation of Quiz.
"""

import random

import pygame
import pygame.freetype
import pygame.midi

from chords import major_scale
from chords import scale_up_down
from midi import Line
from midi import Note
from midi import play
from midi import sequence

size = (300, 500)

initial_button_color = (127, 127, 255)

wrong_button_color = (64, 64, 255)

# Played when we get it right.
chirp = Line([Note(1 / 16, 96 + n) for n in (0, 5, 7, 12, 17, 19, 24)]).note(60, 1, 0)

# Played when we get it wrong.
blat = Line().chord([30, 31, 32, 33, 34], 1 / 8).note(60, 2, 0)


establish_key = scale_up_down(major_scale, 60, 120)


class Question:
    def play(self, midi_out):
        "Play the question."

    def hint(self, midi_out):
        "Play a hint for the question. By default is just the question again."
        self.play(midi_out)

    def after_correct(self, midi_out):
        "Some quizes want to play something after a correct answer."


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


def is_quit(e):
    return e.type == pygame.QUIT or (
        e.type == pygame.KEYDOWN and (e.key in {pygame.K_ESCAPE, pygame.K_q})
    )


def is_replay(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE


def is_replay_with_hint(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_h


def is_establish_key(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_k


def render_buttons(surface, quiz, rect, font, wrong, gap=5):

    h = ((rect.height + gap) / len(quiz)) - gap

    def make_button(q, i):
        b = Button(q, (0, i * (h + gap)), (rect.width, h), q.label in wrong)
        b.render(surface, font)
        return b

    return [make_button(q, i) for i, q in enumerate(quiz)]


def get_answer(buttons, question, midi_out):
    while True:
        event = pygame.event.wait()
        if is_quit(event):
            return False, None
        elif is_replay(event):
            question.play(midi_out)
        elif is_replay_with_hint(event):
            question.hint(midi_out)
        elif is_establish_key(event):
            play(midi_out, establish_key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for b in buttons:
                if b.is_hit(event.pos):
                    return True, b.question


class Quiz:
    def __init__(self, name):
        self.name = name

    def make_universe(self):
        "Make the universe from which make_questions will create a set of questions."

    def make_questions(self, universe):
        return universe

    def run(self):

        universe = self.make_universe()

        pygame.init()
        pygame.midi.init()

        font = pygame.freetype.SysFont("helveticaneue", 32)

        pygame.display.set_caption(self.name)

        screen = pygame.display.set_mode(size)

        background = pygame.Surface(size)
        background.fill(pygame.Color("#dddddd"))

        pygame.event.set_blocked(pygame.MOUSEMOTION)

        port = pygame.midi.get_default_output_id()
        midi_out = pygame.midi.Output(port, 0)

        try:
            midi_out.set_instrument(0)

            running = True

            wrong = set()

            while running:

                if not wrong:
                    questions = self.make_questions(universe)
                    question = random.choice(questions)

                # Draw the screen with the buttons.
                screen.blit(background, (0, 0))
                buttons = render_buttons(
                    screen, questions, pygame.Rect(0, 0, 300, 500), font, wrong
                )
                pygame.display.update()

                # Play the progression
                pygame.event.clear()
                question.play(midi_out)

                # Wait for events until we get a button click; check the answer.
                running, choice = get_answer(buttons, question, midi_out)
                if running:
                    if choice == question:
                        play(midi_out, sequence(chirp, 120))
                        question.after_correct(midi_out)
                        wrong = set()
                    else:
                        if choice.label in wrong:
                            choice.play(midi_out)
                        else:
                            play(midi_out, sequence(blat, 120))
                            wrong.add(choice.label)

        finally:
            pygame.midi.quit()
