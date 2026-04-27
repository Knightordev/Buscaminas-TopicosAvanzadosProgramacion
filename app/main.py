from flask import Flask, render_template, request, jsonify, session
from game import Game
import sqlite3  

app = Flask(__name__)
app.secret_key = 'buscaminas_secret'


def init_db(): 
    conn = sqlite3.connect("puntajes.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS puntajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        puntaje INTEGER
    )
    """)
    
    conn.commit()
    conn.close()

init_db() 

def guardar_puntaje(nombre, puntaje):  
    conn = sqlite3.connect("puntajes.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO puntajes (nombre, puntaje) VALUES (?, ?)",
        (nombre, puntaje)
    )

    conn.commit()
    conn.close()

def calcular_puntaje(game): 
    puntos = 0
    for r in range(game.r):
        for c in range(game.c):
            if game.grid[r][c].revealed and not game.grid[r][c].mine:
                puntos += 10
    return puntos

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
    session['nombre'] = "Jugador"  
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

    if cell.mine:
        cell.revealed = True
        session['grid'] = game_to_dict(game)
        
        puntaje = calcular_puntaje(game)
        guardar_puntaje(session.get('nombre', 'Jugador'), puntaje)
        return jsonify({'type': 'mine', 'puntaje': puntaje})
    
    revealed_cells = game.reveal(row, col)
    session['grid'] = game_to_dict(game)

    if revealed_cells is None:
        return jsonify({'error': 'invalid_move'}), 400
    return jsonify({'type': 'reveal', 'cells': revealed_cells})

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

@app.route('/puntajes')
def ver_puntajes(): 
    conn = sqlite3.connect("puntajes.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nombre, puntaje 
        FROM puntajes 
        ORDER BY puntaje DESC 
        LIMIT 10
    """)

    datos = cursor.fetchall()
    conn.close()

    return render_template("puntajes.html", puntajes=datos)

if __name__ == '__main__':
    app.run(debug=True)