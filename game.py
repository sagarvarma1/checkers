from typing import List, Tuple, Optional, Dict
import json

class CheckersGame:
    def __init__(self):
        self.board = self.create_board()
        self.current_player = 'red'
        self.red_pieces = 12
        self.black_pieces = 12

    def create_board(self) -> List[List[Optional[dict]]]:
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Place black pieces
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = {'color': 'black', 'king': False}
        
        # Place red pieces
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = {'color': 'red', 'king': False}
        
        return board

    def get_valid_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        if self.board[row][col] is None or self.board[row][col]['color'] != self.current_player:
            return []

        piece = self.board[row][col]
        moves = []
        jumps = []
        
        # Determine possible move directions based on piece type
        directions = []
        if piece['color'] == 'red' or piece['king']:
            directions.extend([(-1, -1), (-1, 1)])  # Up-left and up-right
        if piece['color'] == 'black' or piece['king']:
            directions.extend([(1, -1), (1, 1)])    # Down-left and down-right

        # Check for jumps first (they're mandatory)
        for dr, dc in directions:
            # Check jump moves
            jump_row, jump_col = row + dr, col + dc
            if 0 <= jump_row < 8 and 0 <= jump_col < 8:
                if (self.board[jump_row][jump_col] is not None and 
                    self.board[jump_row][jump_col]['color'] != piece['color']):
                    land_row, land_col = jump_row + dr, jump_col + dc
                    if (0 <= land_row < 8 and 0 <= land_col < 8 and 
                        self.board[land_row][land_col] is None):
                        jumps.append((land_row, land_col))

        # If no jumps are available, check regular moves
        if not jumps:
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if self.board[new_row][new_col] is None:
                        moves.append((new_row, new_col))

        # Return jumps if available (they're mandatory), otherwise return regular moves
        return jumps if jumps else moves

    def make_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        start_row, start_col = start
        end_row, end_col = end

        # Validate basic move parameters
        if (not (0 <= start_row < 8 and 0 <= start_col < 8 and 
                0 <= end_row < 8 and 0 <= end_col < 8)):
            return False

        if self.board[start_row][start_col] is None:
            return False

        piece = self.board[start_row][start_col]
        if piece['color'] != self.current_player:
            return False

        valid_moves = self.get_valid_moves(start_row, start_col)
        if (end_row, end_col) not in valid_moves:
            return False

        # Execute the move
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = None

        # Handle jumps
        if abs(end_row - start_row) == 2:
            jumped_row = (start_row + end_row) // 2
            jumped_col = (start_col + end_col) // 2
            jumped_piece = self.board[jumped_row][jumped_col]['color']
            self.board[jumped_row][jumped_col] = None
            
            # Update piece counts
            if jumped_piece == 'red':
                self.red_pieces -= 1
            else:
                self.black_pieces -= 1

        # Handle king promotion
        if (end_row == 0 and piece['color'] == 'red') or (end_row == 7 and piece['color'] == 'black'):
            piece['king'] = True

        # Switch turns
        self.current_player = 'black' if self.current_player == 'red' else 'red'
        return True

    def get_winner(self) -> Optional[str]:
        if self.red_pieces == 0:
            return 'black'
        if self.black_pieces == 0:
            return 'red'
        
        # Check if current player has any valid moves
        has_moves = False
        for row in range(8):
            for col in range(8):
                if (self.board[row][col] is not None and 
                    self.board[row][col]['color'] == self.current_player and 
                    self.get_valid_moves(row, col)):
                    has_moves = True
                    break
            if has_moves:
                break
        
        if not has_moves:
            return 'black' if self.current_player == 'red' else 'red'
            
        return None

    def get_all_valid_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        all_moves = []
        for row in range(8):
            for col in range(8):
                if (self.board[row][col] is not None and 
                    self.board[row][col]['color'] == color):
                    moves = self.get_valid_moves(row, col)
                    all_moves.extend([((row, col), move) for move in moves])
        return all_moves

    def to_json(self) -> str:
        """Convert game state to JSON for web transmission"""
        return json.dumps({
            'board': self.board,
            'current_player': self.current_player,
            'red_pieces': self.red_pieces,
            'black_pieces': self.black_pieces
        })

class SimpleAI:
    def get_move(self, game: CheckersGame) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        valid_moves = game.get_all_valid_moves('black')
        if not valid_moves:
            return None

        # Evaluate each move
        best_score = float('-inf')
        best_move = None

        for start, end in valid_moves:
            score = self.evaluate_move(game, start, end)
            if score > best_score:
                best_score = score
                best_move = (start, end)

        return best_move

    def evaluate_move(self, game: CheckersGame, start: Tuple[int, int], end: Tuple[int, int]) -> float:
        score = 0
        start_row, start_col = start
        end_row, end_col = end

        # Prefer jumps (capturing pieces)
        if abs(end_row - start_row) == 2:
            score += 10

        # Prefer moves towards becoming a king
        if not game.board[start_row][start_col]['king']:
            if game.board[start_row][start_col]['color'] == 'black':
                score += end_row * 0.5  # Prefer moving towards the bottom
            else:
                score += (7 - end_row) * 0.5  # Prefer moving towards the top

        # Prefer keeping pieces on the edges (harder to capture)
        if end_col == 0 or end_col == 7:
            score += 0.5

        # Prefer moves that protect pieces
        if self.is_protected(game, end_row, end_col):
            score += 0.3

        return score

    def is_protected(self, game: CheckersGame, row: int, col: int) -> bool:
        """Check if a position is protected by nearby friendly pieces"""
        if row < 0 or row >= 8 or col < 0 or col >= 8:
            return False

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < 8 and 0 <= new_col < 8 and 
                game.board[new_row][new_col] is not None and 
                game.board[new_row][new_col]['color'] == 'black'):
                return True
        return False