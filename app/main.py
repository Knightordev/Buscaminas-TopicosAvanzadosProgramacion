from flask import Flask, render_template
from game import Game


app = Flask(__name__)

@app.route('/')
def index():
    game = Game( 10, 10, 10)
    grid = game.get_grid()
    data={
        'title':'index',
        'page':'inicio'
    }
    return render_template('index.html', data=data, grid=grid)

if __name__ == '__main__':
    app.run(debug=True)