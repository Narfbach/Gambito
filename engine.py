from stockfish import Stockfish
import os

class ChessEngine:
    def __init__(self, stockfish_path="stockfish.exe"):
        # Paths to check:
        # 1. Provided path
        # 2. Current working directory
        # 3. Directory where this script is located (chess_bot folder)
        
        possible_paths = [
            stockfish_path,
            os.path.join(os.getcwd(), stockfish_path),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), stockfish_path)
        ]
        
        # Also look for any .exe starting with stockfish in these directories
        search_dirs = [
            os.getcwd(),
            os.path.dirname(os.path.abspath(__file__))
        ]

        final_path = None
        
        # Check exact matches first
        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                final_path = path
                break
        
        # If not found, search for wildcard stockfish*.exe
        if not final_path:
            for directory in search_dirs:
                if not os.path.exists(directory): continue
                for file in os.listdir(directory):
                    if file.lower().startswith("stockfish") and file.lower().endswith(".exe"):
                        final_path = os.path.join(directory, file)
                        print(f"Auto-detected Stockfish: {final_path}")
                        break
                if final_path: break

        if not final_path:
            print(f"Warning: Stockfish not found. Checked in: {search_dirs}")
        else:
            stockfish_path = final_path
        
        try:
            self.engine = Stockfish(path=stockfish_path)
            # Default to a moderate level
            self.set_elo_rating(1350)
        except Exception as e:
            print(f"Error initializing Stockfish: {e}")
            self.engine = None

    def set_elo_rating(self, elo):
        """
        Sets the engine ELO rating using UCI_LimitStrength and UCI_Elo.
        Also adjusts depth to match the ELO level.
        """
        if self.engine:
            # Ensure ELO is within valid bounds (1350 - 2850)
            elo = max(1350, min(2850, elo))
            
            # Update UCI options
            print(f"DEBUG: Setting UCI_LimitStrength=true, UCI_Elo={elo}")
            self.engine.update_engine_parameters({
                "UCI_LimitStrength": "true",
                "UCI_Elo": elo
            })
            
            # Verify parameters
            params = self.engine.get_parameters()
            print(f"DEBUG: Current Engine Params: LimitStrength={params.get('UCI_LimitStrength')}, Elo={params.get('UCI_Elo')}")

            # Dynamic Depth Adjustment
            # 1350 -> Depth 1
            # 2850 -> Depth 15
            # Formula: 1 + (elo - 1350) / (2850 - 1350) * 14
            depth = int(1 + (elo - 1350) / 1500 * 14)
            self.engine.set_depth(depth)
            
            print(f"Engine configured: ELO={elo}, Depth={depth}")

    def set_skill_level(self, level):
        """
        Legacy method. Use set_elo_rating instead.
        """
        pass

    def get_best_move(self, fen):
        """
        Returns the best move for the given FEN.
        """
        if self.engine:
            self.engine.set_fen_position(fen)
            return self.engine.get_best_move()
        return None

    def is_move_correct(self, fen, move):
        """
        Checks if a move is valid/good.
        """
        if self.engine:
            self.engine.set_fen_position(fen)
            return self.engine.is_move_correct(move)
        return False
