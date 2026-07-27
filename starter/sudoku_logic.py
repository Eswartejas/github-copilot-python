import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}
def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def find_unassigned_location(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None, None

def fill_board(board):
    row, col = find_unassigned_location(board)
    if row is None:
        return True

    possible = list(range(1, SIZE + 1))
    random.shuffle(possible)
    for candidate in possible:
        if is_safe(board, row, col, candidate):
            board[row][col] = candidate
            if fill_board(board):
                return True
            board[row][col] = EMPTY

    return False

def count_solutions(board, max_solutions=2):
    row, col = find_unassigned_location(board)
    if row is None:
        return 1

    total = 0
    for candidate in range(1, SIZE + 1):
        if is_safe(board, row, col, candidate):
            board[row][col] = candidate
            total += count_solutions(board, max_solutions)
            board[row][col] = EMPTY
            if total >= max_solutions:
                return total
    return total

def remove_cells(board, clues):
    target_removals = SIZE * SIZE - clues
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)

    removed = 0
    for row, col in positions:
        if removed >= target_removals:
            break
        if board[row][col] == EMPTY:
            continue

        backup = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, max_solutions=2) == 1:
            removed += 1
        else:
            board[row][col] = backup

    if removed < target_removals:
        raise RuntimeError('Unable to generate a unique puzzle with the requested clue count')

def generate_puzzle(clues=35):
    while True:
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        try:
            remove_cells(board, clues)
            puzzle = deep_copy(board)
            return puzzle, solution
        except RuntimeError:
            continue
