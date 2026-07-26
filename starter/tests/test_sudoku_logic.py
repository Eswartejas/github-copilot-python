import pytest
import sudoku_logic


def test_create_empty_board_is_9x9():
    board = sudoku_logic.create_empty_board()
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_rejects_invalid_placements():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    assert not sudoku_logic.is_safe(board, 0, 1, 5)
    assert not sudoku_logic.is_safe(board, 1, 0, 5)


def test_is_safe_allows_valid_placements():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    assert sudoku_logic.is_safe(board, 0, 1, 3)
    assert sudoku_logic.is_safe(board, 1, 0, 3)


def test_generate_puzzle_returns_puzzle_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
    assert isinstance(puzzle, list)
    assert isinstance(solution, list)
    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert any(cell == sudoku_logic.EMPTY for row in puzzle for cell in row)
    assert all(cell != sudoku_logic.EMPTY for row in solution for cell in row)


def test_generate_puzzle_has_unique_solution():
    puzzle, _ = sudoku_logic.generate_puzzle(clues=35)
    assert sudoku_logic.count_solutions(puzzle, max_solutions=2) == 1


def test_generate_puzzle_difficulty_clues():
    for difficulty, clues in sudoku_logic.DIFFICULTY_CLUES.items():
        puzzle, _ = sudoku_logic.generate_puzzle(clues=clues)
        assert sum(1 for row in puzzle for cell in row if cell != 0) == clues


def test_deep_copy_returns_independent_clone():
    board = sudoku_logic.create_empty_board()
    clone = sudoku_logic.deep_copy(board)
    clone[0][0] = 9
    assert board[0][0] == sudoku_logic.EMPTY
