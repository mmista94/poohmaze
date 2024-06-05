import pygame
from dataclasses import dataclass
from misc import GameState

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import PoohMaze

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


class MazeLoop(Loop):
    
    def handle_event(self, pressed_keys):
        self.display.screen.fill((255, 255, 255))
        self.move_player(pressed_keys)
        for entity in self.game.sprites:
            self.display.screen.blit(entity.surf, entity.rect)
        pygame.display.flip()

    def move_player(self, pressed_keys):
        player = self.game.characters.player
        def collision_detector(x):
            return pygame.sprite.spritecollide(
                    x, 
                    self.game.maze.borders, 
                    False, 
                    pygame.sprite.collide_mask
            )
        if any(pressed_keys):
            player.move(pressed_keys, collision_detector)

    @property
    def game(self):
        return self.poohmaze.game