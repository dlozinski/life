#!/usr/bin/env python3

# Author: Damian Lozinski <lozinski.d at gmail dot com>
# Licence: MIT

import random
import tkinter as tk

DEFAULT_GAME_ROWS = 50
DEFAULT_GAME_COLS = 50


class Game:
    def __init__(self, rows, cols):
        self._rows = rows
        self._cols = cols
        self.state = [[0] * self._cols for _ in range(self._rows)]
        self._next_state = [[0] * self._cols 
            for _ in range(self._rows)]
        self.set_torus_universe(False)

    def reset(self):
        for i in range(self._rows):
            for j in range(self._cols):
                self.state[i][j] = 0

    def init_random(self):
        for i in range(self._rows):
            for j in range(self._cols):
                self.state[i][j] = (random.randint(0, 10013) % 2) * ((random.randint(0, 765436) % 2) + 1)

    def init_glider(self):
        self.reset()
        x = (self._rows // 2)
        y = (self._cols // 2)
        self.state[x][y - 1] = 1
        self.state[x + 1][y] = 1
        self.state[x - 1][y + 1] = 1
        self.state[x][y + 1] = 1
        self.state[x + 1][y + 1] = 1

    def tick(self):
        for i in range(self._rows):
            for j in range(self._cols):
                self._next_state[i][j] = self._get_next_state(i, j)
        tmp = self.state
        self.state = self._next_state
        self._next_state = tmp

    def _get_next_state(self, row, col):
        alive_1 = self._count_neighbours(row, col, player=1)
        alive_2 = self._count_neighbours(row, col, player=2)
        alive_neighbours = alive_1 + alive_2
        cell = self.state[row][col]
        if alive_neighbours == 3:
            return cell or 1 if alive_1 > alive_2 else 2
        if alive_neighbours == 2:
            return cell
        return 0

    def _count_neighbours_on_plane(self, row, col, player):
        left = col - 1
        right = col + 1
        top = row - 1
        bottom = row + 1
        s = self.state
        count = 0
        if top > 0:
            count +=(
                (left >=0 and s[top][left] == player)
                + (s[top][col] == player)
                + (right < self._cols and s[top][right] == player))
        if bottom < self._rows:
            count += (
                (left >=0 and s[bottom][left] == player)
                + (s[bottom][col] == player)
                + (right < self._cols and s[bottom][right] == player))
        count += (
            (left >=0 and s[row][left] == player)
            + (right < self._cols and s[row][right] == player))            
        return count

    def _count_neighbours_on_torus(self, row, col, player):
        left = col - 1
        right = (col + 1) % self._cols
        top = row - 1
        bottom = (row + 1) % self._rows
        s = self.state
        return (
            (s[top][left] == player)
            + (s[top][col] == player)
            + (s[top][right] == player)
            + (s[row][left] == player)
            + (s[row][right] == player)
            + (s[bottom][left] == player)
            + (s[bottom][col] == player)
            + (s[bottom][right] == player)
        )
    
    def set_torus_universe(self, is_torus: bool):
        self._count_neighbours = self._count_neighbours_on_torus if is_torus else self._count_neighbours_on_plane


class App(tk.Tk):
    TICK_INTERVAL = 100
    CELL_SIZE = 10
    GRID_COLORS =  {0: 'white', 1: 'black', 2: 'red'}

    def __init__(self, rows, cols):
        super(App, self).__init__()
        self._rows = rows
        self._cols = cols
        self._cell_size = 10
        self._game = Game(rows, cols)
        self.bind('<Key-space>', 
                  lambda event: self._tick() if not self.is_running else None)
        self.bind('<Key-Escape>', lambda event: self._cmd_reset())
        self._create_widgets()
        self._grid = None
        self.is_running = False
        self._runing_id = None

    def _create_widgets(self):
        self.title('Game of Life')
        self.canvas = tk.Canvas(self,
                                width=self._rows * self.CELL_SIZE,
                                height=self._cols * self.CELL_SIZE)
        self.canvas.bind('<Button-1>', self._cmd_click)
        self.canvas.bind('<Button-2>', self._cmd_click)
        self.canvas.bind('<Button-3>', self._cmd_click)
        self.canvas.bind('<B1-Motion>', lambda event: self._cmd_drag(event, 1))
        self.canvas.bind('<B2-Motion>', lambda event: self._cmd_drag(event, 2))
        self.canvas.bind('<B3-Motion>', lambda event: self._cmd_drag(event, 0))
        self.canvas.create_text(120, 100,
                                text='Left click/drag -  create cell\n'
                                '\nRight click/drag - remove cell\n'
                                '\n<space> - next generation\n'
                                '\n<esc> - reset',
                                tags='help')
        self.canvas.pack(side=tk.TOP)      
        is_torus = tk.BooleanVar(self, value=False)
        tk.Checkbutton(self, text='Torus universe', variable=is_torus,
            command=lambda: self._game.set_torus_universe(is_torus.get())).pack(side=tk.TOP)               
        tk.Button(self, name='stop', text='Stop', command=self._cmd_stop, state=tk.DISABLED).pack(side=tk.RIGHT)
        tk.Button(self, name='run', text='Run', command=self._cmd_run).pack(side=tk.RIGHT)
        tk.Button(self, text='Random', command=self._cmd_random).pack(side=tk.RIGHT)
        tk.Button(self, text='Glider', command=self._cmd_glider).pack(side=tk.RIGHT)

    def _tick(self):
            self._game.tick()
            self._update_grid()
            if self.is_running:
                self._runing_id = self.after(self.TICK_INTERVAL, self._tick)

    def _cmd_reset(self):
        if self._runing_id is not None:
            self.canvas.after_cancel(self._runing_id)
        self.is_running = False
        self.children['run'].config(state=tk.NORMAL)
        self.children['stop'].config(state=tk.DISABLED)
        self._game.reset()
        self.canvas.delete('cells')
        self._grid = None

    def _cmd_run(self):
        self.is_running = True
        self.children['run'].config(state=tk.DISABLED)
        self.children['stop'].config(state=tk.NORMAL)
        self._tick()

    def _cmd_stop(self):
        self.after_cancel(self._runing_id)
        self.is_running = False
        self.children['stop'].config(state=tk.DISABLED)
        self.children['run'].config(state=tk.NORMAL)

    def _cmd_click(self, event):
        x = min(event.x // self.CELL_SIZE, self._cols - 1)
        y = min(event.y // self.CELL_SIZE, self._rows - 1)
        self._game.state[x][y] = event.num % 3
        self._update_grid()

    def _cmd_drag(self, event, state):
        x = min(event.x // self.CELL_SIZE, self._cols - 1)
        y = min(event.y // self.CELL_SIZE, self._rows - 1)
        self._game.state[x][y] = state
        self._update_grid()

    def _cmd_random(self):
        self._game.init_random()
        self._update_grid()

    def _cmd_glider(self):
        self._game.init_glider()
        self._update_grid()

    def _init_grid(self):
        delta = self.CELL_SIZE
        self._grid = [[None] * self._cols for _ in range(self._rows)]
        for i in range(self._rows):
            for j in range(self._cols):
                x = i * delta
                y = j * delta
                self._grid[i][j] = self.canvas.create_rectangle(
                    x, y, x + delta, y + delta, tags='cells')

    def _update_grid(self):
        if self._grid is None:
            self._init_grid()

        for i in range(self._rows):
            for j in range(self._cols):
                self.canvas.itemconfig(
                    self._grid[i][j],
                    fill=self.GRID_COLORS[self._game.state[i][j]])


def get_args():
    import sys
    if len(sys.argv) == 3:
        rows = sys.argv[1]
        cols = sys.argv[2]
    elif len(sys.argv) == 2:
        rows = sys.argv[1]
        cols = rows
    elif len(sys.argv) == 1:
        rows = DEFAULT_GAME_ROWS
        cols = DEFAULT_GAME_COLS
    else:
        raise ValueError(
            f"Too many arguments: {' '.join(sys.argv[1:])}"
            f"\nUsage: {sys.argv[0]} [ <rows> [ <columns> ] ]")
    return int(rows), int(cols)


if __name__ == '__main__':
    rows, cols = get_args()
    app = App(rows, cols)
    app.mainloop()
