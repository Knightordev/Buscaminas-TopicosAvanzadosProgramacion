import random


class Cell:
    def __init__(self):
        self.mine = False
        self.revealed = False
        self.flag = False
        self.number = 0

class Game:
    def __init__(self, r, c, mines):
        self.r = r
        self.c = c
        self.mines = mines
        self.grid = self.create_grid()
        self.place_mines()
        self.calculate_numbers()

    def create_grid(self):
        return [[Cell() for _ in range(self.c)] for _ in range(self.r)]
    
    def get_grid(self):
        return self.grid
    
    def place_mines(self):
        placed = 0

        while placed < self.mines:
            r = random.randint(0, self.r - 1)
            c = random.randint(0, self.c - 1)

            if not self.grid[r][c].mine:
                self.grid[r][c].mine = True
                placed += 1

    def in_bounds(self, r, c):
        return 0 <= r < self.r and 0 <= c < self.c
    
    def count_mines_around(self, r, c):
        count = 0
        directions = [
            ( -1, -1), ( -1, 0), ( -1, 1),
            ( 0, -1), ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)
        ]
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc

            if self.in_bounds( nr, nc):
                if self.grid[nr][nc].mine:
                    count += 1
        return count
    
    def calculate_numbers(self):
        for r in range(self.r):
            for c in range(self.c):
                if not self.grid[r][c].mine:
                    self.grid[r][c].number = self.count_mines_around(r, c)

    def toggle_flag(self, r, c):
        if self.in_bounds(r, c) and not self.grid[r][c].revealed:
            self.grid[r][c].flag = not self.grid[r][c].flag
            return self.grid[r][c].flag
        return None

    def reveal(self, r, c):
        if not self.in_bounds(r, c):
            return None

        first_cell = self.grid[r][c]
        if first_cell.revealed or first_cell.flag:
            return None

        revealed_cells = []
        stack = [(r, c)]

        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        while stack:
            current_r, current_c = stack.pop()
            current_cell = self.grid[current_r][current_c]

            if current_cell.revealed or current_cell.flag:
                continue

            current_cell.revealed = True
            revealed_cells.append({
                'row': current_r,
                'col': current_c,
                'mine': current_cell.mine,
                'number': current_cell.number
            })

            if not current_cell.mine and current_cell.number == 0:
                for dr, dc in directions:
                    nr = current_r + dr
                    nc = current_c + dc

                    if self.in_bounds(nr, nc):
                        neighbor = self.grid[nr][nc]
                        if not neighbor.revealed and not neighbor.flag:
                            stack.append((nr, nc))

        return revealed_cells
