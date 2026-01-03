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
        self.humanization_delay = (0.1, 0.5)
        self.bullet_mode = False
        self.move_count = 0
        self.current_elo = 2850
        self.pending_elo = 2850
        self.last_position_played = None  # Position where we last made a move

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
        self.current_elo = elo
        if self.engine:
            self.engine.set_elo_rating(elo)
            self.log(f"ELO: {elo}")
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
        self.last_position_played = None
        self.thread = threading.Thread(target=self._game_loop)
        self.thread.daemon = True
        self.thread.start()
        self.log("Bot started.")

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.engine = None
        self.vision = None
        self.board = None
        self.last_position_played = None
        self.log("Bot stopped.")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        state = "PAUSED" if self.is_paused else "RESUMED"
        self.log(f"Bot {state}")

    def get_smart_delay(self):
        if not self.bullet_mode:
            return random.uniform(*self.humanization_delay)
        
        self.move_count += 1
        
        if self.move_count <= 10:
            return random.uniform(0.01, 0.05)
            
        if random.random() < 0.05:
            hesitation = random.uniform(1.0, 1.5)
            self.log(f"Simulating hesitation... ({hesitation:.2f}s)")
            return hesitation
            
        return random.uniform(0.05, 1.0)

    def _game_loop(self):
        self.log("Initializing components...")
        self.vision = Vision()
        self.engine = ChessEngine()
        self.board = chess.Board()

        self.engine.set_elo_rating(self.current_elo)
        self.log(f"Engine ready: ELO {self.current_elo}")

        if self.engine.engine is None:
            self.log("Critical Error: Stockfish engine not found.")
            self.is_running = False
            return

        self.log("Looking for board (Visual)...")
        while self.is_running and self.vision.find_board() is None:
            time.sleep(1)
        
        if not self.is_running: 
            return
        self.log("Board found! Waiting for API connection...")

        api_url = "http://127.0.0.1:5000/get_state"
        waiting_logged = False
        
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
                    current_turn = data.get('turn', 'w')
                    
                    if not current_fen:
                        time.sleep(0.1)
                        continue
                    
                    # Get position (without turn info)
                    position = current_fen.split(' ')[0]
                    
                    # Determine our side
                    is_white = (player_color == 'white')
                    our_turn_char = 'w' if is_white else 'b'
                    
                    # Check if it's our turn
                    is_our_turn = (current_turn == our_turn_char)
                    
                    # Key logic: Play if it's our turn AND position is different from where we last played
                    # This prevents playing twice on the same position
                    if is_our_turn and position != self.last_position_played:
                        waiting_logged = False
                        
                        # Build corrected FEN
                        corrected_fen = f"{position} {current_turn} KQkq - 0 1"
                        
                        try:
                            self.board.set_fen(corrected_fen)
                        except Exception as e:
                            self.log(f"Invalid FEN: {e}")
                            time.sleep(0.2)
                            continue
                        
                        self.log(f"My Turn ({'White' if is_white else 'Black'})")
                        
                        # Check if game is over
                        if self.board.is_game_over():
                            outcome = self.board.outcome()
                            if outcome:
                                self.log(f"Game Over: {outcome.termination.name}")
                            else:
                                self.log("Game Over")
                            self.board = chess.Board()
                            self.move_count = 0
                            self.last_position_played = None
                            self.log("Waiting for new game...")
                            time.sleep(1)
                            continue
                        
                        # Get best move
                        best_move_uci = self.engine.get_best_move(corrected_fen)
                        if best_move_uci:
                            self.log(f"Best move: {best_move_uci}")
                            
                            # Delay
                            delay = self.get_smart_delay()
                            self.log(f"Waiting {delay:.2f}s...")
                            time.sleep(delay)
                            
                            if not self.is_running or self.is_paused:
                                continue
                            
                            # Re-verify state after delay
                            try:
                                verify = requests.get(api_url, timeout=0.3)
                                if verify.status_code == 200:
                                    vdata = verify.json()
                                    vfen = vdata.get('fen', '')
                                    vturn = vdata.get('turn', 'w')
                                    vpos = vfen.split(' ')[0] if vfen else ''
                                    
                                    # If position changed during delay, re-evaluate
                                    if vpos != position:
                                        self.log("Position changed during delay, re-evaluating...")
                                        continue
                                    
                                    # If no longer our turn, skip
                                    if vturn != our_turn_char:
                                        self.log("No longer our turn, skipping...")
                                        continue
                            except:
                                pass
                            
                            # Execute move
                            move = chess.Move.from_uci(best_move_uci)
                            x1, y1 = self.vision.get_square_center_from_index(move.from_square, is_white)
                            x2, y2 = self.vision.get_square_center_from_index(move.to_square, is_white)
                            
                            human_drag(x1, y1, x2, y2)
                            
                            # Handle promotion
                            if move.promotion:
                                time.sleep(0.15)
                                sq_size = self.vision.square_size
                                promo_y = y2 - int(sq_size * 0.4) if is_white else y2 + int(sq_size * 0.4)
                                human_click(x2, promo_y)
                                self.log(f"Promoted to {chess.piece_name(move.promotion).title()}")
                            
                            # IMPORTANT: Record this position so we don't play here again
                            self.last_position_played = position
                            self.board.push(move)
                            
                            self.log("Move executed, waiting for opponent...")
                        else:
                            self.log("No legal moves found.")
                            time.sleep(0.5)
                    else:
                        if not waiting_logged and not is_our_turn:
                            self.log("Opponent's turn...")
                            waiting_logged = True
                
            except requests.exceptions.Timeout:
                pass
            except Exception as e:
                self.log(f"Error: {e}")
                time.sleep(0.5)
            
            time.sleep(0.15)

# Singleton instance
bot = BotController()
