#!/usr/bin/env python3

from sudoku import Sudoku, rows, cols

from z3 import Solver, Int, Or, Distinct, sat

symbols = {pos: Int(pos) for pos in Sudoku.positions}

def basic_solver(solver=None):
    if not solver:
        # first we build a solver with the general constraints for sudoku puzzles:
        solver = Solver()

    # assure that every cell holds a value of [1,9]
    for symbol in symbols.values():
        solver.add(Or([symbol == i for i in range(1, 10)]))

    # assure that every row covers every value:
    for row in rows:
        solver.add(Distinct([symbols[row + col] for col in cols]))

    # assure that every column covers every value:
    for col in cols:
        solver.add(Distinct([symbols[row + col] for row in rows]))

    # assure that every block covers every value:
    for i in range(3):
        for j in range(3):
            solver.add(Distinct([symbols[rows[m + i * 3] + cols[n + j * 3]] for m in range(3) for n in range(3)]))

    return solver

def with_hidden_singles(solver=None):
    if not solver:
        solver = basic_solver()

    # every row contains each value in some column:
    for row in rows:
        for v in range(1, 10):
            solver.add(Or([symbols[row + col] == v for col in cols]))

    # every column contains each value in some row:
    for col in cols:
        for v in range(1, 10):
            solver.add(Or([symbols[row + col] == v for row in rows]))

    # assure that every block covers every value:
    for i in range(3):
        for j in range(3):
            for v in range(1, 10):
                solver.add(Or([symbols[rows[m + i * 3] + cols[n + j * 3]] == v for m in range(3) for n in range(3)]))

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
    values = {pos: model.evaluate(s).as_string() for pos, s in symbols.items()}
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
        if count >= 500:
            print('[+] parsing puzzles')
        for i, line in enumerate(lines):
            puzzle = line.strip()
            if count < 500:
                print("[+] parsing puzzle:", puzzle)
            elif count > 1000 and i % 1000 == 0 and i > 0:
                print(f'[+] parsing puzzle {i}')
            puzzles.append(Sudoku(string=puzzle))

    timed_solve(puzzles, basic_solver(), 'basic Z3')
    solutions = timed_solve(puzzles, with_hidden_singles(), 'hidden singles Z3')
    timed_solve(solutions, basic_solver(), 'complete solution checker')


if __name__ == "__main__":
    from sys import argv
    main(argv)
