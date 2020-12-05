#!/usr/bin/env python

"""
Basic structure for an ear training app.

Customize by providing an implementation of Quiz.
"""

import random

import pygame
import pygame.freetype
import pygame.midi

from midi import Note
from midi import play
from music import Scale
from music import chord
from music import melody

size = (300, 500)

initial_button_color = (127, 127, 255)

wrong_button_color = (64, 64, 255)


def silence(duration):
    return Note(0, duration, 0)


# Played when we get it right.
chirp = (melody((0, 5, 7, 12, 17, 19, 24)).rhythm(1 / 64) + silence(1 / 4)).render(
    96, 120
)

# Played when we get it wrong.
blat = (chord((0, 1, 2, 3, 4)).rhythm(1 / 32) + silence(1 / 2)).render(30, 120)


establish_key = (
    (melody(Scale.major + (12,) + tuple(reversed(Scale.major))))
    .rhythm(1 / 16)
    .render(60, 120)
)


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
        """
        Make the universe from which make_questions will create a set of
        questions. This method is only called once and it's result is
        turned into a set of actual choices each time we present a new
        question. For simple quizes the universe *is* the set of
        choices and only needs to be generated once. If the universe
        of possible questions is too big to present all at once then
        the make_questions method can be used to drwa an appropriately
        sized set of questions out of the universe.
        """

    def choices(self, universe):
        """
        From the universe of possible questions, pick an appropriately
        sized subset of choices to present in one question. If the set
        of choices is always the same, then the default implementation
        is fine. If the universe is too big, override this method to
        reduce it in some way. That might be as simple as picking some
        choices at random but may require picking related elements of
        the total universe.
        """
        return universe

    def make_questions(self, universe):
        """
        From the choices returned by choices() return the actual question
        and the choices. The default implementation is fine for many
        quizes where any of the choices could be the actual question.
        Other quizes may create choices that play something in
        relation to the correct answer.
        """
        choices = self.choices(universe)
        return random.choice(choices), choices

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
                    question, questions = self.make_questions(universe)

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
                        play(midi_out, chirp)
                        question.after_correct(midi_out)
                        wrong = set()
                    else:
                        if choice.label in wrong:
                            choice.play(midi_out)
                        else:
                            play(midi_out, blat)
                            wrong.add(choice.label)

        finally:
            pygame.midi.quit()
