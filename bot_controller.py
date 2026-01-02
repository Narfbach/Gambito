import time
import random
import threading
import chess
import requests
from vision import Vision
from engine import ChessEngine
from input import human_drag, human_click

class BotController:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.thread = None
        self.vision = None
        self.engine = None
        self.board = None
        self.log_messages = []
        self.log_callback = None
        self.humanization_delay = (0.1, 0.5)  # Min, Max
        self.bullet_mode = False
        self.move_count = 0
        self.current_elo = 2850  # Track current ELO setting
        self.pending_elo = 2850  # ELO to apply when engine initializes

    def set_log_callback(self, callback):
        self.log_callback = callback

    def log(self, message):
        print(message)
        self.log_messages.append(message)
        if len(self.log_messages) > 50:
            self.log_messages.pop(0)
        if self.log_callback:
            self.log_callback(message)

    def set_elo(self, elo):
        """Sets the engine ELO and logs the change"""
        self.current_elo = elo
        if self.engine:
            self.engine.set_elo_rating(elo)
            self.log(f"✓ ELO: {elo}")
        else:
            self.pending_elo = elo

    def set_humanization_delay(self, min_delay, max_delay):
        self.humanization_delay = (min_delay, max_delay)
        self.log(f"Humanization delay set to {min_delay}-{max_delay}s")

    def set_bullet_mode(self, enabled):
        self.bullet_mode = enabled
        self.log(f"Bullet Mode: {'ON' if enabled else 'OFF'}")

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self.move_count = 0
        self.thread = threading.Thread(target=self._game_loop)
        self.thread.daemon = True
        self.thread.start()
        self.log("Bot started.")

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        # Cleanup resources
        self.engine = None
        self.vision = None
        self.board = None
        self.log("Bot stopped.")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        state = "PAUSED" if self.is_paused else "RESUMED"
        self.log(f"Bot {state}")

    def get_smart_delay(self):
        if not self.bullet_mode:
            return random.uniform(*self.humanization_delay)
        
        # Smart Timing Logic for Bullet
        self.move_count += 1
        
        # 1. Opening (Moves 1-10): Ultra Fast
        if self.move_count <= 10:
            return random.uniform(0.01, 0.05)
            
        # 2. Random Hesitation (5% chance)
        if random.random() < 0.05:
            hesitation = random.uniform(1.0, 1.5)
            self.log(f"Simulating hesitation... ({hesitation:.2f}s)")
            return hesitation
            
        # 3. Midgame: Fast but variable
        return random.uniform(0.05, 1.0)

    def _game_loop(self):
        self.log("Initializing components...")
        self.vision = Vision()
        self.engine = ChessEngine()
        self.board = chess.Board()

        # Apply ELO setting (from slider or default)
        self.engine.set_elo_rating(self.current_elo)
        self.log(f"✓ Engine ready: ELO {self.current_elo}")

        if self.engine.engine is None:
            self.log("Critical Error: Stockfish engine not found.")
            self.is_running = False
            return

        # 1. Find Board (Visual) - Still needed for clicking
        self.log("Looking for board (Visual)...")
        while self.is_running and self.vision.find_board() is None:
            time.sleep(1)
        
        if not self.is_running: return
        self.log("Board found! Waiting for API connection...")

        # 2. Wait for API (Game State)
        api_url = "http://127.0.0.1:5000/get_state"
        
        last_fen = None
        
        while self.is_running:
            if self.is_paused:
                time.sleep(0.5)
                continue

            try:
                response = requests.get(api_url, timeout=0.5)
                if response.status_code == 200:
                    data = response.json()
                    current_fen = data.get('fen')
                    player_color = data.get('color')
                    
                    if not current_fen:
                        time.sleep(0.1)
                        continue
                        
                    # Detect Side
                    is_white = (player_color == 'white')
                    
                    # Update Board
                    if current_fen != last_fen:
                        self.board.set_fen(current_fen)
                        last_fen = current_fen
                        self.log(f"Board Updated: {current_fen[:40]}...")
                        
                        # Check if game is over
                        if self.board.is_game_over():
                            outcome = self.board.outcome()
                            if outcome:
                                self.log(f"Game Over: {outcome.termination.name}")
                            else:
                                self.log("Game Over")
                            # Reset for next game
                            self.board = chess.Board()
                            self.move_count = 0
                            last_fen = None
                            self.log("Waiting for new game...")
                            continue
                        
                        # Check Turn
                        is_our_turn = (self.board.turn == chess.WHITE and is_white) or \
                                      (self.board.turn == chess.BLACK and not is_white)
                                      
                        if is_our_turn:
                            self.log(f"My Turn ({'White' if is_white else 'Black'})")
                            
                            # Think
                            best_move_uci = self.engine.get_best_move(current_fen)
                            if best_move_uci:
                                self.log(f"Best move: {best_move_uci}")
                                
                                # Smart Delay
                                delay = self.get_smart_delay()
                                self.log(f"Waiting {delay:.2f}s...")
                                time.sleep(delay)
                                
                                # Parse move
                                move = chess.Move.from_uci(best_move_uci)
                                x1, y1 = self.vision.get_square_center_from_index(move.from_square, is_white)
                                x2, y2 = self.vision.get_square_center_from_index(move.to_square, is_white)
                                
                                # Execute drag
                                human_drag(x1, y1, x2, y2)
                                
                                # Handle pawn promotion
                                if move.promotion:
                                    time.sleep(0.15)  # Wait for promotion dialog
                                    # Queen is first option in Chess.com selector
                                    # Dialog appears at destination square
                                    sq_size = self.vision.square_size
                                    if is_white:
                                        # White promotes on rank 8, dialog appears above
                                        promo_y = y2 - int(sq_size * 0.4)
                                    else:
                                        # Black promotes on rank 1, dialog appears below
                                        promo_y = y2 + int(sq_size * 0.4)
                                    human_click(x2, promo_y)
                                    self.log(f"Promoted to {chess.piece_name(move.promotion).title()}")
                                
                                # Optimistic update to prevent double move
                                self.board.push(move)
                                last_fen = self.board.fen() 
                            else:
                                self.log("No move found.")
                
            except Exception as e:
                self.log(f"API Error: {e}")
                time.sleep(1)
            
            time.sleep(0.1)

# Singleton instance
bot = BotController()
