from flask import Flask, render_template, jsonify, request
import random
import sudoku_logic

app = Flask(__name__)
DEFAULT_DIFFICULTY = 'medium'

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', DEFAULT_DIFFICULTY).lower()
    clues_arg = request.args.get('clues')

    if clues_arg is not None:
        try:
            clues = int(clues_arg)
        except ValueError:
            difficulty = DEFAULT_DIFFICULTY
            clues = sudoku_logic.DIFFICULTY_CLUES[DEFAULT_DIFFICULTY]
    else:
        clues = sudoku_logic.DIFFICULTY_CLUES.get(difficulty, sudoku_logic.DIFFICULTY_CLUES[DEFAULT_DIFFICULTY])
        if difficulty not in sudoku_logic.DIFFICULTY_CLUES:
            difficulty = DEFAULT_DIFFICULTY

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty, 'clues': clues})

@app.route('/hint', methods=['POST'])
def get_hint():
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400

    empty_cells = [
        (i, j) for i in range(sudoku_logic.SIZE)
        for j in range(sudoku_logic.SIZE)
        if puzzle[i][j] == sudoku_logic.EMPTY
    ]

    if not empty_cells:
        return jsonify({'error': 'No empty cells available'}), 400

    row, col = random.choice(empty_cells)
    value = solution[row][col]
    puzzle[row][col] = value
    CURRENT['puzzle'] = puzzle

    return jsonify({'row': row, 'col': col, 'value': value})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    incomplete = False
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            value = board[i][j]
            if value == 0:
                incomplete = True
            elif value != solution[i][j]:
                incorrect.append([i, j])
    solved = not incorrect and not incomplete
    return jsonify({'incorrect': incorrect, 'solved': solved})

if __name__ == '__main__':
    app.run(debug=True)