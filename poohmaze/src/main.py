from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass, field
import enum
import os
import pygame
from characters import Characters
from maze import CellFrontend, maze_factory, Maze

def start_game():
    app = PoohMaze.create()
    app.start()

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
    gameplay = "gameplay"
    resizing = "resizing"
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
            if event.type == pygame.WINDOWRESIZED:
                self.set_state(GameState.resizing)
        pressed_keys = pygame.key.get_pressed()
        self.handle_event(pressed_keys)

    def loop(self):
        while self.state != GameState.quitting:
            if self.state == GameState.resizing:
                size = self.display.screen.get_size()
                self.display.resize(size)
                self.poohmaze.game.maze.update_video(
                    self.display.screen.get_size()
                )  
                self.display.screen.fill((255, 255, 255))
                self.set_state(GameState.gameplay)
            self.handle_events()
            

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
    
    def resize(self, size):
        self.rect = pygame.Rect(0, 0, size[0], size[1])  
        window_style = pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE
        self.screen = pygame.display.set_mode(size, window_style)
        pygame.display.update()
    
@dataclass
class Game:

    maze: Maze
    characters: Characters
    gameloop: MazeLoop
    sprites: pygame.sprite.Group = field(init=False, default_factory=pygame.sprite.Group)

    @classmethod
    def create(cls, maze_config, engine):
        maze = maze_factory(maze_config)
        characters = Characters.generate_characters()
        game = cls(
            maze=maze,
            characters=characters,
            gameloop = MazeLoop(engine)
        )
        game.maze.generate()
        game.collect_sprites()
        return game
    
    def collect_sprites(self):
        self.sprites.add(self.maze.borders.sprites())
        self.sprites.add(self.characters.all_chars.sprites())
    
    def loop(self):
        self.gameloop.loop()
    
@dataclass
class PoohMaze:

    display: Display
    game: Game
    config: ConfigParser
    state: GameState

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
        poohmaze.update_size()
        return poohmaze
    
    def start(self):
        self.loop()

    def update_size(self):
        self.game.maze.update_video(
            self.display.screen.get_size()
        )
        cell_size = self.game.maze.cell_dimensions
        for entity in self.game.characters.all_chars:
            entity.scale(cell_size)

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
        window_style = pygame.FULLSCREEN if self.display.fullscreen else pygame.RESIZABLE
        self.display.screen = pygame.display.set_mode(rect.size, window_style)
        self.display.screen.fill((255, 255, 255))
        # pygame.display.flip()
        self.set_state(GameState.display_initialized)

    def init_game_backend(self, maze_config=None):
        self.assert_state_is(GameState.display_initialized)
        self.game = Game.create(maze_config, self)
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

    def loop(self):
        self.game.loop()


class MazeLoop(Loop):
    
    def handle_event(self, pressed_keys):
        self.display.screen.fill((255, 255, 255))
        self.move_player(pressed_keys)
        for entity in self.game.sprites:
            self.display.screen.blit(entity.surf, entity.rect)
        pygame.display.flip()

    def move_player(self, pressed_keys):
        player = self.poohmaze.game.characters.player
        def collision_detector(x):
            return pygame.sprite.spritecollide(
                    x, 
                    self.poohmaze.game.maze.borders, 
                    False, 
                    pygame.sprite.collide_mask
            )
        if any(pressed_keys):
            player.move(pressed_keys, collision_detector)

    @property
    def game(self):
        return self.poohmaze.game

if __name__=='__main__':
    start_game()