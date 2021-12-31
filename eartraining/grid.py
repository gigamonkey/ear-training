#!/usr/bin/env python

"""
Basic structure for an ear training app.

Customize by providing an implementation of Quiz.
"""

import random
from collections import defaultdict
from dataclasses import dataclass
from typing import List

import pygame
import pygame.freetype
import pygame.midi
import pygame.time

from eartraining.midi import play
from eartraining.music import Scale
from eartraining.music import melody
from eartraining.ui import Button
from eartraining.ui import ButtonState
from eartraining.ui import Grid
from eartraining.ui import Status
from eartraining.ui import is_establish_key
from eartraining.ui import is_quit
from eartraining.ui import is_replay
from eartraining.ui import is_replay_with_hint

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


@dataclass
class Row:
    questions: List[Question]
    active: bool = True


@dataclass
class QuestionGrid:
    rows: List[Row]

    def get_question(self):
        row = random.choice([r for r in self.rows if r.active])
        return random.choice(row.questions)


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
    def __init__(self):
        self.current_question = Question()  # Dummy question
        self.grid = self.make_grid()

    def make_grid(self):
        """
        Make a grid of questions.
        """

    def dimensions(self):
        return len(self.grid.rows), len(self.grid.rows[0].questions)

    def update(self, choice, question):
        "Update any count of how we're doing."

    def status_text(self):
        return ""

    def next_question(self):
        question = self.grid.get_question()
        self.current_question = question

        pygame.event.post(pygame.event.Event(QuizUI.NEW_QUESTION, question=question))

    def check_answer(self, choice):
        print(f"Checking answer for {choice} with current: {self.current_question}")
        self.update(choice, self.current_question)

        if choice is self.current_question:
            pygame.event.post(
                pygame.event.Event(QuizUI.CORRECT_ANSWER, question=choice)
            )
            self.next_question()
            return True
        else:
            pygame.event.post(
                pygame.event.Event(
                    QuizUI.WRONG_ANSWER, question=self.current_question, choice=choice
                )
            )
            return False


class QuizUI:

    CLOCK_TICK = pygame.event.custom_type()
    SOUND_DONE = pygame.event.custom_type()
    NEW_QUESTION = pygame.event.custom_type()
    CORRECT_ANSWER = pygame.event.custom_type()
    WRONG_ANSWER = pygame.event.custom_type()

    def __init__(self, name, quiz):
        pygame.init()
        pygame.display.set_caption(name)
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        pygame.event.pump()

        self.quiz = quiz
        self.listeners = defaultdict(list)
        self.running = False

        r, c = quiz.dimensions()

        print(f"Dimensions {r, c}")

        self.clock = Clock()

        status_font = pygame.freetype.SysFont("helveticaneue", 14)
        status_height = 20
        status_padding = 5
        button_size = 100
        self.size = (
            (c * button_size) + status_height + status_padding,
            r * button_size,
        )
        print(f"Size {self.size}")
        self.screen = pygame.display.set_mode(self.size)
        self.status = Status(
            self.quiz,
            (0, 0),
            (self.size[0], status_height),
            status_font,
            self.screen,
            self.clock,
        )

        button_font = pygame.freetype.SysFont("helveticaneue", 32)
        buttons_start = status_height + status_padding
        buttons_size = (self.size[0], self.size[1] - buttons_start)
        buttons_rect = pygame.Rect((0, buttons_start), buttons_size)
        self.grid = Grid(self.screen, button_font, buttons_rect, 5)
        self.grid.set_questions(self.quiz.grid)

        self.register_listener(pygame.QUIT, self)
        self.register_listener(pygame.KEYDOWN, self)
        self.register_listener(QuizUI.NEW_QUESTION, self)
        self.register_listener(QuizUI.CORRECT_ANSWER, self)
        self.register_listener(QuizUI.WRONG_ANSWER, self)
        self.register_listener(Button.BUTTON_PRESSED, self)
        self.register_listener(QuizUI.CLOCK_TICK, self.status)
        self.register_listener(pygame.MOUSEBUTTONDOWN, self.grid)
        self.register_listener(pygame.MOUSEBUTTONUP, self.grid)
        self.register_listener(pygame.KEYDOWN, self.grid)

    def register_listener(self, type, listener):
        self.listeners[type].append(listener)

    def dispatch_events(self):
        for event in pygame.event.get():
            for listener in self.listeners[event.type]:
                listener.handle_event(event)

    def handle_event(self, event):
        "The events we handle directly."
        if is_quit(event):
            self.running = False

        elif is_replay(event):
            self.quiz.current_question.play(self.midi_out)

        elif is_replay_with_hint(event):
            self.quiz.current_question.hint(self.midi_out)

        elif is_establish_key(event):
            play(self.midi_out, establish_key)

        elif event.type == QuizUI.NEW_QUESTION:
            self.draw()
            event.question.play(self.midi_out)

        elif event.type == QuizUI.CORRECT_ANSWER:
            self.play_and_wait(self.correct_sound)
            self.draw()
            event.question.after_correct(self.midi_out)

        elif event.type == QuizUI.WRONG_ANSWER:
            self.play_and_wait(self.wrong_sound)
            self.draw()
            event.question.play(self.midi_out)

        elif event.type == Button.BUTTON_PRESSED:
            print(f"Got button presssed")
            # FIXME: this should probably live in the Button itself.
            if event.button.state is ButtonState.WRONG:
                # We get here when the button has already been marked
                # wrong previously.
                event.button.question.play(self.midi_out)
            else:
                print(f"About to check answer")
                if not self.quiz.check_answer(event.button.question):
                    event.button.state = ButtonState.WRONG
                    event.button.draw()

    def draw(self):
        background = pygame.Surface(self.size)
        background.fill(pygame.Color("#dddddd"))
        self.screen.blit(background, (0, 0))
        self.status.draw()
        self.grid.draw()
        pygame.display.update()

    def run(self):
        try:
            self.setup_sound_effects()
            self.open_midi_out()
            self.clock.start()
            self.quiz.next_question()

            self.running = True
            while self.running:
                self.dispatch_events()

        finally:
            print(f"Time: {self.status.time_label(self.clock.elapsed())}")
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
