# z3-sudoku-test

I took the Z3-based Sudoku solver implementation from [this
repo](https://github.com/ppmx/sudoku-solver/) and modified it to handle large
batches of puzzles. Also included are copies of the datasets for ~49,000 "easy"
17 clue puzzles and 375 "hard" puzzles. For more on the datasets, and general
information about different approaches to solving Sudoku, [this blog
post](https://t-dillon.github.io/tdoku/) from the author of the fastest
available Sudoku solver (AFAIK) is a great resource.

Running this on my machine (equipped with an i7 6700K) with [Z3
4.8.9](https://github.com/Z3Prover/z3/releases/tag/z3-4.8.9) resulted in an
average of ~15ms on the easy-49K set. and ~29ms on the hard-375 set. Note that,
as a rough measure of the overhead of the Z3 Python API, simply checking a
solved puzzle averaged ~7ms.
