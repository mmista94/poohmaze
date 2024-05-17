import pygame
from maze import maze_factory
import video
import chars

pygame.init()

maze_config = {
    'rows':10,
    'columns':10
}

SCREEN_LENGTH, SCREEN_WIDTH = 800, 900
# dims = (SCREEN_LENGTH, SCREEN_WIDTH)

class App:

    def __init__(self) -> None:
        #self.init_display(SCREEN_LENGTH, SCREEN_WIDTH)
        self.screen = self.init_display(SCREEN_LENGTH, SCREEN_WIDTH)
        self.maze = Maze(maze_config, 'standard')
        self.all_sprites = pygame.sprite.Group()
        self.borders_sprites = pygame.sprite.Group()
        
        self.run()

    def init_display(self, length, width):
        size = (width, length)
        return pygame.display.set_mode(size)

    def run(self):
        maze_cells = self.maze.graphics.draw_maze_input()
        # self.screen.blits(maze_cells)
        player = chars.Player()
        self.all_sprites.add(player)
        playersize =(
            0.65*SCREEN_LENGTH/maze_config['rows'],
            0.65*SCREEN_WIDTH/maze_config['columns']
        )
        player.scale(playersize)
        for border in self.maze.sprites_borders:
            self.borders_sprites.add(border)
            self.all_sprites.add(border)
        for entity in self.borders_sprites:
            self.screen.blit(entity.surf, entity.rect)
        # self.screen.blit(player.surf, (30,30))
        running = True
        while running:
            # Did the user click the window close button?
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # Get the set of keys pressed and check for user input
            pressed_keys = pygame.key.get_pressed()
            player.update(pressed_keys)
            self.screen.blits(maze_cells)
            for entity in self.all_sprites:
                self.screen.blit(entity.surf, entity.rect)
            # maze_cells = self.maze.graphics.draw_maze_input()
            # self.screen.blits(maze_cells)
            if pygame.sprite.spritecollide(player, self.borders_sprites, False, pygame.sprite.collide_mask):
                # If so, remove the player
                player.kill()
                print('test')
            # pygame.display.update()
            pygame.display.flip()
        
class Maze:

    def __init__(self, maze_config, maze_type='standard') -> None:
        self.maze = maze_factory(maze_type, maze_config)
        self.graphics = video.Maze()
        self.sprites_borders = []
        self.graphics.init_cells(
            SCREEN_WIDTH,
            SCREEN_LENGTH,
            self.maze.columns,
            self.maze.rows
        )
        for i in range(self.maze.rows):
            for j in range(self.maze.columns):
                print(f'cell {i}, {j}', self.maze.grid(i, j))

        for i in range(self.maze.rows):
            for j in range(self.maze.columns):
                print(f'filling cell {i}, {j}')
                borders = self.maze.grid(i, j).get_borders()
                l = self.graphics.cells(i, j).prepare_borders(borders, 7.5)
                for sprite in l:
                    self.sprites_borders.append(sprite)


if __name__=='__main__':
    App()