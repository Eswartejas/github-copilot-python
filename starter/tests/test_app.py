import json
from app import CURRENT


def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<html' in response.data or b'<!DOCTYPE html>' in response.data


def test_new_game_route_returns_puzzle(client):
    response = client.get('/new')
    assert response.status_code == 200
    data = response.get_json()
    assert 'puzzle' in data
    assert isinstance(data['puzzle'], list)
    assert len(data['puzzle']) == 9
    assert all(len(row) == 9 for row in data['puzzle'])


def test_new_game_route_supports_difficulty(client):
    response = client.get('/new?difficulty=hard')
    assert response.status_code == 200
    data = response.get_json()
    assert data['difficulty'] == 'hard'
    assert data['clues'] == 25
    assert len(data['puzzle']) == 9
    assert sum(1 for row in data['puzzle'] for cell in row if cell != 0) == 25


def test_hint_route_requires_game_in_progress(client):
    response = client.post('/hint')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'No game in progress'


def test_hint_route_reveals_one_cell(client):
    new_game_response = client.get('/new?difficulty=medium')
    assert new_game_response.status_code == 200
    data = new_game_response.get_json()
    assert data['difficulty'] == 'medium'

    empty_cell_count = sum(1 for row in data['puzzle'] for cell in row if cell == 0)
    assert empty_cell_count > 0

    response = client.post('/hint')
    assert response.status_code == 200
    hint_data = response.get_json()
    assert 'row' in hint_data and 'col' in hint_data and 'value' in hint_data
    assert isinstance(hint_data['row'], int)
    assert isinstance(hint_data['col'], int)
    assert isinstance(hint_data['value'], int)
    assert 0 <= hint_data['row'] < 9
    assert 0 <= hint_data['col'] < 9

    assert data['puzzle'][hint_data['row']][hint_data['col']] == 0

    # The hint must fill an empty cell with a nonzero value
    assert hint_data['value'] != 0


def test_check_route_requires_game_in_progress(client):
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'No game in progress'


def test_check_route_reports_incorrect_cells(client):
    new_game_response = client.get('/new')
    assert new_game_response.status_code == 200
    board = [row[:] for row in new_game_response.get_json()['puzzle']]
    row, col = next((i, j) for i in range(9) for j in range(9) if board[i][j] == 0)
    board[row][col] = 1 if board[row][col] != 1 else 2

    response = client.post('/check', json={'board': board})
    assert response.status_code == 200
    data = response.get_json()
    assert 'incorrect' in data
    assert isinstance(data['incorrect'], list)
    assert [row, col] in data['incorrect']


def test_check_route_highlights_only_incorrect_user_entries(client):
    response = client.get('/new')
    assert response.status_code == 200
    game_data = response.get_json()
    board = [row[:] for row in game_data['puzzle']]
    solution = CURRENT['solution']
    empty_cells = [(i, j) for i in range(9) for j in range(9) if board[i][j] == 0]
    assert empty_cells

    row, col = empty_cells[0]
    wrong_value = solution[row][col] % 9 + 1
    if wrong_value == solution[row][col]:
        wrong_value = (wrong_value % 9) + 1
    board[row][col] = wrong_value

    response = client.post('/check', json={'board': board})
    assert response.status_code == 200
    data = response.get_json()
    assert [row, col] in data['incorrect']
    assert all([i, j] not in data['incorrect'] for i, j in empty_cells if (i, j) != (row, col))


def test_check_route_accepts_correct_solution_entries(client):
    response = client.get('/new')
    assert response.status_code == 200
    correct_board = CURRENT['solution']

    response = client.post('/check', json={'board': correct_board})
    assert response.status_code == 200
    data = response.get_json()
    assert data['incorrect'] == []
    assert data['solved'] is True


def test_check_route_detects_incomplete_puzzle(client):
    response = client.get('/new')
    assert response.status_code == 200
    incomplete_board = [row[:] for row in CURRENT['puzzle']]

    response = client.post('/check', json={'board': incomplete_board})
    assert response.status_code == 200
    data = response.get_json()
    assert data['incorrect'] == []
    assert data['solved'] is False
