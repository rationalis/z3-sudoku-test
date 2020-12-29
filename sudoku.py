#!/usr/bin/env python3

def cross(iter_a, iter_b):
    """ Returns a list of all elements of the cross product of iter_a and iter_b """

    return [(x + y) for x in iter_a for y in iter_b]

rows, cols = "ABCDEFGHI", "123456789"
positions = cross(rows, cols)
# units stores a list of lists with cells belonging together:
units = [cross(rows, col) for col in cols] \
        + [cross(row, cols) for row in rows] \
        + [cross(r, c) for r in ["ABC", "DEF", "GHI"] for c in ["123", "456", "789"]]

class Sudoku:
    """ Sudoku grid representation.

    Provides a routine to check if current grid is solved.
    """
    positions = positions

    def __init__(self, mapping=None, string=None):
        # self.grid maps a cell (e.g. 'A1') to its value (e.g. int('9')).
        # A dot ('.') represents a cell that is not yet filled.
        self.grid = {pos: '.' for pos in positions}

        if string:
            if any(c not in "123456789." for c in string) or len(string) != 81:
                raise Exception(f'invalid grid string {string}')
            mapping = dict(zip(positions, string))

        if mapping:
            # print(mapping)
            self.grid.update(mapping)

    def __str__(self):
        """ Returns simple string representation of the current grid. Can be used
        as input for parse().
        """

        return ''.join([self.grid[pos] for pos in positions])

    def is_solved(self):
        """ Returns true if the current grid is solved and false otherwise. """

        # assert that every cell holds a value the range of 1 to 9:
        if not all([cell in "123456789" for cell in self.grid.values()]):
            return False

        # assert that each unit is solved:
        check_unit = lambda unit: set(self.grid[cell] for cell in unit) == set("123456789")
        return all(check_unit(unit) for unit in units)
