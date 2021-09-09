#!/usr/bin/env python

"""
Basic structure for an ear training app.

Customize by providing an implementation of Quiz.
"""

import random

import pygame
import pygame.freetype
import pygame.midi
import pygame.time

from midi import Note
from midi import play
from music import Scale
from music import chord
from music import melody

initial_button_color = (127, 127, 255)

wrong_button_color = (64, 64, 255)

status_color = (16 * 10, 16 * 10, 255)


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
        b = Button(
            q, (0, rect.top + (i * (h + gap))), (rect.width, h), q.label in wrong
        )
        b.render(surface, font)
        return b

    return [make_button(q, i) for i, q in enumerate(quiz)]


def get_answer(buttons, question, midi_out, status):
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
        elif event.type == pygame.USEREVENT:
            status.update()
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
        the make_choices method can be used to draw an appropriately
        sized set of questions out of the universe.
        """
        return None

    def make_choices(self, universe):
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

    def make_questions(self, choices):
        """
        From the choices returned by choices() return the actual question
        and the choices. The default implementation is fine for many
        quizes where any of the choices could be the actual question.
        Other quizes may create choices that play something in
        relation to the correct answer.
        """
        return random.choice(choices), choices

    def update(self, choice, question):
        "Update any count of how we're doing."

    def status_text(self):
        return ""

    def run(self):

        universe = self.make_universe()

        pygame.init()
        pygame.midi.init()

        font = pygame.freetype.SysFont("helveticaneue", 32)
        status_font = pygame.freetype.SysFont("helveticaneue", 14)

        pygame.display.set_caption(self.name)

        size = (300, 500)
        status_height = 20

        status_padding = 5

        buttons_start = status_height + status_padding
        buttons_size = (size[0], size[1] - buttons_start)

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

            # For updating status
            pygame.time.set_timer(pygame.USEREVENT, 1000)

            status = Status(self, (0, 0), (size[0], status_height), status_font, screen)

            while running:

                if not wrong:
                    choices = self.make_choices(universe)
                    question, questions = self.make_questions(choices)

                # Draw the screen with the buttons.
                screen.blit(background, (0, 0))

                button_rect = pygame.Rect((0, buttons_start), buttons_size)
                buttons = render_buttons(screen, questions, button_rect, font, wrong)

                # Play the progression
                pygame.event.clear()
                status.update()
                question.play(midi_out)

                # Wait for events until we get a button click; check the answer.
                running, choice = get_answer(buttons, question, midi_out, status)
                if running:
                    if choice.label in wrong:
                        choice.play(midi_out)
                    else:
                        if choice == question:
                            play(midi_out, chirp)
                            question.after_correct(midi_out)
                            wrong = set()
                        else:
                            play(midi_out, blat)
                            wrong.add(choice.label)
                        self.update(choice, question)

        finally:
            print(f"Time: {status.time_label()}")
            pygame.midi.quit()
