#!/usr/bin/env python3

from sudoku import Sudoku, rows, cols, cross

from z3 import Solver, Bool, Int, Not, And, Or, Distinct, sat

from itertools import chain, combinations, product

vals = cols
symbols = {pos: Int(pos) for pos in Sudoku.positions}
bool_symbols = {pos: [Bool(pos+str(val)) for val in vals] for pos in Sudoku.positions}

def block_cell_ind(block_row, block_col, inner_row, inner_col):
    i, j, m, n = block_row, block_col, inner_row, inner_col
    return rows[i * 3 + m] + cols[j * 3 + n]

class SymbolGrid:
    def __init__(self, d):
        self.d = d

    @property
    def cells(self):
        return self.d.values()

    @property
    def cols(self):
        for col in cols:
            yield [self.d[row + col] for row in rows]

    @property
    def rows(self):
        for row in rows:
            yield [self.d[row + col] for col in cols]

    @property
    def blocks(self):
        square = list(product(range(3), repeat=2))
        for i, j in square:
            yield [self.d[block_cell_ind(i,j,m,n)] for m, n in square]

    @property
    def groups(self):
        for group in chain(self.rows, self.cols, self.blocks):
            yield group


def basic_solver_bool(solver=None):
    if not solver:
        solver = Solver()

    grid = SymbolGrid(bool_symbols)
    # assert that every cell holds a value of [1,9]
    for cell in grid.cells:
        solver.add(Or(cell))

    # assert that no group holds any value twice
    for group in grid.groups:
        for cell1, cell2 in combinations(group, 2):
            for v in range(9):
                solver.add(Not(And(cell1[v], cell2[v])))

    return solver

def with_hidden_singles_bool(solver=None):
    if not solver:
        solver = basic_solver_bool()

    grid = SymbolGrid(bool_symbols)
    # every group contains each value in some cell:
    for group in grid.groups:
        for v in range(9):
            solver.add(Or([cell[v] for cell in group]))

    return solver

def basic_solver(solver=None):
    if not solver:
        solver = Solver()

    grid = SymbolGrid(symbols)

    # assert that every cell holds a value of [1,9]
    for cell in grid.cells:
        solver.add(Or([cell == i for i in range(1, 10)]))

    # assert that no group holds any value twice
    for group in grid.groups:
        solver.add(Distinct(group))

    return solver

def with_hidden_singles(solver=None):
    if not solver:
        solver = basic_solver()

    grid = SymbolGrid(symbols)

    # every group contains each value in some cell:
    for group in grid.groups:
        for v in range(1, 10):
            solver.add(Or([cell == v for cell in group]))

    return solver

def z3_solving(puzzle, solver):
    """ Function solving the given sudoku puzzle using Z3 """

    # Save current state so we can erase the given values and re-use the basic
    # Sudoku constraints.
    solver.push()

    for pos, value in puzzle.grid.items():
        if value in "123456789":
            solver.add(symbols[pos] == value)

    if solver.check() != sat:
        raise Exception("unsolvable")

    model = solver.model()
    try:
        values = {pos: model.evaluate(s).as_string() for pos, s in symbols.items()}
    except:
        values = dict()
        for pos, l in bool_symbols.items():
            for v in range(9):
                if model.evaluate(l[v]):
                    values[pos] = str(v+1)
    solver.pop()

    return Sudoku(values)

def timed_solve(puzzles, solver, solver_name='Z3'):
    count = len(puzzles)
    print(f'[+] solving using {solver_name}')

    solutions = []

    from time import perf_counter as now
    millis_from_secs = 1000
    start = now()
    for (i, puzzle) in enumerate(puzzles):
        solutions.append(z3_solving(puzzle, solver))
        if count > 1000 and i % 1000 == 0 and i > 0:
            print(f'[+] solved puzzle {i}')
    end = now()
    for solution in solutions:
        assert solution.is_solved()
    avg = round(((end - start)/count)*millis_from_secs, 6)
    print(f'{avg}ms average solve time for {count} puzzles')
    return solutions

def main(argv):
    puzzles = []
    with open('1106_375.txt', 'r') as f:
        lines = f.readlines()
        count = len(lines)
        parse_display_limit = 100
        if count >= parse_display_limit:
            print('[+] parsing puzzles')
        for i, line in enumerate(lines):
            puzzle = line.strip()
            if count < parse_display_limit:
                print("[+] parsing puzzle:", puzzle)
            elif count > 1000 and i % 1000 == 0 and i > 0:
                print(f'[+] parsing puzzle {i}')
            puzzles.append(Sudoku(string=puzzle))

    solutions = timed_solve(puzzles, basic_solver(), 'basic Z3')
    timed_solve(puzzles, with_hidden_singles(), 'hidden singles Z3')
    timed_solve(puzzles, basic_solver_bool(), 'basic Z3 (boolean)')
    timed_solve(puzzles, with_hidden_singles_bool(), 'hidden singles Z3 (boolean)')
    timed_solve(solutions, basic_solver(), 'complete solution checker')


if __name__ == "__main__":
    from sys import argv
    main(argv)
