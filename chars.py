import pygame

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("media/coala_tigger_bigger.png").convert_alpha()
        # self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.mask = pygame.mask.from_surface(self.surf)

    def scale(self, size):
        self.surf = pygame.transform.scale(self.surf, size)
        self.rect = self.surf.get_rect()
        self.mask = pygame.mask.from_surface(self.surf)

    # Move the sprite based on keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -1)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 1)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-1, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(1, 0)

        # # Keep player on the screen
        # if self.rect.left < 0:
        #     self.rect.left = 0
        # elif self.rect.right > SCREEN_WIDTH:
        #     self.rect.right = SCREEN_WIDTH
        # if self.rect.top <= 0:
        #     self.rect.top = 0
        # elif self.rect.bottom >= SCREEN_HEIGHT:
        #     self.rect.bottom = SCREEN_HEIGHT