from stockfish import Stockfish
import os
import chess

class ChessEngine:
    def __init__(self, stockfish_path="stockfish.exe"):
        self.stockfish_path = None
        self.engine = None
        self.current_elo = 2850
        
        # Find stockfish executable
        possible_paths = [
            stockfish_path,
            os.path.join(os.getcwd(), stockfish_path),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), stockfish_path)
        ]
        
        search_dirs = [
            os.getcwd(),
            os.path.dirname(os.path.abspath(__file__))
        ]

        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                self.stockfish_path = path
                break
        
        if not self.stockfish_path:
            for directory in search_dirs:
                if not os.path.exists(directory):
                    continue
                for file in os.listdir(directory):
                    name_lower = file.lower()
                    if name_lower.startswith("stockfish") and (
                        name_lower.endswith(".exe") or 
                        not "." in name_lower
                    ):
                        self.stockfish_path = os.path.join(directory, file)
                        print(f"Auto-detected Stockfish: {self.stockfish_path}")
                        break
                if self.stockfish_path:
                    break

        if not self.stockfish_path:
            print(f"Warning: Stockfish not found. Checked in: {search_dirs}")
        else:
            self._init_engine()

    def _init_engine(self):
        """Initialize or reinitialize the Stockfish engine"""
        try:
            if self.engine:
                try:
                    self.engine.send_quit_command()
                except:
                    pass
            
            self.engine = Stockfish(path=self.stockfish_path)
            self.set_elo_rating(self.current_elo)
            print(f"Stockfish engine initialized (ELO: {self.current_elo})")
            return True
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            self.engine = None
            return False

    def _ensure_engine(self):
        """Ensure engine is running, restart if crashed"""
        if self.engine is None:
            return self._init_engine()
        
        try:
            self.engine.get_parameters()
            return True
        except:
            print("Stockfish crashed, restarting...")
            return self._init_engine()

    def _validate_and_fix_fen(self, fen):
        """Validate FEN and fix common issues"""
        try:
            parts = fen.split(' ')
            if len(parts) < 6:
                # Pad missing parts
                while len(parts) < 6:
                    if len(parts) == 1:
                        parts.append('w')  # Turn
                    elif len(parts) == 2:
                        parts.append('-')  # Castling
                    elif len(parts) == 3:
                        parts.append('-')  # En passant
                    elif len(parts) == 4:
                        parts.append('0')  # Halfmove
                    elif len(parts) == 5:
                        parts.append('1')  # Fullmove
            
            position = parts[0]
            turn = parts[1]
            castling = parts[2]
            
            # Use python-chess to validate and potentially correct castling rights
            try:
                board = chess.Board()
                board.set_fen(' '.join(parts))
                # If it works, the FEN is valid
                return fen
            except:
                # Try to fix castling rights based on actual piece positions
                board = chess.Board()
                board.set_board_fen(position)
                
                # Calculate valid castling rights
                valid_castling = ''
                
                # White kingside
                if (board.piece_at(chess.E1) == chess.Piece(chess.KING, chess.WHITE) and
                    board.piece_at(chess.H1) == chess.Piece(chess.ROOK, chess.WHITE)):
                    valid_castling += 'K'
                
                # White queenside
                if (board.piece_at(chess.E1) == chess.Piece(chess.KING, chess.WHITE) and
                    board.piece_at(chess.A1) == chess.Piece(chess.ROOK, chess.WHITE)):
                    valid_castling += 'Q'
                
                # Black kingside
                if (board.piece_at(chess.E8) == chess.Piece(chess.KING, chess.BLACK) and
                    board.piece_at(chess.H8) == chess.Piece(chess.ROOK, chess.BLACK)):
                    valid_castling += 'k'
                
                # Black queenside
                if (board.piece_at(chess.E8) == chess.Piece(chess.KING, chess.BLACK) and
                    board.piece_at(chess.A8) == chess.Piece(chess.ROOK, chess.BLACK)):
                    valid_castling += 'q'
                
                if not valid_castling:
                    valid_castling = '-'
                
                fixed_fen = f"{position} {turn} {valid_castling} - 0 1"
                
                # Verify the fixed FEN works
                try:
                    board.set_fen(fixed_fen)
                    return fixed_fen
                except:
                    # Last resort: no castling
                    return f"{position} {turn} - - 0 1"
                    
        except Exception as e:
            print(f"FEN validation error: {e}")
            return None

    def set_elo_rating(self, elo):
        """Sets the engine ELO rating"""
        elo = max(1350, min(2850, elo))
        self.current_elo = elo
        
        if self.engine:
            try:
                self.engine.update_engine_parameters({
                    "UCI_LimitStrength": "true",
                    "UCI_Elo": elo
                })
                
                depth = int(1 + (elo - 1350) / 1500 * 14)
                self.engine.set_depth(depth)
            except:
                pass
    
    def get_elo(self):
        return self.current_elo

    def set_skill_level(self, level):
        pass

    def get_best_move(self, fen):
        """Returns the best move for the given FEN, with error handling"""
        # Validate and potentially fix the FEN
        validated_fen = self._validate_and_fix_fen(fen)
        if not validated_fen:
            print(f"Could not validate FEN: {fen}")
            return None
        
        if not self._ensure_engine():
            return None
        
        try:
            self.engine.set_fen_position(validated_fen)
            move = self.engine.get_best_move()
            return move
        except Exception as e:
            print(f"Stockfish error with FEN '{validated_fen}': {e}")
            
            # Try to restart and retry once
            if self._init_engine():
                try:
                    self.engine.set_fen_position(validated_fen)
                    return self.engine.get_best_move()
                except Exception as e2:
                    print(f"Retry failed: {e2}")
            
            return None

    def is_move_correct(self, fen, move):
        """Checks if a move is valid"""
        validated_fen = self._validate_and_fix_fen(fen)
        if not validated_fen:
            return False
            
        if not self._ensure_engine():
            return False
        
        try:
            self.engine.set_fen_position(validated_fen)
            return self.engine.is_move_correct(move)
        except:
            return False
