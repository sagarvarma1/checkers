from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Dict
from game import CheckersGame  # Add at the top of the file
from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Dict

class GameNetwork:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.games: Dict[str, dict] = {}  # game_id -> {players, game_obj}
        self.player_rooms: Dict[str, str] = {}  # player_id -> game_id

    def create_game(self, player_id: str) -> str:
        """Create a new game and return game_id"""
        game_id = str(len(self.games))
        self.games[game_id] = {
            'players': {'red': player_id, 'black': None},
            'game': CheckersGame(),
            'spectators': set()
        }
        self.player_rooms[player_id] = game_id
        return game_id

    def join_game(self, game_id: str, player_id: str) -> bool:
        """Join an existing game"""
        if game_id not in self.games:
            return False
            
        game = self.games[game_id]
        if game['players']['black'] is None:
            game['players']['black'] = player_id
            self.player_rooms[player_id] = game_id
            return True
        return False

    def spectate_game(self, game_id: str, spectator_id: str) -> bool:
        """Add a spectator to a game"""
        if game_id in self.games:
            self.games[game_id]['spectators'].add(spectator_id)
            self.player_rooms[spectator_id] = game_id
            return True
        return False

    def make_move(self, game_id: str, player_id: str, start: tuple, end: tuple) -> dict:
        """Process a move and return the updated game state"""
        game = self.games[game_id]
        
        # Verify it's the player's turn
        current_color = game['game'].current_player
        if game['players'][current_color] != player_id:
            return {'error': 'Not your turn'}
            
        # Make the move
        if not game['game'].make_move(start, end):
            return {'error': 'Invalid move'}
            
        # Return the new game state
        return {
            'board': game['game'].board,
            'current_player': game['game'].current_player,
            'winner': game['game'].get_winner()
        }