from math import inf as inf, sqrt as sqrt
import time
from checker import SudokuChecker
from problems import ProblemSet

class SudokuSolver:
    def __init__(self, n: int) -> None:
        self.n = n
        self.sq = int(sqrt(n))
        self.bit_to_int = {}
        for value in range(n + 1):
            self.bit_to_int[1 << value] = value
        self.filled_mask = (1 << (n + 1)) - 2
        
        self.peers = {}
        for i in range(n):
            for j in range(n):
                self.peers[(i, j)] = []
                for k in range(n):
                    if k != j:
                        self.peers[(i, j)].append((i, k))
                for k in range(n):
                    if k != i:
                        self.peers[(i, j)].append((k, j))
                r = (i // self.sq) * self.sq
                c = (j // self.sq) * self.sq
                for k1 in range(self.sq):
                    for k2 in range(self.sq):
                        row = r + k1
                        col = c + k2
                        if row != i and col != j:
                            self.peers[(i, j)].append((row, col))

    def get_matrix(self, puzzle: str) -> list[list[int]]:
        if "0" in puzzle:
            m = max(ord(ch) for ch in puzzle)
            puzzle = [chr(m+1) if ch == "0" else ch for ch in puzzle]

        puzzle = [ch.upper() if "a" <= ch <= "z" else ch for ch in puzzle]
        mat = [[] for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                index = i * self.n + j
                if puzzle[index] == ".":
                    mat[i].append(0)
                elif "A" <= puzzle[index] <= "Z":
                    mat[i].append(10 + ord(puzzle[index]) - ord("A"))
                else:
                    mat[i].append(int(puzzle[index]))
        return mat

    def get_ints_squares(self, mat: list[list[int]]) -> list[int]:
        squares = [0] * self.n
        for i in range(self.n):
            for j in range(self.n):
                square_idx = (j // self.sq) + (i // self.sq) * self.sq
                if mat[i][j]:
                    squares[square_idx] |= 1 << mat[i][j]
        return squares

    def get_ints_rows_cols(self, mat: list[list[int]], invert: bool) -> list[int]:
        rc = [0] * self.n
        for i in range(self.n):
            for j in range(self.n):
                if mat[i][j]:
                    if invert:
                        rc[j] |= 1 << mat[i][j]
                    else:
                        rc[i] |= 1 << mat[i][j]
        return rc

    def solve(self, puzzle: str) -> list[list[int]]:
        puzzle_matrix = self.get_matrix(puzzle)
        rows = self.get_ints_rows_cols(puzzle_matrix, False)
        cols = self.get_ints_rows_cols(puzzle_matrix, True)
        squares = self.get_ints_squares(puzzle_matrix)


        def get_square_idx(i: int, j: int) -> int:
            return (j // self.sq) + (i // self.sq) * self.sq
        
            
        def constraints(i: int, j: int) -> int:
            square_idx = get_square_idx(i, j)
            used = rows[i] | cols[j] | squares[square_idx]
            return self.n + 1 - used.bit_count()
        
        buckets = [set() for _ in range(self.n+1)]
        lowest_amount_of_constraints = self.n
        for i in range(self.n):
            for j in range(self.n):
                if puzzle_matrix[i][j] == 0:
                    count = constraints(i, j)
                    buckets[count].add((i, j))
                    lowest_amount_of_constraints = min(lowest_amount_of_constraints, count)

        def recursive_solver(lowest_amount_of_constraints: int) -> list[list[int]]:

            _lowest = lowest_amount_of_constraints
            while _lowest < self.n+1 and not buckets[_lowest]:
                _lowest += 1
            if _lowest == self.n+1:
                return puzzle_matrix
            
            i, j = buckets[_lowest].pop()

            updates = []
            for x, y in self.peers[(i, j)]:
                if puzzle_matrix[x][y] == 0:
                    count = constraints(x, y)
                    if (x, y) in buckets[count]:
                        buckets[count].remove((x, y))
                        buckets[count-1].add((x, y))
                        if count == _lowest:
                            lowest_amount_of_constraints = _lowest - 1
                        updates.append((count, x, y))

            square_idx = get_square_idx(i, j)
            mask = ~(rows[i] | cols[j] | squares[square_idx]) & self.filled_mask
            while mask:
                lsb = mask & -mask
                mask -= lsb
                chosen_value_for_current_cell = lsb.bit_length() - 1

                puzzle_matrix[i][j] = chosen_value_for_current_cell

                rows[i] ^= lsb
                cols[j] ^= lsb
                squares[square_idx] ^= lsb
                
                if recursive_solver(lowest_amount_of_constraints):
                    return puzzle_matrix
                
                puzzle_matrix[i][j] = 0
                rows[i] ^= lsb
                cols[j] ^= lsb
                squares[square_idx] ^= lsb

            for c, x, y in updates:
                buckets[c-1].remove((x, y))
                buckets[c].add((x, y))
                
            buckets[_lowest].add((i, j))
        
        return recursive_solver(lowest_amount_of_constraints)
    

## example usage
for dimension, problems in ProblemSet.problems():

    solver = SudokuSolver(dimension)
    checker = SudokuChecker(dimension)

    for i, p in enumerate(problems):
        start = time.perf_counter()
        solution = solver.solve(p)
        end = time.perf_counter()
        duration = end - start

        print(f"id:{i} took {duration:.4f} seconds to solve")
        print(checker.check(solution))

