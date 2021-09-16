import pygame

quit_keys = {pygame.K_ESCAPE, pygame.K_q}


def is_quit(e):
    return e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and (e.key in quit_keys))


def is_replay(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE


def is_replay_with_hint(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_h


def is_establish_key(e):
    return e.type == pygame.KEYDOWN and e.key == pygame.K_k
