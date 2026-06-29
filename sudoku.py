import tkinter as tk
from tkinter import ttk, messagebox
import copy

# Built-in puzzle library  (0 = empty cell)
PUZZLES = {
    "Easy": [
        # Classic Wikipedia example — 51 given clues
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
    "Medium": [
        # 29 given clues — requires more deduction
        [0, 0, 0, 2, 6, 0, 7, 0, 1],
        [6, 8, 0, 0, 7, 0, 0, 9, 0],
        [1, 9, 0, 0, 0, 4, 5, 0, 0],
        [8, 2, 0, 1, 0, 0, 0, 4, 0],
        [0, 0, 4, 6, 0, 2, 9, 0, 0],
        [0, 5, 0, 0, 0, 3, 0, 2, 8],
        [0, 0, 9, 3, 0, 0, 0, 7, 4],
        [0, 4, 0, 0, 5, 0, 0, 3, 6],
        [7, 0, 3, 0, 1, 8, 0, 0, 0],
    ],
    "Hard": [
        # Arto Inkala's 2012 "World's Hardest Sudoku" — only 23 clues
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 6, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 9, 0, 2, 0, 0],
        [0, 5, 0, 0, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 4, 5, 7, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 3, 0],
        [0, 0, 1, 0, 0, 0, 0, 6, 8],
        [0, 0, 8, 5, 0, 0, 0, 1, 0],
        [0, 9, 0, 0, 0, 0, 4, 0, 0],
    ],
}

# Solver — pure logic

def is_valid(grid: list, row: int, col: int, num: int) -> bool:
   
    if num in grid[row]:
        return False

    if num in [grid[r][col] for r in range(9)]:
        return False

    box_row = 3 * (row // 3)
    box_col = 3 * (col // 3)
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if grid[r][c] == num:
                return False

    return True


def solve_sudoku(grid: list) -> bool:
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:                     # found an empty cell
                for num in range(1, 10):
                    if is_valid(grid, row, col, num):
                        grid[row][col] = num            # tentatively place num
                        if solve_sudoku(grid):
                            return True                 # propagate success up
                        grid[row][col] = 0              # ← BACKTRACK: undo placement
                return False                            # no num worked → dead end
    return True                                         # no empty cell → solved!


def validate_input(grid: list) -> tuple:
   
    for row in range(9):
        for col in range(9):
            num = grid[row][col]
            if num == 0:
                continue
            # Temporarily blank this cell, check if placing num here is still valid
            grid[row][col] = 0
            if not is_valid(grid, row, col, num):
                grid[row][col] = num   # restore before returning
                return False, (
                    f"Conflict detected: the number {num} appears more than once\n"
                    f"in the same row, column, or 3×3 box."
                )
            grid[row][col] = num
    return True, ""


# Visual constants

FONT_GIVEN  = ("Segoe UI", 14, "bold")
FONT_SOLVED = ("Segoe UI", 14)
C_BG        = "#f4f6f8"   # window background
C_BLOCK     = "#8395a7"   # thick border between 3×3 blocks
C_CELL      = "#ffffff"   # normal cell background
C_GIVEN_BG  = "#dfe6f0"   # light tint for cells that have given numbers
C_GIVEN_FG  = "#1f2933"   # near-black text for given numbers
C_SOLVED_FG = "#0b6fbf"   # blue text for algorithm-solved numbers


# GUI

class SudokuSolverApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.resizable(False, False)
        self.root.configure(bg=C_BG)

        # cells[r][c]  — the Entry widget at row r, column c
        self.cells = [[None] * 9 for _ in range(9)]

        self._build_widgets()

    # Widget construction 

    def _build_widgets(self):
        tk.Label(
            self.root, text="Sudoku Solver",
            font=("Segoe UI", 18, "bold"), bg=C_BG, fg="#1f2933"
        ).pack(pady=(20, 3))

        tk.Label(
            self.root,
            text="Type your puzzle below, or load an example — then click Solve",
            font=("Segoe UI", 10), bg=C_BG, fg="#616e7c"
        ).pack(pady=(0, 12))

        self._build_grid()
        self._build_controls()

        self.status_var = tk.StringVar(value="Ready — load a puzzle or type your own.")
        tk.Label(
            self.root, textvariable=self.status_var,
            font=("Segoe UI", 9), bg=C_BG, fg="#9aa5b1"
        ).pack(pady=(8, 18))

    def _build_grid(self):
        
        grid_outer = tk.Frame(self.root, bg=C_BLOCK, bd=2, relief="solid")
        grid_outer.pack(padx=20)

        register = self.root.register(self._validate_key)

        for br in range(3):        # block-row  (0=top, 1=middle, 2=bottom)
            for bc in range(3):    # block-col  (0=left, 1=center, 2=right)

                block = tk.Frame(grid_outer, bg=C_BLOCK, padx=2, pady=2)
                block.grid(row=br, column=bc, padx=2, pady=2)

                for cr in range(3):    # cell-row within block
                    for cc in range(3):  # cell-col within block
                        r = br * 3 + cr   # absolute row 0–8
                        c = bc * 3 + cc   # absolute col 0–8

                        entry = tk.Entry(
                            block,
                            width=2,
                            font=FONT_GIVEN,
                            justify="center",
                            bg=C_CELL,
                            fg=C_GIVEN_FG,
                            relief="flat",
                            highlightthickness=1,
                            highlightbackground="#c8d6e5",
                            validate="key",
                            validatecommand=(register, "%P"),
                        )
                        entry.grid(row=cr, column=cc, padx=1, pady=1, ipadx=9, ipady=7)
                        self.cells[r][c] = entry

    def _build_controls(self):
        bar = tk.Frame(self.root, bg=C_BG)
        bar.pack(pady=12)

        tk.Label(bar, text="Example:", font=("Segoe UI", 10), bg=C_BG).grid(
            row=0, column=0, padx=(0, 4)
        )

        self.puzzle_var = tk.StringVar(value="Easy")
        ttk.Combobox(
            bar, textvariable=self.puzzle_var,
            values=list(PUZZLES.keys()), state="readonly", width=8
        ).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(bar, text="Load",     command=self.on_load).grid(row=0, column=2, padx=4)
        ttk.Button(bar, text="✔  Solve", command=self.on_solve).grid(row=0, column=3, padx=4)
        ttk.Button(bar, text="Clear",    command=self.on_clear).grid(row=0, column=4, padx=4)

    # Input validation 

    @staticmethod
    def _validate_key(new_value: str) -> bool:
        """
        Tkinter calls this before each keystroke in any cell.
        Only allow: empty string (user erasing) or exactly one digit 1–9.
        """
        return new_value == "" or (len(new_value) == 1 and new_value in "123456789")

    #  Grid read / write helpers 

    def _read_grid(self) -> list:
        """Pull current Entry values → 9×9 list of ints (0 = empty)."""
        return [
            [int(self.cells[r][c].get()) if self.cells[r][c].get() else 0
             for c in range(9)]
            for r in range(9)
        ]

    def _reset_cells(self):
        """Restore every cell to its blank, editable state."""
        for r in range(9):
            for c in range(9):
                e = self.cells[r][c]
                e.config(state="normal", bg=C_CELL, fg=C_GIVEN_FG, font=FONT_GIVEN)
                e.delete(0, tk.END)

    def _write_solution(self, original: list, solved: list):
        
        for r in range(9):
            for c in range(9):
                e = self.cells[r][c]
                e.config(state="normal")
                e.delete(0, tk.END)
                val = solved[r][c]
                e.insert(0, str(val))

                if original[r][c] != 0:
                    # Given number
                    e.config(fg=C_GIVEN_FG, font=FONT_GIVEN,
                             bg=C_GIVEN_BG, state="readonly")
                else:
                    # Algorithm-filled number
                    e.config(fg=C_SOLVED_FG, font=FONT_SOLVED,
                             bg=C_CELL, state="readonly")

    # Event handlers 

    def on_load(self):
        """Load the selected example puzzle into the grid."""
        self._reset_cells()
        name    = self.puzzle_var.get()
        puzzle  = PUZZLES[name]

        for r in range(9):
            for c in range(9):
                val = puzzle[r][c]
                if val != 0:
                    self.cells[r][c].insert(0, str(val))
                    self.cells[r][c].config(bg=C_GIVEN_BG, state="readonly")

        self.status_var.set(f"{name} puzzle loaded — click Solve to fill it in.")

    def on_solve(self):
        """Validate the grid, run the backtracking solver, display results."""
        original = self._read_grid()

        # Check 1: conflicts in existing numbers 
        ok, msg = validate_input(copy.deepcopy(original))
        if not ok:
            messagebox.showerror("Invalid puzzle", msg)
            self.status_var.set("⚠  Fix the conflict and try again.")
            return

        #  Check 2: already complete? 
        if all(original[r][c] != 0 for r in range(9) for c in range(9)):
            messagebox.showinfo("Already complete", "The grid is already fully filled!")
            return

        # ── Run solver on a copy (preserves original for color-coding) ──
        working = copy.deepcopy(original)
        solved  = solve_sudoku(working)

        if not solved:
            messagebox.showerror(
                "No solution",
                "This puzzle has no valid solution.\n\n"
                "Check for conflicting or missing numbers."
            )
            self.status_var.set("❌  No solution found.")
            return

        self._write_solution(original, working)
        self.status_var.set("✅  Puzzle solved! Given numbers are dark, solved numbers are blue.")

    def on_clear(self):
        """Wipe the board completely."""
        self._reset_cells()
        self.status_var.set("Board cleared — enter a puzzle or load an example.")


# Entry point

def main():
    root = tk.Tk()
    SudokuSolverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()