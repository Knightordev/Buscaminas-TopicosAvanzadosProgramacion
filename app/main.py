from flask import Flask, render_template, request, jsonify, session
from game import Game
import json

app = Flask(__name__)
app.secret_key = 'buscaminas_secret'

def game_to_dict(game):
    result = []
    for r in range(game.r):
        row = []
        for c in range(game.c):
            cell = game.grid[r][c]
            row.append({
                'mine': cell.mine,
                'revealed': cell.revealed,
                'flag': cell.flag,
                'number': cell.number
            })
        result.append(row)
    return result

def load_game_from_session():
    if 'grid' not in session:
        return None
    g = Game.__new__(Game)
    g.r = session['r']
    g.c = session['c']
    g.mines = session['mines']
    from game import Cell
    g.grid = [[Cell() for _ in range(g.c)] for _ in range(g.r)]
    for r in range(g.r):
        for c in range(g.c):
            d = session['grid'][r][c]
            g.grid[r][c].mine = d['mine']
            g.grid[r][c].revealed = d['revealed']
            g.grid[r][c].flag = d['flag']
            g.grid[r][c].number = d['number']
    return g

@app.route('/')
def index():
    game = Game(10, 10, 10)
    session['grid'] = game_to_dict(game)
    session['r'] = game.r
    session['c'] = game.c
    session['mines'] = game.mines
    data = {'title': 'index', 'page': 'inicio'}
    return render_template('index.html', data=data, grid=game.get_grid())

@app.route('/reveal/<int:row>/<int:col>', methods=['POST'])
def reveal(row, col):
    game = load_game_from_session()
    if game is None:
        return jsonify({'error': 'no game'}), 400

    if not game.in_bounds(row, col):
        return jsonify({'error': 'invalid_coordinates'}), 400
    cell = game.grid[row][col]

    if cell.revealed:
        return jsonify({'already_revealed': True})

    if cell.flag:
        return jsonify({'blocked': 'flagged'})
    revealed_cell = game.reveal(row, col)
    session['grid'] = game_to_dict(game)

    if revealed_cell is None:
        return jsonify({'error': 'invalid_move'}), 400

    if revealed_cell.mine:
        return jsonify({'type': 'mine'})
    else:
        return jsonify({'type': 'number', 'value': revealed_cell.number})


@app.route('/toggle_flag', methods=['POST'])
def handle_flag():
    game = load_game_from_session()
    if game is None:
        return jsonify({'error': 'no game'}), 400

    data = request.json
    r = data.get('r')
    c = data.get('c')
    
    if r is None or c is None:
        return jsonify({'error': 'missing_coordinates'}), 400
    if not game.in_bounds(r, c):
        return jsonify({'error': 'invalid_coordinates'}), 400

    flagged = game.toggle_flag(r, c)
    if flagged is None:
        return jsonify({'error': 'invalid_move'}), 400
    session['grid'] = game_to_dict(game)

    return jsonify({'status': 'success', 'is_flagged': flagged})

if __name__ == '__main__':
    app.run(debug=True)
