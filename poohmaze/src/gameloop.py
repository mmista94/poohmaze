


from dataclasses import dataclass
import pygame
from poohmaze.src.main import GameState, PoohMaze


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
            self.handle_event(event)

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
    
class GameLoop(Loop):
    
    def handle_event(self, pressed_keys):
        self.move_player(pressed_keys)
        self.move_npcs()

    def move_player(self, pressed_keys):
        velocity = compute_velocity()
        player = self.poohmaze.game.characters.player
        player.move(pressed_keys, velocity)

        player.horizontal_move(pressed_keys, velocity)
        collisions_horizontal = pygame.sprite.spritecollide(
                player, 
                self.borders_sprites, 
                False, 
                pygame.sprite.collide_mask
        )
        if collisions_horizontal:
            player.horizontal_block(pressed_keys)

