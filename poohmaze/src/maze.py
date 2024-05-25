from __future__ import annotations
import random
from collections import deque

import pygame
from pygame.sprite import _Group

from poohmaze.src.main import Display


def get_opposite_direction(direction) -> str:
    mapper = {
        't':'b',
        'b':'t',
        'r':'l',
        'l':'r'
    }
    return mapper[direction]


def draw_maze(maze: StandardMaze, display: Display):
    size = display.screen.get_size()
    width, height = size
    cell_height = height / maze.rows
    cell_width = width / maze.columns
    cell_size = (cell_width, cell_height)
    for i in range(maze.rows):
        for j in range(maze.columns):
            cell: Cell = maze.grid(i, j)
            borders = cell.logic.get_borders()
            cell.visual.draw_cell()



class Cell:

    def __init__(self) -> None:
        self.logic: CellBackend = CellBackend()
        self.visual: CellFrontend = CellFrontend()

    def __str__(self):
        return str(self.logic.get_borders())
    
class CellBackend:

    def __init__(self) -> None:
        self.borders: dict = {
            't':1,
            'b':1,
            'l':1,
            'r':1
        }
        self.was_traversed: bool = False

    def carve_passage(self, direction) -> None:
        self.borders[direction] = 0

    def get_borders(self):
        return [k for k, v in self.borders.items() if v]
    
    def get_paths(self):
        return [k for k, v in self.borders.items() if not v]


class CellFrontend():
    
    def __init__(self):
        self.colour = (255, 255, 255)

    def draw_cell(self, size, x, y):
        self.size = size
        self.x, self.y = x, y
        self.surf = pygame.Surface(size=size)
        self.surf.fill(self.colour)
        self.rect = self.surf.get_rect() 
        self.rect.topleft = (self.x, self.y)   

    def draw_border(self, borders, border_width):
        self.borders: dict[str, Border] = {}
        for d in borders:
            border_params = self._compute_border_geometry(d, border_width)
            x, y = border_params['coordinates']
            size = border_params['size']
            self.borders[d] = Border(d, size, (x, y))

    def _compute_border_geometry(self, border: str, border_width: float):
        if border=='b':
                x = self.x
                y = self.y + self.size[1] - border_width
                size = (self.size[0], border_width)
        elif border=='t':
            x = self.x
            y = self.y
            size = (self.size[0], border_width)
        elif border=='l':
            x = self.x
            y = self.y
            size = (border_width, self.size[1])
        elif border=='r':
            x = self.x + self.size[0] - border_width
            y = self.y 
            size = (border_width, self.size[1])
        output = {
            'coordinates':(x,y),
            'size':size
        }
        return output


class Border(pygame.sprite.Sprite):

    def __init__(self, border, size, coordinates):
        super().__init__()
        self.size = size
        self.direction = border
        self.surf = pygame.Surface(size=size)
        self.rect = self.surf.get_rect() 
        self.rect.topleft = coordinates
        self.mask = pygame.mask.from_surface(self.surf)


class StandardMaze:

    def __init__(self, rows: int, columns: int) -> None:
        self.rows = rows
        self.columns = columns
        self._grid = [[Cell() for _ in range(columns)] for _ in range(rows)]
        self.generate_maze()
        # self.add_random_passages(int(0.05*self.rows*self.columns))

    def grid(self, row, column) -> Cell:
        return self._grid[row][column]

    def random_location(self):
        return random.randint(0, self.rows-1), random.randint(0, self.columns-1)

    def generate_maze(self):
        location = self.random_location()
        k = 0
        moves = deque()
        moves.append(location)
        # self.grid(*location).was_traversed = True
        while k < self.rows*self.columns:
            # Check if neighboring cells are suitable
            if good_neighbors:=self.check_neighboring_cells(*location):
                location = self._carve_passages(location, good_neighbors)
                moves.append(location)
                k += 1
            else:
                moves.pop()
                location = moves[-1]

    def add_random_passages(self, number_of_passages):
        for _ in range(number_of_passages):
            location = self.random_location()
            good_neighbors = self.check_neighboring_cells(*location, False)
            location = self._carve_passages(location, good_neighbors)


    def cell_offset(self, location, direction):
        if direction=="t":
            offset = -1, 0
        elif direction=='l':
            offset = 0, -1
        elif direction=='r':
            offset = 0, 1
        elif direction=='b':
            offset = 1, 0
        return location[0] + offset[0], location[1] + offset[1]

    def _carve_passages(self, location, good_neighbors) -> tuple:
        direction = random.choice(good_neighbors)
        self.grid(*location).logic.carve_passage(direction)
        adjacent_location = self.cell_offset(location, direction)
        opposite_direction = get_opposite_direction(direction)
        self.grid(*adjacent_location).logic.carve_passage(opposite_direction)
        self.grid(*adjacent_location).logic.was_traversed = True
        return adjacent_location

    def check_neighboring_cells(self, i, j, check_traversed=True):
        adjacent_cells = []
        if i > 0:
            n_cell = self.grid(i-1, j) 
            if (not n_cell.logic.was_traversed or not check_traversed):
                adjacent_cells.append('t')
        if i < self.rows-1:
            n_cell = self.grid(i+1, j)
            if (not n_cell.logic.was_traversed or not check_traversed):
                adjacent_cells.append('b')
        if j > 0:
            n_cell = self.grid(i, j-1)
            if (not n_cell.logic.was_traversed or not check_traversed):
                adjacent_cells.append('l')
        if j < self.columns-1:
            n_cell = self.grid(i, j+1)
            if (not n_cell.logic.was_traversed or not check_traversed):
                adjacent_cells.append('r')
        return adjacent_cells
    
    
def maze_factory(config):
    if config['type']=='standard':
        rows = config['rows']
        columns = config['columns']
        maze = StandardMaze(rows=rows, columns=columns)
        return maze