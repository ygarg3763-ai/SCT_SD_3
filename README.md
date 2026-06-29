# SCT_SD_3
Sudoku Solver:
A desktop GUI application built with Python and Tkinter that solves Sudoku puzzles
automatically using a backtracking algorithm. Users can type their own puzzle or load
one of three built-in examples, then solve it instantly with a single click.

Features
Auto-solver — backtracking algorithm fills in all missing numbers instantly
3 built-in puzzles — Easy, Medium, and Hard (including Arto Inkala's 2012 "World's Hardest Sudoku")
Custom input — type any puzzle directly into the 9×9 grid
Color coding — given numbers appear dark, algorithm-solved numbers appear in blue
Input validation — only digits 1–9 accepted per cell; conflicts detected before solving
Clear board — reset the grid and start fresh anytime
Clean visual layout with thick borders separating the 3×3 boxes

How It Works — The Backtracking Algorithm
The solver uses a classic backtracking approach — a form of recursive trial and error:
1. Scan the grid for the first empty cell (value = 0)
2. If no empty cell exists → puzzle is solved ✅
3. Try placing digits 1–9 in that cell
4. For each digit, check three Sudoku rules:
     - Not already in the same row
     - Not already in the same column
     - Not already in the same 3×3 box
5. If a digit is valid → place it and recurse to the next empty cell
6. If the recursive call fails → erase the digit (backtrack) and try the next one
7. If no digit works → return False, signalling the caller to backtrack

This guarantees a correct solution for any valid Sudoku puzzle.

Tech Used:
Tool         Purpose
Python 3     Core language
Tkinter      GUI framework (built into Python — no install needed)
copy module  Deep-copying the grid before solving (preserves original for color-coding)

No external libraries required — runs on any machine with Python 3 installed.
