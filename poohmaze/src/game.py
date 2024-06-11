from __future__ import annotations
import random

import pygame 
from configparser import ConfigParser
from dataclasses import dataclass, field
import os
from objects import Characters, Maze, maze_factory
from misc import GameState, StateError

from objects.characters import DESIRED_FPS
from objects.maze import get_opposite_direction


# DESIRED_FPS = 60

@dataclass
class Display:

    screen: pygame.Surface
    screen_rect: pygame.Rect
    fullscreen: bool

    def __post_init__(self):
        window_style = pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE
        self.screen = pygame.display.set_mode(
            self.screen_rect.size, 
            window_style
        )
        self.screen.fill((255, 255, 255))

    @classmethod
    def create(cls, screenrect, fullscreen=False):
        screen = cls(
            screen=None,
            screen_rect=screenrect,
            fullscreen=fullscreen,
        )
        return screen
    
    def resize(self):
        size = self.screen.get_size()
        self.rect = pygame.Rect(0, 0, size[0], size[1])  
        window_style = pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE
        self.screen = pygame.display.set_mode(size, window_style)
        pygame.display.update()


@dataclass
class Game:

    maze: Maze
    characters: Characters
    sprites: pygame.sprite.Group = field(init=False, 
                                         default_factory=pygame.sprite.Group)

    @classmethod
    def create(cls, maze_config, size):
        maze = maze_factory(maze_config)
        maze.generate()
        # maze.update_video(size)
        # cell_size = maze.cell_dimensions
        characters = Characters.generate_characters(maze)
        game = cls(
            maze=maze,
            characters=characters
        )
        game._collect_sprites()
        game.update_geometry(size)
        return game
    
    def _collect_sprites(self):
        self.sprites.add(self.maze.borders.sprites())
        self.sprites.add(self.characters.all_chars.sprites())

    def update_geometry(self, size):
        self.maze.update_video(size)
        cell_size = self.maze.cell_dimensions
        for entity in self.characters.all_chars:
            entity.update_geometry(size, cell_size)
            entity.previous_size = size


@dataclass
class Loop:
    poohmaze: PoohMaze

    def handle_events(self):
        """
        Sample event handler that ensures quit events and normal
        event loop processing takes place. Without this, the game will
        hang, and repaints by the operating system will not happen,
        causing the game window to hang.
        """
        for event in pygame.event.get():
            if (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ) or event.type == pygame.QUIT:
                self.set_state(GameState.quitting)
            # Delegate the event to a sub-event handler `handle_event`
            if event.type == pygame.WINDOWRESIZED:
                self.display.resize()
                self.poohmaze.update_game_geometry()
        self.handle_event()

    def loop(self):
        clock = pygame.time.Clock()
        while self.state != GameState.quitting: 
            pygame.display.set_caption(f"FPS {round(clock.get_fps())}")
            if self.state == GameState.gameplay:
                if not isinstance(self.poohmaze.gameloop, MazeLoop):
                    self.poohmaze.gameloop = MazeLoop(self.poohmaze)
            self.poohmaze.gameloop.handle_events()
            clock.tick(DESIRED_FPS)
            

    def handle_event(self, event):
        """
        Handles a singular event, `event`.
        """

    # Convenient shortcuts.
    def set_state(self, new_state):
        self.poohmaze.set_state(new_state)

    @property
    def display(self):
        return self.poohmaze.display

    @property
    def state(self):
        return self.poohmaze.state


class MazeLoop(Loop):
    
    def handle_event(self):
        self.display.screen.fill((255, 255, 255))
        self.move_player()
        self.move_badmans()
        for entity in self.game.sprites:
            self.display.screen.blit(entity.surf, entity.rect)
        pygame.display.flip()

    def move_player(self):
        player = self.game.characters.player
        borders = self.game.maze.borders
        pressed_keys = pygame.key.get_pressed()
        if any(pressed_keys):
            player.move(pressed_keys, borders)
        pygame.sprite.spritecollide(
            player,
            self.game.characters.targets,
            True,
            pygame.sprite.collide_mask
        )


    def move_badmans(self):
        for enemy in self.game.characters.enemies:
            if enemy.is_waiting_for_target:
                position = enemy.rect.center
                row_column = self.game.maze.point_to_cell(position)
                current_cell = self.game.maze.grid(*row_column)
                paths = current_cell.logic.get_paths()
                if enemy.direction:
                    if (o_d:=get_opposite_direction(enemy.direction)) in paths:
                        if len(paths) > 1:
                            random_number = random.uniform(0, 1)
                            if random_number < 0.9:
                                paths.remove(o_d)
                dir = random.choice(paths)
                enemy.direction = dir
                new_cell = self.game.maze.adjacent_cell(current_cell, dir)
                enemy.target = new_cell.visual.get_center()
                enemy.is_waiting_for_target = False
            else:
                enemy.move() 
            pygame.sprite.spritecollide(
                enemy,
                self.game.characters.players,
                True,
                pygame.sprite.collide_mask
            )

    @property
    def game(self):
        return self.poohmaze.game


@dataclass
class PoohMaze:

    display: Display
    game: Game
    config: ConfigParser
    state: GameState
    gameloop: Loop = field(init=False)

    def __post_init__(self):
        self.gameloop = Loop(self)

    @classmethod
    def create(cls):  
        pygame.init()
        poohmaze = cls(
            display=None,
            game=None,
            config=None,
            state=GameState.starting
        )
        poohmaze.init_config()
        poohmaze.init_display()
        poohmaze.init_game_backend(
            poohmaze.config['maze_config']
        )
        poohmaze.update_game_geometry()
        return poohmaze
    
    def start(self): 
        self.gameloop = Loop(self)
        self.gameloop.loop()

    def update_game_geometry(self):
        size = self.display.screen.get_size()
        self.game.update_geometry(size)

    def init_config(self):
        self.assert_state_is(GameState.starting)
        self.config = ConfigParser()
        cd = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(cd, '../settings.ini'))
        self.config.read(path)

    def init_display(self):  
        self.assert_state_is(GameState.starting)
        window_config = self.config['display_window']
        width = window_config.getint('screen_width')
        height = window_config.getint('screen_height')
        start_fullscreen = window_config.getboolean('start_fullscreen')
        rect = pygame.Rect(0, 0, width, height)
        self.display = Display.create(rect, start_fullscreen)
        self.set_state(GameState.display_initialized)

    def init_game_backend(self, maze_config=None):
        self.assert_state_is(GameState.display_initialized)
        # self.game = Game.create(maze_config, self)
        self.game = Game.create(maze_config, self.display.screen.get_size())
        self.set_state(GameState.gameplay)
    
    def set_state(self, new_state):
        self.state = new_state

    def assert_state_is(self, *expected_states: GameState):
        """
        Asserts that the game engine is one of
        `expected_states`. If that assertions fails, raise
        `StateError`.
        """
        if not self.state in expected_states:
            raise StateError(
                f"Expected the game state to be one of {expected_states} not {self.state}"
            )