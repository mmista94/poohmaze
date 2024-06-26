from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt
from typing import Any, Iterable
import pygame
from pygame.math import Vector2

# from ..game import DESIRED_FPS
# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
# from pygame.locals import *
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_w,
    K_s,
    K_a,
    K_d
)
from pygame.sprite import AbstractGroup

from .maze import Maze

DESIRED_FPS = 100

@dataclass
class Characters:

    player: Player
    enemies: pygame.sprite.Group[Badman]
    players: pygame.sprite.Group[Player]
    targets: pygame.sprite.Group[MazeRunner]
    all_chars: pygame.sprite.Group[MazeRunner] = field(
        init=False, 
        default_factory=pygame.sprite.Group
    )
    players_backup: list = field(
        init=False, 
        default_factory=list
    )

    @classmethod
    def generate_characters(cls, maze: Maze):
        player = Player(r'poohmaze\assets\coala_tigger_bigger.png')
        # player_two = Player(r'poohmaze\assets\pingwin.png', True)
        players = pygame.sprite.Group()
        players.add(player)
        # players.add(player_two)
        enemies: Enemies = Enemies(maze=maze)
        targets: Targets = Targets(maze=maze)
        chars = cls(
            player, enemies, players, targets
        )
        chars.players_backup.append(player)
        # chars.players_backup.append(player_two)
        chars.all_chars.add(chars.players.sprites())
        chars.all_chars.add(chars.enemies.sprites())
        chars.all_chars.add(chars.targets.sprites())
        return chars
    
    def reset_player(self, player, cell_size):
        player.set_starting_position(cell_size)
        self.players.add(player)
        self.all_chars.add(player)

    def reset_targets(self):
        for target in self.targets.backup:
            self.targets.add(target)
        self.all_chars.add(self.targets.sprites())       



class Enemies(pygame.sprite.Group):

    def __init__(self, maze, *sprites: Any | AbstractGroup | Iterable) -> None:
        super().__init__(*sprites)
        self.add_enemies(maze)

    def add_enemies(self, maze: Maze, number: int = 3):
        for _ in range(number):
            badman = Badman(r'poohmaze\assets\badman.png')
            badman.starting_coordinates = maze.random_location()
            self.add(badman)

class Targets(pygame.sprite.Group):

    def __init__(self, maze, *sprites: Any | AbstractGroup | Iterable) -> None:
        super().__init__(*sprites)
        self.backup: list[MazeRunner] = []
        self.add_targets(maze)

    def add_targets(self, maze: Maze, number: int = 5):
        for _ in range(number):
            target = MazeRunner(r'poohmaze\assets\star.png')
            target.starting_coordinates = maze.random_location()
            self.add(target)
            self.backup.append(target)
    

class MazeRunner(pygame.sprite.Sprite):



    def __init__(self, bitmap_path: str) -> None:
        super().__init__()
        self.bitmap = pygame.image.load(bitmap_path).convert_alpha()
        self.surf = self.bitmap
        # self.position: Vector2 = None
        # self.velocity = Vector2(0,0)
        # self.scale(cell_size=cell_size)
        self.rect = self.surf.get_rect()
        self.mask = pygame.mask.from_surface(self.surf)
        # self.velocity = None
        self.speed_x = None
        self.speed_y = None
        self.previous_size = None
        self.starting_coordinates = None

    def update_geometry(self, size, cell_size):
        self.update_position_after_resize(size, cell_size)
        self.scale(cell_size)
        self.update_velocity(size)

    def scale(self, cell_size, scaling_factor = 0.8):
        size = scaling_factor * cell_size[0], scaling_factor * cell_size[1]
        self.surf = pygame.transform.scale(self.bitmap, size)
        self.rect = self.surf.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.surf)

    def update_position_after_resize(self, size: tuple, cell_size):
        # Calculate the new position of the object based on the resize ratio
        # Calculate the new position of the object based on the resize ratio
        if not self.previous_size:
            self.previous_size = size
            self.set_starting_position(cell_size)
        x = size[0] * self.rect.center[0] / self.previous_size[0]
        y = size[1] * self.rect.center[1] / self.previous_size[1]
        self.rect.center = x, y

    def update_velocity(self, size: tuple):
        self.speed_y = (size[1] / 200) / (DESIRED_FPS/60)
        self.speed_x = (size[0] / 200)  / (DESIRED_FPS/60)

    def set_starting_position(self, cell_size):
        x = cell_size[0]*(self.starting_coordinates[0] + 0.5)
        y = cell_size[1]*(self.starting_coordinates[1] + 0.5)
        self.position = pygame.Vector2(x, y)
        self.rect.center = self.position.x, self.position.y
        # raise NotImplementedError


class Player(MazeRunner):

    def __init__(self, bitmap_path: str, letters = False) -> None:
        super().__init__(bitmap_path)
        self.up = K_UP
        self.down = K_DOWN
        self.left = K_LEFT
        self.right = K_RIGHT
        if letters:
            self.up = K_w
            self.down = K_s
            self.right = K_d
            self.left = K_a

    def set_starting_position(self, cell_size):
        x = cell_size[0]/2
        y = cell_size[1]/2
        self.position = Vector2(x, y)
        self.rect.center = self.position.x, self.position.y

    # Move the sprite based on keypresses
    def vertical_move(self, pressed_keys, velocity=1):
        # velocity = self.velocity * velocity
        if pressed_keys[self.up]:
            self.rect.move_ip(0, -velocity)
        if pressed_keys[self.down]:
            self.rect.move_ip(0, velocity)

    # Move the sprite based on keypresses
    def horizontal_move(self, pressed_keys, velocity=1):
        # velocity = self.velocity * velocity
        if pressed_keys[self.left]:
            self.rect.move_ip(-velocity, 0)
        if pressed_keys[self.right]:
            self.rect.move_ip(velocity, 0)

    def check_borders_collisions(self, borders):
        if borders:=pygame.sprite.spritecollide(
                self, 
                borders, 
                False, 
                pygame.sprite.collide_rect
            ):
            return pygame.sprite.spritecollide(
                    self, 
                    borders, 
                    False, 
                    pygame.sprite.collide_mask
            )

    def move(self, pressed_keys, borders):
        velocity = self.compute_velocity(pressed_keys)
        self.horizontal_move(pressed_keys, velocity[0])
        if self.check_borders_collisions(borders):
            self.horizontal_block(pressed_keys, velocity[0])
        self.vertical_move(pressed_keys, velocity[1])
        if self.check_borders_collisions(borders):
            self.vertical_block(pressed_keys, velocity[1])

    def compute_velocity(self, pressed_keys):
        # absolute_v = self.velocity * absolute_v
        is_vertical = (pressed_keys[self.up] or pressed_keys[self.down])
        is_horizontal = (pressed_keys[self.left] or pressed_keys[self.right])
        if is_horizontal and is_vertical:
            # velocity = self.speed_x / sqrt(2), self.speed_y / sqrt(2)
            velocity = self.speed_x/sqrt(2), self.speed_y/sqrt(2)
        else:
            velocity = is_horizontal*self.speed_x, is_vertical*self.speed_y
        # d = (sqrt(2)/absolute_v)
        # velocity = is_horizontal/d, is_vertical/d
        return velocity

    def vertical_block(self, pressed_keys, velocity=1):
        # velocity = self.velocity * velocity
        if pressed_keys[self.up]:
            self.rect.move_ip(0, velocity)
        if pressed_keys[self.down]:
            self.rect.move_ip(0, -velocity)

    def horizontal_block(self, pressed_keys, velocity=1):
        # velocity = self.velocity * velocity
        if pressed_keys[self.left]:
            self.rect.move_ip(velocity, 0)
        if pressed_keys[self.right]:
            self.rect.move_ip(-velocity, 0)


class Badman(MazeRunner):

    def __init__(self, bitmap_path: str) -> None:
        super().__init__(bitmap_path)
        self.rect.center = (0,0)
        self.is_waiting_for_target = True
        self.target = None
        self.direction = None

    def set_starting_position(self, cell_size):
        x = cell_size[0]*(self.starting_coordinates[0] + 0.5)
        y = cell_size[1]*(self.starting_coordinates[1] + 0.5)
        self.position = Vector2(x, y)
        self.rect.center = self.position.x, self.position.y

    def move(self):
        dx = self.target[0] - self.rect.center[0]
        dy = self.target[1] - self.rect.center[1]
        distance = (dx**2 + dy**2)**0.5
        if distance > max(self.speed_x, self.speed_y):
            # Calculate the movement vector
            move_x = (dx / distance) * self.speed_x*0.9
            move_y = (dy / distance) * self.speed_y*0.9
            # Update the position
            self.rect.move_ip(move_x, move_y)
        else:
            # If the distance is less than the speed, move directly to the target
            self.rect.center = self.target[0], self.target[1]
            # self.rect.center[0] = self.target[0]
            self.is_waiting_for_target = True

    def update_position_after_resize(self, size: tuple, cell_size):
        super().update_position_after_resize(size, cell_size)
        if self.target:
        # Calculate the new position of the object based on the resize ratio
            x = size[0] * self.target[0] / self.previous_size[0]
            y = size[1] * self.target[1] / self.previous_size[1]
            self.target = x, y
