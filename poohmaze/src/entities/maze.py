from __future__ import annotations

from dataclasses import dataclass, field
import random
from collections import deque
import weakref
import pygame


def get_opposite_direction(direction) -> str:
    mapper = {
        't':'b',
        'b':'t',
        'r':'l',
        'l':'r'
    }
    return mapper[direction]

class CellBackend:

    def __init__(self) -> None:
        self.borders: dict = {
            't':1,
            'b':1,
            'l':1,
            'r':1
        }
        self.borders_created: bool = False

    def carve_passage(self, direction) -> None:
        self.borders[direction] = 0

    def get_borders(self):
        return [k for k, v in self.borders.items() if v]
    
    def get_paths(self):
        return [k for k, v in self.borders.items() if not v]
    
    
class Border(pygame.sprite.Sprite): 

    border_factor = 0.05

    def __init__(self, direction: str, parent: Cell):
        super().__init__()
        self._cell: weakref.ReferenceType[Cell] = weakref.ref(parent)
        self.which_border = direction
        self.surf = pygame.Surface(size=self.size)
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect() 
        self.rect.topleft = self.coordinates
        self.mask = pygame.mask.from_surface(self.surf)
    
    @property
    def coordinates(self):
        border_width = self.border_factor * self._cell().size[0]
        if self.which_border=='b':
            x = self._cell().coordinates[0]
            y = (self._cell().coordinates[1] 
                 + self._cell().size[1] - border_width)
        elif self.which_border=='t':
            x = self._cell().coordinates[0]
            y = self._cell().coordinates[1]
        elif self.which_border=='l':
            x = self._cell().coordinates[0]
            y = self._cell().coordinates[1]
        elif self.which_border=='r':
            x = (self._cell().coordinates[0] + 
                 self._cell().size[0] - border_width)
            y = self._cell().coordinates[1]
        return x, y
    
    @property
    def size(self):
        border_width = self.border_factor * self._cell().size[0]
        if self.which_border=='b':
            size = (self._cell().size[0], border_width)
        elif self.which_border=='t':
            size = (self._cell().size[0], border_width)
        elif self.which_border=='l':
            size = (border_width, self._cell().size[1])
        elif self.which_border=='r':
            size = (border_width, self._cell().size[1])
        return size
    
    def kill(self):
        super().kill()
        self._cell().logic.borders[self.which_border] = 0

    def _update(self):
        if self.which_border in self._cell().logic.get_borders():
            self.surf = pygame.Surface(size=self.size)
            self.rect = self.surf.get_rect() 
            self.rect.topleft = self.coordinates
            self.mask = pygame.mask.from_surface(self.surf)
        else:
            self.kill()
    

class CellFrontend():

    cell_width: float = 0
    cell_height: float = 0

    def __init__(self, parent) -> None:
        self.cell: weakref.ReferenceType[Cell] = weakref.ref(parent)
        self.borders: pygame.sprite.Group[Border] = pygame.sprite.Group()
        self.init_borders()

    @property
    def size(self):
        return self.cell_width, self.cell_height
    
    @property
    def coordinates(self):
        return self.cell().coordinates

    def update(self):
        for border in self.borders: 
            border._update()

    def init_borders(self):
        for d in self.cell().logic.get_borders():
            self.borders.add(Border(d, self.cell()))


@dataclass
class Cell:

    row: int
    column: int
    logic: CellBackend = field(init=False, default_factory=CellBackend)
    visual: CellFrontend = field(init=False)

    def __post_init__(self):
        self.visual = CellFrontend(self)

    def update_video(self):
        self.visual.update()

    @property
    def size(self):
        return CellFrontend.cell_width, CellFrontend.cell_height
    
    @property
    def coordinates(self):
        x = self.column * CellFrontend.cell_width
        y = self.row * CellFrontend.cell_height
        return x, y
    

# Define the strategy interface
class MazeGenerationStrategy:
    def generate(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    

class StandardMaze(MazeGenerationStrategy):

    @classmethod
    def generate(cls, maze: Maze):
        location = maze.random_location()
        cell = maze.grid(*location)
        k = 0
        moves = deque()
        moves.append(cell)
        cell.logic.borders_created = True
        while k < (maze.rows * maze.columns - 1):
            # Check if neighboring cells are suitable
            if good_neighbors:=cls.check_neighboring_cells(maze, cell):
                cell = cls._carve_passages(maze, cell, good_neighbors)
                moves.append(cell)
                k += 1
            else:
                moves.pop()
                cell = moves[-1]
        cls.add_random_passages(maze, int(0.1*maze.rows*maze.columns))

    @classmethod
    def add_random_passages(cls, maze: Maze, number_of_passages):
        for _ in range(number_of_passages):
            location = maze.random_location()
            cell = maze.grid(*location)
            good_neighbors = cls.check_neighboring_cells(maze, cell, False)
            cls._carve_passages(maze, cell, good_neighbors)

    @staticmethod
    def _carve_passages(
            maze: Maze, 
            cell: Cell,
            good_neighbors: list[str]
        ) -> Cell:
        # direction should be: 't', 'b', 'l', 'r'
        direction = random.choice(good_neighbors)
        cell.logic.carve_passage(direction)
        # maze.grid(*location).logic.carve_passage(direction)
        adjacent_cell = maze.adjacent_cell(cell, direction)
        opposite_direction = get_opposite_direction(direction)
        adjacent_cell.logic.carve_passage(opposite_direction)
        adjacent_cell.logic.borders_created = True
        return adjacent_cell

    @staticmethod
    def check_neighboring_cells(
        maze: Maze, 
        cell: Cell, 
        check_traversed=True
    ) -> list[str]:
        adjacent_cells = []
        if cell.row > 0:
            n_cell = maze.adjacent_cell(cell, 't')
            if (not n_cell.logic.borders_created or not check_traversed):
                adjacent_cells.append('t')
        if cell.row < maze.rows-1:
            n_cell = maze.adjacent_cell(cell, 'b')
            if (not n_cell.logic.borders_created or not check_traversed):
                adjacent_cells.append('b')
        if cell.column > 0:
            n_cell = maze.adjacent_cell(cell, 'l')
            if (not n_cell.logic.borders_created or not check_traversed):
                adjacent_cells.append('l')
        if cell.column < maze.columns-1:
            n_cell = maze.adjacent_cell(cell, 'r')
            if (not n_cell.logic.borders_created or not check_traversed):
                adjacent_cells.append('r')
        return adjacent_cells
    

class Maze:

    def __init__(self, rows: int, columns: int, strategy: str) -> None:
        self.rows = rows
        self.columns = columns
        self._grid = [[Cell(j, i) for i in range(columns)] for j in range(rows)]
        self.borders = pygame.sprite.Group()
        self.set_generation_strategy(strategy)

    # ####### Video: ####################################

    def update_video(self, size: tuple[float, float]):
        self._update_cell_dimensions(size)
        for row in self._grid:
            for cell in row:
                cell.update_video()

    def _update_cell_dimensions(self, size: tuple[float, float]):
        cell_width = size[0] / self.columns
        cell_height = size[1] / self.rows
        CellFrontend.cell_height = cell_height
        CellFrontend.cell_width = cell_width

    @property
    def cell_dimensions(self):
        return CellFrontend.cell_width, CellFrontend.cell_height

    # ####### Logic: ####################################

    def set_generation_strategy(self, strategy: str=None):
        if not strategy or strategy=='standard':
            self.generation_strategy = StandardMaze()

    def generate(self):
        if self.generation_strategy:
            self.generation_strategy.generate(self)
        else:
            raise ValueError("Generation strategy not set")   
        self.collect_borders()
    
    def reset(self):
        self._grid = [
            [Cell(j, i) for i in range(self.columns)] for j in range(self.rows)
        ]
        self.borders = pygame.sprite.Group()
    
    def grid(self, row, column) -> Cell:
        return self._grid[row][column]

    def random_location(self):
        return random.randint(0, self.rows-1), random.randint(0, self.columns-1)

    def adjacent_cell(self, cell: Cell, direction: str) -> Cell:
        if direction=="t":
            offset = -1, 0
        elif direction=='l':
            offset = 0, -1
        elif direction=='r':
            offset = 0, 1
        elif direction=='b':
            offset = 1, 0
        adjacent_cell = self.grid(
            cell.row + offset[0],
            cell.column + offset[1]
        )
        return adjacent_cell        

    def collect_borders(self):
        for row in self._grid:
            for cell in row:
                self.borders.add(cell.visual.borders.sprites())
    

def maze_factory(config):
    rows = config.getint('rows')
    columns = config.getint('columns')
    if config['type']=='standard':
        strategy = config['type']
    maze = Maze(rows, columns, strategy)
    return maze