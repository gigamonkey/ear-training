"""
Abstracted representation of notes, chords, and rests and
functions for rendering them into note on/note off events.

Notes, chords, and rests have only a duration, expressed in terms of
(possibly fractional) quarter notes but can be arranged in a list
which can then be rendered as a sorted list of note on and note off
events.

Multiple sequences can be combined in parallel to allow overlapping
notes.
"""

import time


def play(midi_out, events):

    t_zero = time.monotonic()

    for e in events:
        # TODO: check accuracy of sleep timing
        t = time.monotonic()
        at = t_zero + e.time
        if at > t:
            time.sleep(at - t)
        e.emit(midi_out)
