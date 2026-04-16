import random

class Cell:
    def __init__(self):
        self.mine = False
        self.revealed = False
        self.flag = False
        self.number = 0

def generateGrid(c, r): 
    return [[Cell() for _ in range(c)] for _ in range(r)]

def setMines(grid, totlamines):
    r = len(grid)
    c = len(grid[0])
    placed = 0

    while placed < totlamines:
        newr = random.randint(0, r-1)
        newc = random.randint(0, c-1)
        if not grid[newr][newc].mine:
            grid[newr][newc].mine = True
            placed += 1

def cellExist(grid, r, c):
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])

def restartCell(grid):
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            grid[r][c].number = 0 

def addtocount(grid, r, c):
    if grid[r][c].mine:
        return
    
    directions = [(-1,-1),(-1,0),(-1,1),
                  (0,-1),(0,1),
                  (1,-1),(1,0),(1,1)]

    for dr, dc in directions:
        nr = r + dr
        nc = c + dc

        if cellExist(grid, nr, nc):
            if grid[nr][nc].mine:
                grid[r][c].number += 1

def aroundMines(grid):
    restartCell(grid)

    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if not grid[r][c].mine:
                addtocount(grid, r, c)

# NUEVO: mostrar tablero del jugador
def show_player_grid(grid):
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            cell = grid[r][c]
            if cell.flag:
                print("F", end=" ")
            elif not cell.revealed:
                print("*", end=" ")
            elif cell.mine:
                print("#", end=" ")
            else:
                print(cell.number, end=" ")
        print()

# NUEVO: revelar celda
def reveal(grid, r, c):
    if not cellExist(grid, r, c) or grid[r][c].revealed:
        return True
    
    grid[r][c].revealed = True

    if grid[r][c].mine:
        return False  # PERDISTE

    # si es 0, revelar alrededor automáticamente
    if grid[r][c].number == 0:
        directions = [(-1,-1),(-1,0),(-1,1),
                      (0,-1),(0,1),
                      (1,-1),(1,0),(1,1)]
        for dr, dc in directions:
            reveal(grid, r+dr, c+dc)

    return True

# JUEGO
game = generateGrid(5,5)
setMines(game, 5)
aroundMines(game)

while True:
    show_player_grid(game)
    
    action = input("Acción (r = revelar, f = bandera): ")
    r = int(input("Fila: "))
    c = int(input("Columna: "))

    if action == "r":
        alive = reveal(game, r, c)
        if not alive:
            print("PERDISTE")
            break
    elif action == "f":
        game[r][c].flag = not game[r][c].flag