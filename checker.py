from math import sqrt as sqrt
class SudokuChecker:
    def __init__(self, n: int) -> None:
        self.n = n
        self.sq = int(sqrt(n))
        
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