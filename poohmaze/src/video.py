import pygame
import random

class MazeInterface:

    def __init__(self) -> None:
        self._cells = []

    def cells(self, i, j):
        return self._cells[i][j]

    def init_cells(
            self, 
            maze_width, 
            maze_height,
            columns,
            rows
        ):
        self.cell_width = round(maze_width / columns)
        self.cell_height = round(maze_height / rows)
        for row in range(rows):
            r = []
            for col in range(columns):
                x, y = col*self.cell_width, row*self.cell_height
                cell = Cell(
                    x,
                    y,
                    self.cell_width,
                    self.cell_height
                )
                r.append(cell)
            self._cells.append(r)

    def draw_maze_input(self):
        cells = []
        for row in self._cells:
            for cell in row:
                # (r, g, b) = [random.randint(0, 255) for i in range(3)]
                # cell.surf.fill((r,g,b))
                cells.append((cell.surf, (cell.x, cell.y)))
        return cells
    
class Border(pygame.sprite.Sprite):

    def __init__(self, border, size, coordinates):
        super(Border, self).__init__()
        self.size = size
        self.x, self.y = coordinates
        self.direction = border
        self.surf = pygame.Surface(size=size)
        self.rect = self.surf.get_rect() 
        self.rect.topleft = (self.x, self.y)
        self.mask = pygame.mask.from_surface(self.surf)

    def draw_border(self, surf):
        self.rect.topleft = (self.x, self.y)
        surf.blit(self.surf, self.rect)

class Cell:

    def __init__(self, x, y, width, height) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = (255, 255, 255)
        self.border_colour = (0, 0, 0)
        self.surf = pygame.Surface(size=(width, height))
        self.rect = self.surf.get_rect()
        self.rect.topleft = x, y
        self.surf.fill(self.colour)
        # self.draw_border('t', 5)
        self.borders = {}

    def get_coordinates(self):
        return self.x, self.y

    def prepare_borders(self, borders, border_width):
        output_list = []
        for border in borders:
            if border=='b':
                x = self.x
                y = self.y + self.height - border_width
                size = (self.width, border_width)
            elif border=='t':
                x = self.x
                y = self.y
                size = (self.width, border_width)
            elif border=='l':
                x = self.x
                y = self.y
                size = (border_width, self.height)
            elif border=='r':
                x = self.x + self.width - border_width
                y = self.y 
                size = (border_width, self.height)
            b = Border(
                border=border,
                size=size,
                coordinates=(x, y)
            )
            self.borders[border] = b
            output_list.append(b)
        return output_list









