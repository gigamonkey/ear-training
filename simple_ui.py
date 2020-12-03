from dataclasses import dataclass
import pygame
import pygame.freetype

size = (300, 500)

pygame.init()

pygame.display.set_caption("Quick Start")

window_surface = pygame.display.set_mode(size)

background = pygame.Surface(size)
background.fill(pygame.Color("#dddddd"))

clock = pygame.time.Clock()

font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 32)


class Button:
    def __init__(self, label, pos, size):
        self.label = label
        self.rect = pygame.Rect(pos, size)

    def render(self, screen):
        surface = pygame.Surface(self.rect.size)
        pygame.draw.rect(
            surface,
            (127, 127, 255),
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
        )
        text, text_rect = font.render(self.label, (0, 0, 0))

        x = (self.rect.width - text_rect.width) / 2
        y = (self.rect.height - text_rect.height) / 2

        surface.blit(text, (x, y))
        screen.blit(surface, (self.rect.x, self.rect.y))


button1 = Button("I-IV-V-I", (0, 0), (300, 100))
button2 = Button("I-ii-vi-I", (0, 110), (300, 100))


def is_quit(e):
    return e.type == pygame.QUIT or (
        e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE
    )


def render_buttons(surface, labels, rect, gap=5):

    num = len(labels)

    # (num * h) + ((num - 1) * gap) = rect.height
    # (num * h) + (num * gap) - gap = rect.height
    # (num * h) + (num * gap) = rect.height + gap
    # num * (h + gap) = rect.height + gap
    # h + gap = (rect.height + gap) / num
    h = ((rect.height + gap) / num) - gap

    buttons = [
        Button(label, (0, i * (h + gap)), (rect.width, h))
        for i, label in enumerate(labels)
    ]
    for b in buttons:
        b.render(surface)
        # surface.blit(b.render(), (b.rect.x, b.rect.y))

    return buttons


pygame.event.set_blocked(pygame.MOUSEMOTION)

running = True

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if is_quit(event):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for b in buttons:
                if b.rect.collidepoint(event.pos):
                    print(b.label)

    window_surface.blit(background, (0, 0))

    buttons = render_buttons(
        window_surface,
        ("I-IV-V-I", "I-ii-vi-I", "I-iii-V-I"),
        pygame.Rect(0, 0, 300, 500),
    )

    pygame.display.update()
