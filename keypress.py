#!/usr/bin/env python

"Utility for finding out what keys' scancodes are."


import pygame as pg
import pygame.midi


def run():

    pg.init()

    while True:
        e = pg.event.wait()
        if e.type == pg.QUIT:
            break
        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_ESCAPE:
                break
            else:
                print(f"KEYDOWN: {e}")


if __name__ == "__main__":

    run()
