from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
import enum
import os
import pygame
# from maze import Maze
# from loops import GameLoop
from characters import Characters
from maze import maze_factory, Maze
# from maze import Maze, maze_factory

def start_game():
    game = PoohMaze.start()

class GameState(enum.Enum):
    """
    Enum for the Game's State Machine. Every state represents a
    known game state for the game engine.
    """

    # Unknown state, indicating possible error or misconfiguration.
    unknown = "unknown"
    starting = "starting"
    initializing_maze = "initializing_maze"
    display_initialized = "display_initialized"
    initialized = "initialized"
    game_playing = "game_playing"
    game_ended = "game_ended"
    quitting = "quitting"
    

class StateError(Exception):
    """
    Raised if the game is in an unexpected game state at a point
    where we expect it to be in a different state. For instance, to
    start the game loop we must be initialized.
    """

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
        pressed_keys = pygame.key.get_pressed()
        self.handle_event(pressed_keys)

    def loop(self):
        while self.state != GameState.quitting:
            self.handle_events()
            

    def handle_event(self, event):
        """
        Handles a singular event, `event`.
        """

    # Convenient shortcuts.
    def set_state(self, new_state):
        self.poohmaze.set_state(new_state)

    @property
    def screen(self):
        return self.poohmaze.display

    @property
    def state(self):
        return self.poohmaze.state


@dataclass
class Display:

    screen: pygame.Surface
    screen_rect: pygame.Rect
    fullscreen: bool

    @classmethod
    def create(cls, screenrect, fullscreen=False):
        screen = cls(
            screen=None,
            screen_rect=screenrect,
            fullscreen=fullscreen,
        )
        return screen
    
@dataclass
class Game:

    maze: Maze
    characters: Characters
    loop: GameLoop
    # all_sprites = pygame.sprite.Group()
    # all_sprites = pygame.sprite.Group()
    # borders_sprites = pygame.sprite.Group()
    # enemies_sprites = pygame.sprite.Group()

    @classmethod
    def create(cls, maze_config, display, engine):
        # maze = Maze.create(maze_config, display)
        maze = maze_factory(maze_config)
        characters = Characters.generate_characters()
        game = cls(
            maze=maze,
            characters=characters,
            loop = GameLoop(engine)
        )
        game.maze.update_video(display)
        return game
    
@dataclass
class PoohMaze:

    display: Display
    game: Game
    config: ConfigParser
    state: GameState

    @classmethod
    def start(cls):  
        pygame.init()
        game = cls(
            display=None,
            game=None,
            config=None,
            state=GameState.starting
        )
        game.init_config()
        game.init_display()
        game.init_game_backend(game.config['maze_config'])
        game.loop()
        return game

    def init_config(self):
        self.assert_state_is(GameState.starting)
        self.config = ConfigParser()
        cd = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(cd, '../settings.ini'))
        self.config.read(path)

    def init_display(self):  
        self.assert_state_is(GameState.starting)
        window_config = self.config['display_window']
        #######################################
        width = int(window_config['screen_width'])
        height = int(window_config['screen_height'])
        start_fullscreen = window_config.getboolean('start_fullscreen')
        #######################################
        rect = pygame.Rect(0, 0, width, height)
        self.display = Display.create(rect, start_fullscreen)
        window_style = pygame.FULLSCREEN if self.display.fullscreen else 0
        self.display.screen = pygame.display.set_mode(rect.size, window_style)
        self.display.screen.fill((255, 255, 255))
        self.set_state(GameState.display_initialized)

    def init_game_backend(self, maze_config=None):
        self.assert_state_is(GameState.display_initialized)
        self.game = Game.create(maze_config, self.display, self)
        # self.set_state(GameState.initialized)
        self.set_state(GameState.game_playing)
    
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

    def loop(self, ):
        while self.state != GameState.quitting:
            if self.state == GameState.game_playing:
                self.game.loop.loop()
        #self.quit()


class GameLoop(Loop):
    
    def handle_event(self, pressed_keys):
        self.move_player(pressed_keys)
        display = self.poohmaze.display
        display.screen.blit(display.screen, display.screen_rect)
        self.poohmaze.game.maze.borders = pygame.sprite.Group()
        self.poohmaze.game.maze.collect_borders()
        self.poohmaze.game.maze.update_cell_dimensions(display)
        self.poohmaze.game.maze.blit(display)
        pygame.display.flip()
        # self.move_npcs()

    def move_player(self, pressed_keys):
        player = self.poohmaze.game.characters.player
        def collision_detector(x):
            return pygame.sprite.spritecollide(
                    x, 
                    self.poohmaze.game.maze.borders, 
                    False, 
                    pygame.sprite.collide_mask
            )
        player.move(pressed_keys, collision_detector)

if __name__=='__main__':
    start_game()