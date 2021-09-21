#!/usr/bin/env python

"""
Basic structure for an ear training app.

Customize by providing an implementation of Quiz.
"""

import random
from dataclasses import dataclass

import pygame
import pygame.freetype
import pygame.midi
import pygame.time

from eartraining.midi import play
from eartraining.music import Scale
from eartraining.music import melody
from eartraining.ui import Status
from eartraining.ui import is_establish_key
from eartraining.ui import is_quit
from eartraining.ui import is_replay
from eartraining.ui import is_replay_with_hint
from eartraining.ui import render_buttons

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

    def after_incorrect(self, midi_out, choice, question):
        "Some quizes want to play something after an incorrect answer."


@dataclass
class Clock:

    "Keep track of elasped time."

    start_tick = None

    def start(self):
        self.start_tick = pygame.time.get_ticks()
        pygame.time.set_timer(QuizUI.CLOCK_TICK, 1000)

    def elapsed(self):
        return pygame.time.get_ticks() - self.start_tick


class Quiz:
    def make_universe(self):
        """
        Make the universe from which make_questions will create a set of
        questions. This method is only called once and its result is
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


class QuizUI:

    CLOCK_TICK = pygame.event.custom_type()
    SOUND_DONE = pygame.event.custom_type()

    def __init__(self, name, quiz):
        pygame.init()
        pygame.display.set_caption(name)
        pygame.event.set_blocked(pygame.MOUSEMOTION)

        self.size = (300, 500)
        self.clock = Clock()
        self.screen = pygame.display.set_mode(self.size)
        self.quiz = quiz

    def draw(self, questions, wrong):
        background = pygame.Surface(self.size)
        background.fill(pygame.Color("#dddddd"))
        self.screen.blit(background, (0, 0))

        font = pygame.freetype.SysFont("helveticaneue", 32)
        status_font = pygame.freetype.SysFont("helveticaneue", 14)

        status_height = 20
        status_padding = 5
        status = Status(
            self, (0, 0), (self.size[0], status_height), status_font, self.screen
        )

        buttons_start = status_height + status_padding
        buttons_size = (self.size[0], self.size[1] - buttons_start)

        button_rect = pygame.Rect((0, buttons_start), buttons_size)
        buttons = render_buttons(self.screen, questions, button_rect, font, wrong)
        pygame.display.update()

        return buttons, status

    def get_answer(self, buttons, question, status):
        while True:
            event = pygame.event.wait()
            if is_quit(event):
                return False, None
            elif is_replay(event):
                question.play(self.midi_out)
            elif is_replay_with_hint(event):
                question.hint(self.midi_out)
            elif is_establish_key(event):
                play(self.midi_out, establish_key)
            elif event.type == QuizUI.CLOCK_TICK:
                status.update(self.clock.elapsed(), self.quiz.status_text())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for b in buttons:
                    if b.is_hit(event.pos):
                        return True, b.question

    def run(self):
        try:
            self.setup_sound_effects()
            self.open_midi_out()
            self.clock.start()

            universe = self.quiz.make_universe()
            wrong = set()
            running = True

            while running:

                if not wrong:
                    choices = self.quiz.make_choices(universe)
                    question, questions = self.quiz.make_questions(choices)

                buttons, status = self.draw(questions, wrong)

                # Play the progression
                pygame.event.clear()
                status.update(self.clock.elapsed(), self.quiz.status_text())
                question.play(self.midi_out)

                # Wait for events until we get a button click; check the answer.
                running, choice = self.get_answer(buttons, question, status)
                if running:
                    if choice.label in wrong:
                        choice.play(self.midi_out)
                    else:
                        if choice == question:
                            self.play_and_wait(self.correct_sound)
                            question.after_correct(self.midi_out)
                            wrong = set()
                        else:
                            self.play_and_wait(self.wrong_sound)
                            question.after_incorrect(self.midi_out, choice, question)
                            wrong.add(choice.label)
                        self.quiz.update(choice, question)

        finally:
            print(f"Time: {status.time_label(self.clock.elapsed())}")
            pygame.midi.quit()

    def setup_sound_effects(self):
        pygame.mixer.init()

        self.correct_sound = pygame.mixer.Sound("sounds/bell.wav")
        self.correct_sound.set_volume(0.10)

        self.wrong_sound = pygame.mixer.Sound("sounds/boop.wav")
        self.wrong_sound.set_volume(0.10)

        channel = pygame.mixer.Channel(0)
        channel.set_endevent(QuizUI.SOUND_DONE)

    def play_and_wait(self, sound):
        "Play a non-MIDI sound."
        sound.play(maxtime=500)

        # Wait for sound to be done.
        while True:
            event = pygame.event.wait()
            if event.type == QuizUI.SOUND_DONE:
                pygame.time.wait(300)
                break

    def open_midi_out(self):
        pygame.midi.init()
        port = pygame.midi.get_default_output_id()
        self.midi_out = pygame.midi.Output(port, 0)
        self.midi_out.set_instrument(0)
