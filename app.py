from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO
from networking import GameNetwork
import secrets
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app)
game_network = GameNetwork(socketio)

@app.before_request
def before_request():
    if 'player_id' not in session:
        session['player_id'] = secrets.token_hex(8)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create-game')
def create_game():
    game_id = game_network.create_game(session['player_id'])
    return jsonify({'game_id': game_id})

@app.route('/join-game/<game_id>')
def join_game(game_id):
    success = game_network.join_game(game_id, session['player_id'])
    return jsonify({'success': success})

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {session['player_id']}")

@socketio.on('join_game')
def handle_join_game(data):
    game_id = data['game_id']
    join_room(game_id)
    emit('player_joined', {'player_id': session['player_id']}, room=game_id)

@socketio.on('make_move')
def handle_move(data):
    game_id = data['game_id']
    start = tuple(data['start'])
    end = tuple(data['end'])
    
    result = game_network.make_move(game_id, session['player_id'], start, end)
    if 'error' not in result:
        emit('move_made', result, room=game_id)
    else:
        emit('move_error', result, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)

@socketio.on('join_game')
def handle_join_game(data):
    print(f"Joining game: {data}")  # Debug print
    game_id = data['game_id']
    join_room(game_id)
    game_state = game_network.games[game_id]['game']
    print(f"Sending board state: {game_state.board}")  # Debug print
    emit('player_joined', {
        'player_id': session['player_id'],
        'board': game_state.board,
        'current_player': game_state.current_player
    }, room=game_id)