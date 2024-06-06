from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt
import pygame

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT
)

@dataclass
class Characters:

    player: Player
    enemies: pygame.sprite.Group
    all_chars: pygame.sprite.Group[MazeRunner] = field(init=False, default_factory=pygame.sprite.Group)

    @classmethod
    def generate_characters(cls, enemies_input=None):
        player = Player(r'poohmaze\assets\coala_tigger_bigger.png')
        enemies: Enemies = Enemies()
        badman = Badman(r'poohmaze\assets\badman.png', )
        # enemies.add_enemies(enemies_input)
        chars = cls(
            player, enemies
        )
        chars.all_chars.add(chars.player)
        chars.all_chars.add(chars.enemies.sprites())
        return chars


class Enemies(pygame.sprite.Group):

    def add_enemies(self):
        badman = Badman()
    

class MazeRunner(pygame.sprite.Sprite):

    def __init__(self, bitmap_path: str) -> None:
        super().__init__()
        self.surf = pygame.image.load(bitmap_path).convert_alpha()
        self.rect = self.surf.get_rect()
        self.mask = pygame.mask.from_surface(self.surf)
        self.velocity = 2

    def scale(self, cell_size, scaling_factor = 0.8):
        size = scaling_factor * cell_size[0], scaling_factor * cell_size[1]
        self.surf = pygame.transform.scale(self.surf, size)
        self.rect = self.surf.get_rect()
        self.mask = pygame.mask.from_surface(self.surf)


class Player(MazeRunner):

    # Move the sprite based on keypresses
    def vertical_move(self, pressed_keys, velocity=1):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -velocity)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, velocity)

    # Move the sprite based on keypresses
    def horizontal_move(self, pressed_keys, velocity=1):
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-velocity, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(velocity, 0)

    def move(self, pressed_keys, collision_detector):
        velocity = self.compute_velocity(pressed_keys)
        self.horizontal_move(pressed_keys, velocity[0])
        if collision_detector(self):
            self.horizontal_block(pressed_keys, velocity[0])
        self.vertical_move(pressed_keys, velocity[1])
        if collision_detector(self):
            self.vertical_block(pressed_keys, velocity[1])

    def compute_velocity(self, pressed_keys, absolute_v=2):
        is_vertical = (pressed_keys[K_UP] or pressed_keys[K_DOWN])
        is_horizontal = (pressed_keys[K_LEFT] or pressed_keys[K_RIGHT])
        d = (sqrt(2)/absolute_v)
        velocity = is_horizontal/d, is_vertical/d
        return velocity

    def vertical_block(self, pressed_keys, velocity=1):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, velocity)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, -velocity)

    def horizontal_block(self, pressed_keys, velocity=5):
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(velocity, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(-velocity, 0)


class Badman(MazeRunner):

    def __init__(self, bitmap_path: str, coordinates: tuple) -> None:
        super().__init__(bitmap_path)
        self.rect.center = coordinates
        self.is_waiting_for_target = True
        self.target = None

    def move(self):
        dx = self.target[0] - self.rect.center[0]
        dy = self.target[1] - self.rect.center[1]
        distance = (dx**2 + dy**2)**0.5
        if distance > self.velocity:
            # Calculate the movement vector
            move_x = (dx / distance) * self.velocity
            move_y = (dy / distance) * self.velocity
            
            # Update the position
            self.rect.center[0] += move_x
            self.rect.center[1] += move_y
        else:
            # If the distance is less than the speed, move directly to the target
            self.rect.center[0] = self.target[0]
            self.rect.center[0] = self.target[0]
            self.is_waiting_for_target = True



