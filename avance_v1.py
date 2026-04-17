import tkinter as tk
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

def reveal(grid, r, c):
    if not cellExist(grid, r, c) or grid[r][c].revealed:
        return True
    
    grid[r][c].revealed = True

    if grid[r][c].mine:
        return False

    if grid[r][c].number == 0:
        directions = [(-1,-1),(-1,0),(-1,1),
                      (0,-1),(0,1),
                      (1,-1),(1,0),(1,1)]
        for dr, dc in directions:
            reveal(grid, r+dr, c+dc)

    return True

# intrefaz
root = tk.Tk()
root.title("Buscaminas")

grid = generateGrid(5,5)
setMines(grid, 5)
aroundMines(grid)

buttons = []

def update_buttons():
    for r in range(5):
        for c in range(5):
            cell = grid[r][c]
            btn = buttons[r][c]

            if cell.flag:
                btn.config(text="F")
            elif not cell.revealed:
                btn.config(text="")
            elif cell.mine:
                btn.config(text="💣")
            else:
                btn.config(text=str(cell.number))

def click_left(r, c):
    alive = reveal(grid, r, c)
    update_buttons()
    if not alive:
        print("PERDISTE")

def click_right(event, r, c):
    grid[r][c].flag = not grid[r][c].flag
    update_buttons()

# crear botones
for r in range(5):
    row = []
    for c in range(5):
        btn = tk.Button(root, width=4, height=2,
                        command=lambda r=r, c=c: click_left(r, c))
        btn.grid(row=r, column=c)

        btn.bind("<Button-3>", lambda e, r=r, c=c: click_right(e, r, c))

        row.append(btn)
    buttons.append(row)

root.mainloop()