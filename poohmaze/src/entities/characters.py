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
        # enemies.add_enemies(enemies_input)
        chars = cls(
            player, enemies
        )
        chars.all_chars.add(chars.player)
        chars.all_chars.add(chars.enemies.sprites())
        return chars


class Enemies(pygame.sprite.Group):

    def add_enemies(self, enemies_config):
        badmans = enemies_config['badmans']
        for badman_config in badmans:
            bitmap_path = badman_config[0]
            coordinates = badman_config[1]
            badman = Badman(bitmap_path, coordinates)
            self.add(badman)
        
    

class MazeRunner(pygame.sprite.Sprite):

    def __init__(self, bitmap_path: str) -> None:
        super().__init__()
        self.surf = pygame.image.load(bitmap_path).convert_alpha()
        self.rect = self.surf.get_rect()
        self.mask = pygame.mask.from_surface(self.surf)

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
        self.maze_coordinates: tuple = coordinates
        self.is_moving = False
        self.target = None
        self.movement_mode = None
        self.direction = None

    def move(self, velocity=1):
        if self.direction=='l':
            self.rect.move_ip(-velocity, 0)
        elif self.direction=='r':
            self.rect.move_ip(velocity, 0)
        elif self.direction=='t':
            self.rect.move_ip(0, -velocity)
        elif self.direction=='b':
            self.rect.move_ip(0, velocity)
    
    def compute_target(
            self, 
            x, 
            y, 
            dir, 
            cell_height, 
            cell_width
        ):
        if dir=='t':
            y = y - cell_height
        elif dir=='b':
            y = y + cell_height
        elif dir=='l':
            x = x - cell_width
        elif dir=='r':
            x = x + cell_width
        return x, y
            



