#!/usr/bin/env python3

from sudoku import Sudoku

from z3 import Solver, Int, Or, Distinct, sat

# first we build a solver with the general constraints for sudoku puzzles:
solver = Solver()

symbols = {pos: Int(pos) for pos in Sudoku.positions}

# assure that every cell holds a value of [1,9]
for symbol in symbols.values():
    solver.add(Or([symbol == i for i in range(1, 10)]))

# assure that every row covers every value:
for row in "ABCDEFGHI":
    solver.add(Distinct([symbols[row + col] for col in "123456789"]))

# assure that every column covers every value:
for col in "123456789":
    solver.add(Distinct([symbols[row + col] for row in "ABCDEFGHI"]))

# assure that every block covers every value:
for i in range(3):
    for j in range(3):
        solver.add(Distinct([symbols["ABCDEFGHI"[m + i * 3] + "123456789"[n + j * 3]] for m in range(3) for n in range(3)]))

def z3_solving(puzzle):
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

def main():
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

    print("[+] solving using Z3")

    solutions = []

    from time import perf_counter as now
    millis_from_secs = 1000
    start = now()
    for (i, puzzle) in enumerate(puzzles):
        solutions.append(z3_solving(puzzle))
        if count > 1000 and i % 1000 == 0 and i > 0:
            print(f'[+] solved puzzle {i}')
    end = now()
    for solution in solutions:
        assert solution.is_solved()
    avg = round(((end - start)/count)*millis_from_secs, 6)
    print(f'{avg}ms average solve time for {count} puzzles')

if __name__ == "__main__":
    from sys import argv

    main()
