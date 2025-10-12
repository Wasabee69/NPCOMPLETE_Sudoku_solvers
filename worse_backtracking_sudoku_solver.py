import math
import time
from sortedcontainers import SortedList

class SudokuSolver:
    def __init__(self, n: int) -> None:
        self.n = n
        self.sq = int(math.sqrt(n))
        self.bit_to_int = {}
        for value in range(1, n + 1):
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
        
        def get_square_idx(i, j):
            return (j // self.sq) + (i // self.sq) * self.sq
            
        def remaining_count(i, j):
            square_idx = get_square_idx(i, j)
            used = rows[i] | cols[j] | squares[square_idx]
            return self.n - used.bit_count()
        
        remaining_arr = [[0] * self.n for _ in range(self.n)]
        remaining_cells = set()
        sorted_list = SortedList(key=lambda x: x[0])
        
        for i in range(self.n):
            for j in range(self.n):
                if puzzle_matrix[i][j] == 0:
                    count = remaining_count(i, j)
                    remaining_arr[i][j] = count
                    sorted_list.add((count, i, j))
                    remaining_cells.add((i, j))

        def recursive_solver(remaining_cells: set) -> list[list[int]]:
            if not remaining_cells:
                return puzzle_matrix
                
            count, i, j = sorted_list.pop(0)
            remaining_cells.remove((i, j))
            square_idx = get_square_idx(i, j)

            mask = ~(rows[i] | cols[j] | squares[square_idx]) & self.filled_mask
            while mask:
                lsb = mask & -mask
                mask -= lsb
                value = self.bit_to_int[lsb]
                
                puzzle_matrix[i][j] = value
                rows[i] ^= lsb
                cols[j] ^= lsb
                squares[square_idx] ^= lsb

                peers_to_reset = []
                for (x, y) in self.peers[(i, j)]:
                    if (x, y) in remaining_cells:
                        old_count = remaining_arr[x][y]
                        sorted_list.remove((old_count, x, y))
                        
                        new_count = remaining_count(x, y)
                        remaining_arr[x][y] = new_count
                        sorted_list.add((new_count, x, y))
                        peers_to_reset.append((x, y, old_count))
                
                if recursive_solver(remaining_cells):
                    return puzzle_matrix
                
                puzzle_matrix[i][j] = 0
                rows[i] ^= lsb
                cols[j] ^= lsb
                squares[square_idx] ^= lsb
                
                for (x, y, old_count) in peers_to_reset:
                    sorted_list.remove((remaining_arr[x][y], x, y))
                    remaining_arr[x][y] = old_count
                    sorted_list.add((old_count, x, y))
            
            remaining_cells.add((i, j))
            sorted_list.add((remaining_arr[i][j], i, j))
        
        return recursive_solver(remaining_cells)
    
class SudokuChecker:
    def __init__(self, n: int) -> None:
        self.n = n
        self.sq = int(math.sqrt(n))

    def check(self, board: list[list[int]]) -> bool:
        digits = set(range(1, self.n + 1))
        for i in range(self.n):
            if set(board[i]) != digits:
                return False
        for j in range(self.n):
            col = {board[i][j] for i in range(self.n)}
            if col != digits:
                return False
        for i in range(0, self.n, self.sq):
            for j in range(0, self.n, self.sq):
                block = set()
                for r in range(i, i + self.sq):
                    for c in range(j, j + self.sq):
                        block.add(board[r][c])
                if block != digits:
                    return False
        return True

## benchmarking with some problems i copied
problems9x9 = ["..7.9.6.3..3..4...1.6..5..........5....7.9.......5..2.8.1..........8.3...243..7..","38..............6.1....93....62...9.832...1.......6....1..7.2.39.31...8.5..6.2..9", ".86..1..41....67.22..45.81..15......32...........17.5.....4....5.7.63.8..32......", ".4.6.....7..2.5....964.75..6715..2..........75..8..6..95.....8..6...24.........7.",".4.3...69..5....81.9126...5.5.1.23....9..3.1....65...........4..6.5.......84.....","9.8....52..4..59..1.3.........5.8.3..3.92...4....317.......2..5.19.8....2.7......",".......1.9...2...........69.4375....2.9..35..67...4.......6.2...5..3..7...7.9...3",".1.5.8.9....49..31..8....6....835.....3.4..1..2.........6..2...5.2916..3.8.......","......1.7...1.956..5.....4934.26..7...69....1......4...74.9.........129.5.......4","...359...2.54.8.6.........8..8.65.7.9..2..3..7.......6.67..25....9...8..4........","..9...4.5.2.....1.1.....2......4..5....1...47.....9..6.562.....9..73.5...1.4.6.3.","....9.......2.3..5..845.2..35..7.182...12..7......4.9..7....3..8..3...2.....4.8..",".....4...86....3..9.1.2....7.3...62..1.9..74.4....1..81.23.........18.......6....","....687..5.6.........3..9......2.3793..6.....4.27..8.6..9....8..5..4...38...5.4..",".7.36.5....2.7.1....95...2..64......3..95.7........9.3....1.2.......6.9.........5","52....6.8..7..4.2...6.9......275.....4...9.8..6.2.........735.............8.26..7",".1.........5.1...2.8.9..1...264.53....81..2.419.2..8.......39.........85...52.6..","...1.9.46......8......38......96..8...6...2.48...74..12.8...4.....3......147..63.",".......194...7.........6....75.6..3..1835.7......8....9....8361.6.......7.3....5.",".4.9..15.2.8.4....5......3.....2157...........7....2.9..9...4..187.........79..8.",".9.8.31...6....7......2......1.3.......4.8.72....6....23.....1.4.9..6..36.8...4.9",".95..6..2...9.23......5..7....7.1.....26.3..8....9....25....1..6...8.23.7.......5","......5....4...812....4...7.....23..78...1...5.2....762..7....1.7...4.6.3.6....5."]
solver = SudokuSolver(9)
checker = SudokuChecker(9)
for i, p in enumerate(problems9x9):
    start = time.perf_counter()
    s1 = solver.solve(p)
    end = time.perf_counter()
    duration = end - start
    print(f"id:{i} took {duration:.4f} seconds to solve")
    print(checker.check(s1))


problems16x16 = ["..7..29.3..a......e..a.g..2fb.9.a....c...........8d.6......b1.e2b.5...168e.7f..3..8g7.c2.3b.........8.......d.2e.acd....46..7.5..b.f..81....g5c.19.7.......e.........f7.2g.ce9..g..ce.4361...2.b85.ed......4.f6...........3....9.g.a36..9.c..d......4..a.f8..e..", "02.....5.4..3.b.68.e..a3...2.f4.b....02.6.5....a...9...c...785.0..a...c1........d6e...9.7a....3..30.e...f..951.d4....8b20..............f2b6....8a.36c..9...8.25..1....86.0...7d3........d3...a..7.d43...5...0...3....6.0.8c....5.b2.a...3f..d.61.c.f..1.9.....e4"]
solver = SudokuSolver(16)
checker = SudokuChecker(16)
for i, p in enumerate(problems16x16):
    start = time.perf_counter()
    s1 = solver.solve(p)
    end = time.perf_counter()
    duration = end - start
    print(f"id:{i} took {duration:.4f} seconds to solve")
    print(checker.check(s1))

