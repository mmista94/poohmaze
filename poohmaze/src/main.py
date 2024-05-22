from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
import os
import random
import pygame
from maze import StandardMaze, maze_factory, get_opposite_direction
import video
from characters import Characters

def start_game(fullscreen=False):
    App.start(fullscreen)


@dataclass
class App:

    display: Display
    game: Game
    config: ConfigParser

    @classmethod
    def start(cls, fullscreen):  
        pygame.init()
        game = cls(
            display=None,
            game=None,
            config=None
        )
        game.init_config()
        game.init_display(fullscreen)
        game.init_game_backend()
        return game

    def init_config(self):
        self.config = ConfigParser()
        cd = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(cd, '../settings.ini'))
        self.config.read(path)

    def init_display(self, fullscreen=False):
        window_config = self.config['display_window']
        width = int(window_config['screen_width'])
        height = int(window_config['screen_height'])
        rect = pygame.Rect(0, 0, width, height)
        self.display = Display.create(rect, fullscreen)
        window_style = pygame.FULLSCREEN if self.display.fullscreen else 0
        self.display.screen = pygame.display.set_mode(rect.size, window_style)

    def init_game_backend(self, maze_config=None):
        # Game.create(maze_config, characters_config, self.screen)
        running = True
        while running:
            # Did the user click the window close button?
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

    def loop(self):
        return

#     def run(self):
#         maze_cells = self.maze.graphics.draw_maze_input()
#         c = self.maze.graphics.cells(0, 0)
#         # self.screen.blits(maze_cells)
#         player = characters.Player()
#         badman = characters.Badman((2,2))
#         self.all_sprites.add(player)
#         self.enemies_sprites.add(badman)
#         self.all_sprites.add(badman)
#         playersize =(
#             0.65*SCREEN_LENGTH/maze_config['rows'],
#             0.65*SCREEN_WIDTH/maze_config['columns']
#         )
#         badmansize = (
#             SCREEN_LENGTH/maze_config['rows'],
#             SCREEN_WIDTH/maze_config['columns']
#         )
#         # badman.movement_coordinates = (2, 3)
#         player.scale(playersize)
#         badman.scale(badmansize)
#         w = c.width/2    
#         h = c.height/2
#         player.rect.center = (w, h)
#         badman.rect.center = (5*w, 5*h)
#         for border in self.maze.sprites_borders:
#             self.borders_sprites.add(border)
#             self.all_sprites.add(border)
#         for entity in self.borders_sprites:
#             self.screen.blit(entity.surf, entity.rect)
#         # self.screen.blit(player.surf, (30,30))
#         running = True
#         while running:
#             # Did the user click the window close button?
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     running = False
#             # Get the set of keys pressed and check for user input
#             pressed_keys = pygame.key.get_pressed()
#             player.horizontal_move(pressed_keys)
#             self.move_badmans(badman)
#             self.screen.blits(maze_cells)
#             for entity in self.all_sprites:
#                 self.screen.blit(entity.surf, entity.rect)
#             # maze_cells = self.maze.graphics.draw_maze_input()
#             # self.screen.blits(maze_cells)
#             collisions_horizontal = pygame.sprite.spritecollide(
#                 player, 
#                 self.borders_sprites, 
#                 False, 
#                 pygame.sprite.collide_mask
#             )
#             # if pygame.sprite.spritecollide(
#             #     player, 
#             #     self.enemies_sprites, 
#             #     False, 
#             #     pygame.sprite.collide_mask
#             # ):
#             #     badman.kill()
#             if collisions_horizontal:
#                 # If so, remove the player
#                 player.horizontal_block(pressed_keys)
            
#             player.vertical_move(pressed_keys)
#             for entity in self.all_sprites:
#                 self.screen.blit(entity.surf, entity.rect)
#             collisions_vertical = pygame.sprite.spritecollide(
#                 player, 
#                 self.borders_sprites, 
#                 False, 
#                 pygame.sprite.collide_mask
#             )
#             if collisions_vertical:
#                 # If so, remove the player
#                 player.vertical_block(pressed_keys)
#             # pygame.display.update()
#             pygame.display.flip()

#     def move_badmans(self, badman):
#         if not badman.is_moving:
#             i_b, j_b = badman.maze_coordinates
#             current_cell = self.maze.maze.grid(i_b, j_b)
#             paths = current_cell.get_paths()
#             if not badman.opposite_direction:
#                 path = random.choice(paths)
#             else:  
#                 if random.random() < 0.9 and len(paths) > 1:
#                     paths.remove(badman.opposite_direction)
#                 path = random.choice(paths)
#             badman.opposite_direction = get_opposite_direction(path)
#             badman.direction = path
#             badman.maze_coordinates = self.maze.maze.cell_offset(badman.maze_coordinates, path)
#             i_b, j_b = badman.maze_coordinates
#             badman.target = self.maze.graphics.cells(i_b, j_b).rect.center
#             badman.is_moving = True
#         else:
#             x, y = badman.rect.center
#             # print(f'Wartość x_dist: {x - badman.target[0]}')
#             # print(f'Wartość y_dist: {y - badman.target[1]}')
#             if (abs(x - badman.target[0]) < 1 and abs(y - badman.target[1])<1):
#                 i_b, j_b = badman.maze_coordinates
#                 cell = self.maze.graphics.cells(i_b, j_b)
#                 badman.rect.center = cell.rect.center
#                 badman.is_moving = False
#             else:
#                 badman.move()
        
# class MazeBackend:

#     def __init__(self, maze_config, maze_type='standard') -> None:
#         self.maze = maze_factory(maze_type, maze_config)
#         self.graphics = video.Maze()
#         self.sprites_borders = []
#         self.graphics.init_cells(
#             SCREEN_WIDTH,
#             SCREEN_LENGTH,
#             self.maze.columns,
#             self.maze.rows
#         )
#         for i in range(self.maze.rows):
#             for j in range(self.maze.columns):
#                 borders = self.maze.grid(i, j).get_borders()
#                 l = self.graphics.cells(i, j).prepare_borders(borders, 7.5)
#                 for sprite in l:
#                     self.sprites_borders.append(sprite)


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

    maze: StandardMaze
    characters: Characters
    # all_sprites = pygame.sprite.Group()
    # all_sprites = pygame.sprite.Group()
    # borders_sprites = pygame.sprite.Group()
    # enemies_sprites = pygame.sprite.Group()

    @classmethod
    def create(cls, maze_config, display):
        maze = maze_factory(maze_config)
        characters = Characters.generate_characters()
        game = cls(
            maze=maze,
            characters=characters
        )
        return game


if __name__=='__main__':
    start_game(True)