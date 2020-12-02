import pygame
import pygame_gui

size = (200, 600)

pygame.init()

pygame.display.set_caption("Quick Start")

window_surface = pygame.display.set_mode(size)

background = pygame.Surface(size)
background.fill(pygame.Color("#dddddd"))

manager = pygame_gui.UIManager(size)


button_1 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((10, 10), (180, 50)),
    text="I-IV-V",
    object_id="button_1",
    manager=manager,
    anchors={"left": "left", "right": "right", "top": "top", "bottom": "bottom"},
)

button_2 = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((10, 60), (180, 50)),
    text="I-V-IV",
    object_id="button_2",
    manager=manager,
    anchors={"left": "left", "right": "right", "top": "top", "bottom": "bottom"},
)

button_1.disable()
button_2.disable()

clock = pygame.time.Clock()

running = True

while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                print(event.ui_object_id)

        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()
