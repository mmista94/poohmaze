import random
from collections import deque


class Cell:

    def __init__(self) -> None:
        self.borders = [1,1,1,1]
        self.was_traversed: bool = False

    def carve_passage(self, direction) -> None:
        mapper = {
            't':0,
            'b':1,
            'l':2,
            'r':3
        }
        self.borders[mapper[direction]] = 0

    @staticmethod
    def opposite_direction(direction) -> str:
        mapper = {
            't':'b',
            'b':'t',
            'r':'l',
            'l':'r'
        }
        return mapper[direction]
    

class Maze:

    def __init__(self, rows: int, columns: int) -> None:
        self.rows = rows
        self.columns = columns
        self._grid = [[Cell() for _ in range(columns)] for _ in range(rows)]
        self.generate_maze()

    def grid(self, i, j) -> Cell:
        return self._grid[i][j]

    def generate_maze(self):
        location = random.randint(0, self.rows-1), random.randint(0, self.columns-1)
        k = 0
        moves = deque()
        moves.append(location)
        while k < self.rows*self.columns:
            # Check if neighboring cells are suitable
            if good_neighbors:=self.check_neighboring_cells(*location):
                location = self._carve_passages(location, good_neighbors)
                moves.append(location)
                k += 1
            else:
                moves.pop()
                location = moves[-1]

    def cell_offset(self, location, direction):
        if direction=="t":
            offset = 1, 0
        elif direction=='l':
            offset = 0, -1
        elif direction=='r':
            offset = 0, 1
        elif direction=='b':
            offset = -1, 0
        return location[0] + offset[0], location[1] + offset[1]

    def _carve_passages(self, location, good_neighbors) -> tuple:
            direction = random.choice(good_neighbors)
            self.grid(*location).carve_passage(direction)
            adjacent_location = self.cell_offset(location, direction)
            opposite_direction = Cell.opposite_direction(direction)
            self.grid(*adjacent_location).carve_passage(opposite_direction)
            self.grid(*adjacent_location).was_traversed = True
            return adjacent_location
    
    def check_neighboring_cells(self, i, j):
        adjacent_cells = []
        if i > 0:
            n_cell = self.grid(i-1, j) 
            if not n_cell.was_traversed:
                adjacent_cells.append('b')
        if i < self.rows-1:
            n_cell = self.grid(i+1, j)
            if not n_cell.was_traversed:
                adjacent_cells.append('t')
        if j > 0:
            n_cell = self.grid(i, j-1)
            if not n_cell.was_traversed:
                adjacent_cells.append('l')
        if j < self.columns-1:
            n_cell = self.grid(i, j+1)
            if not n_cell.was_traversed:
                adjacent_cells.append('r')
        return adjacent_cells