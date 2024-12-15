class CheckersUI {
    constructor() {
        this.selectedPiece = null;
        this.gameId = null;
        this.board = document.getElementById('board');
        this.status = document.getElementById('status');
        this.socket = io();
        this.playerColor = null;
        this.setupSocketListeners();
        
        document.getElementById('new-game').addEventListener('click', () => {
            console.log('Starting new game...');
            this.startNewGame();
        });
        this.updatePieceSizes = this.updatePieceSizes.bind(this);
        window.addEventListener('resize', this.updatePieceSizes);
        this.updatePieceSizes();

        const joinBtn = document.createElement('button');
        joinBtn.textContent = 'Join Game';
        joinBtn.onclick = () => this.joinGame(prompt('Enter game ID:'));
        document.querySelector('.info-panel').appendChild(joinBtn);
    }

    renderBoard(board) {
        console.log('Rendering board:', board); // Debug log
        if (!board) return;
        
        this.board.innerHTML = '';
        
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const piece = board[row][col];
                if (piece) {
                    const pieceElement = document.createElement('div');
                    pieceElement.className = 'piece';
                    pieceElement.dataset.row = row;
                    pieceElement.dataset.col = col;
                    pieceElement.dataset.color = piece.color;
                    
                    const imageName = `${piece.color}-${piece.king ? 'king' : 'piece'}.png`;
                    pieceElement.style.backgroundImage = `url('/static/images/${imageName}')`;
                    
                    pieceElement.style.top = `${row * 12.5}%`;
                    pieceElement.style.left = `${col * 12.5}%`;
                    
                    if (piece.color === this.playerColor) {
                        pieceElement.addEventListener('click', (e) => this.handlePieceClick(e));
                    }
                    
                    this.board.appendChild(pieceElement);
                }
            }
        }
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('player_joined', (data) => {
            console.log('Player joined, data received:', data); // Debug log
            this.renderBoard(data.board);
            this.status.textContent = 'Game started! Red moves first.';
        });
    }


    async joinGame(gameId) {
        try {
            const response = await fetch(`/join-game/${gameId}`);
            const data = await response.json();
            if (data.success) {
                this.gameId = gameId;
                this.playerColor = 'black';
                this.socket.emit('join_game', { game_id: gameId });
            } else {
                alert('Could not join game');
            }
        } catch (error) {
            console.error('Error joining game:', error);
        }
    }

    async startNewGame() {
        try {
            const response = await fetch('/create-game');
            const data = await response.json();
            this.gameId = data.game_id;
            this.playerColor = 'red';
            this.socket.emit('join_game', { game_id: this.gameId });
            this.status.textContent = 'Waiting for opponent...';
            console.log('Created game:', this.gameId);
        } catch (error) {
            console.error('Error creating game:', error);
        }
    }

    handlePieceClick(event) {
        const piece = event.target;
        
        // Clear previous selection
        document.querySelectorAll('.piece.selected').forEach(p => p.classList.remove('selected'));
        document.querySelectorAll('.valid-move').forEach(m => m.remove());
        
        if (piece.dataset.color === 'red') {
            piece.classList.add('selected');
            this.selectedPiece = {
                row: parseInt(piece.dataset.row),
                col: parseInt(piece.dataset.col)
            };
            this.showValidMoves(this.selectedPiece);
        }
    }

    makeMove(start, end) {
        if (this.playerColor !== this.currentPlayer) {
            return;
        }
        
        this.socket.emit('make_move', {
            game_id: this.gameId,
            start: start,
            end: end
        });
    }

    async showAIMoves(moves, finalBoard) {
        // Show each move with a delay
        for (let i = 0; i < moves.length; i++) {
            const [start, end] = moves[i];
            
            // Highlight the piece that's moving
            const piece = document.querySelector(`.piece[data-row="${start[0]}"][data-col="${start[1]}"]`);
            if (piece) piece.classList.add('moving');
            
            // Wait a moment to show the highlight
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Update the piece position
            if (piece) {
                piece.style.top = `${end[0] * 12.5}%`;
                piece.style.left = `${end[1] * 12.5}%`;
                piece.dataset.row = end[0];
                piece.dataset.col = end[1];
            }
            
            // Wait for the move animation to complete
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Remove the highlight
            if (piece) piece.classList.remove('moving');
        }
        this.renderBoard(finalBoard);
    }

    showValidMoves(piece) {
        const possibleMoves = [
            [piece.row - 1, piece.col - 1],
            [piece.row - 1, piece.col + 1],
            [piece.row - 2, piece.col - 2],
            [piece.row - 2, piece.col + 2]
        ];
        
        possibleMoves.forEach(([row, col]) => {
            if (row >= 0 && row < 8 && col >= 0 && col < 8) {
                const moveMarker = document.createElement('div');
                moveMarker.className = 'valid-move';
                // Center in the target square
                moveMarker.style.top = `${row * 12.5 + 6.25}%`;  // Add half square size (12.5/2)
                moveMarker.style.left = `${col * 12.5 + 6.25}%`; // Add half square size (12.5/2)
                moveMarker.addEventListener('click', () => {
                    this.makeMove([piece.row, piece.col], [row, col]);
                });
                this.board.appendChild(moveMarker);
            }
        });
    }

    updatePieceSizes() {
        const board = document.getElementById('board');
        const boardRect = board.getBoundingClientRect();
        const squareSize = boardRect.width / 8;
        const pieceSize = squareSize * 0.7; // Reduced from 0.8 to 0.7 for better fit
        
        document.documentElement.style.setProperty('--square-size', `${squareSize}px`);
        document.documentElement.style.setProperty('--piece-size', `${pieceSize}px`);
        document.documentElement.style.setProperty('--piece-margin', `${(squareSize - pieceSize) / 2}px`);
    }

    

}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing game...');
    const game = new CheckersUI();
    game.startNewGame();
});