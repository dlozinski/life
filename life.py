#!/usr/bin/env python3

# Author: Damian Lozinski <lozinski.d@gmail.com>
# Licence: GPLv3

import random
import tkinter as tk


class Game:
    CELL_ALIVE = 1
    CELL_DEAD = 0

    def __init__(self, rows, cols):
        self._rows = rows
        self._cols = cols
        self.state = [[Game.CELL_DEAD] * self._cols for _ in range(self._rows)]
        self._next_state = [[Game.CELL_DEAD] * self._cols for _ in range(self._rows)]

    def reset(self):
        for i in range(self._rows):
            for j in range(self._cols):
                self.state[i][j] = Game.CELL_DEAD

    def random(self):
        for i in range(self._rows):
            for j in range(self._cols):
                self.state[i][j] = random.randint(0, 1)

    def glider(self):
        self.reset()
        x, y = self._rows // 2 + 1, self._cols // 2 + 1
        self.state[x    ][y - 1] = Game.CELL_ALIVE
        self.state[x + 1][y    ] = Game.CELL_ALIVE
        self.state[x - 1][y + 1] = Game.CELL_ALIVE
        self.state[x    ][y + 1] = Game.CELL_ALIVE
        self.state[x + 1][y + 1] = Game.CELL_ALIVE

    def tick(self):
        for i in range(self._rows):
            for j in range(self._cols):
                self._next_state[i][j] = self._get_next_state(i, j)
        tmp = self.state
        self.state = self._next_state
        self._next_state = tmp

    def _get_next_state(self, row, col):
        live_neighbours = self._count_live_neighbours(row, col)
        if live_neighbours == 3:
            return Game.CELL_ALIVE
        if live_neighbours == 2:
            return self.state[row][col]
        return Game.CELL_DEAD

    def _count_live_neighbours(self, row, col):
        left = max(0, col - 1)
        right = min(self._cols, col + 1)
        count = 0
        if col > 0:
            count += self.state[row][left]
        if col < self._cols - 1:
            count += self.state[row][right]
        if row > 0:
            count += sum(self.state[row - 1][left:right+1])
        if row < self._rows - 1:
            count += sum(self.state[row + 1][left:right+1])
        return count


class App(tk.Tk): 
    TICK_INTERVAL = 100
    CELL_SIZE = 10
    def __init__(self, rows, cols):
        super(App, self).__init__() 
        self._rows = rows
        self._cols = cols
        self._cell_size = 10
        self._game = Game(cols, rows)
        self._create_widgets()
        self.canvas.create_text(100, 100, text='Left click to add cell.\n\nRight click to remove.', tags='help')
        self._grid = None

    def _create_widgets(self):    
        self.title('Game of Life')  
        self.is_playing = False
        self.bind('<space>', lambda a: self._tick() if not self.is_playing else None)
        self.bind('<Escape>', lambda a: self.destroy())
        self.canvas = tk.Canvas(self, 
            width=self._rows * App.CELL_SIZE, 
            height=self._cols * App.CELL_SIZE)
        self.canvas.bind('<Button-1>', self._cmd_click)
        self.canvas.bind('<Button-2>', self._cmd_click)
        
        self.btn_stop = tk.Button(self, text='Stop', command=self._cmd_stop, state=tk.DISABLED)
        self.btn_play = tk.Button(self, text='Play', command=self._cmd_start)
        self.btn_random = tk.Button(self, text='Random', command=self._cmd_random)
        self.btn_glider = tk.Button(self, text='Glider', command=self._cmd_glider)
        self.canvas.pack()
        self.btn_stop.pack(side=tk.RIGHT)
        self.btn_play.pack(side=tk.RIGHT)
        self.btn_random.pack(side=tk.RIGHT)
        self.btn_glider.pack(side=tk.RIGHT)        

    def _cmd_start(self):
            self.is_playing = True
            self.btn_play.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self._tick()
                
    def _tick(self):
        self._game.tick()
        self._update_grid()
        if self.is_playing:
            self.after(App.TICK_INTERVAL, self._tick)

    def _cmd_stop(self):
        self.is_playing = False
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_play.config(state=tk.NORMAL)

    def _cmd_click(self, event):
        x = event.x // app.CELL_SIZE
        y = event.y // app.CELL_SIZE
        state = Game.CELL_ALIVE if event.num == 1 else Game.CELL_DEAD
        self._game.state[x][y] = state
        self._update_grid()

    def _cmd_random(self):
        self._game.random()
        self._update_grid()

    def _cmd_glider(self):
        self._game.glider()
        self._update_grid()

    def _init_grid(self):
        delta = App.CELL_SIZE
        self._grid = [[None] * self._cols for _ in range(self._rows)]
        for i in range(self._rows):
            for j in range(self._cols):
                x = i * delta
                y = j * delta
                self._grid[i][j] = self.canvas.create_rectangle(x, y, x + delta, y + delta)

    def _update_grid(self):
        if self._grid is None:
            self._init_grid()

        for i in range(self._rows):
            for j in range(self._cols):
                self.canvas.itemconfig(self._grid[i][j], 
                    fill='black' if self._game.state[i][j] == Game.CELL_ALIVE else 'white')

def parse_command_line_args():
    import sys
    if len(sys.argv) == 3:
        rows = sys.argv[1]
        cols = sys.argv[2]
    elif len(sys.argv) == 2:
        rows = sys.argv[1]
        cols = rows
    elif len(sys.argv) == 1:
        rows = 25
        cols = 25
    else:
        raise ValueError(f"Too many arguments: {' '.join(sys.argv[1:])}\nUsage: {sys.argv[0]} [ <rows> [ <columns> ] ]")
    return int(rows), int(cols)
   
if __name__ == '__main__':
    rows, colls = parse_command_line_args()
    app = App(rows, colls)            
    app.mainloop()