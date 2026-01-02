import cv2
import numpy as np
import pyautogui
from utils import BOARD_SIZE, GREEN_SQUARE, WHITE_SQUARE

class Vision:
    def __init__(self):
        self.board_top_left = None
        self.square_size = None
        self.board_image = None

    def take_screenshot(self):
        """Captures the screen and converts it to an OpenCV image."""
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def find_board(self, image=None):
        """
        Locates the chessboard on the screen.
        Returns (x, y, width, height) of the board or None if not found.
        """
        if image is None:
            image = self.take_screenshot()

        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply GaussianBlur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours to find the board
        # We are looking for a large square
        possible_boards = []
        
        height, width = image.shape[:2]
        min_area = (height // 4) * (height // 4) # Assume board is at least 1/4 of screen height squared

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                perimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
                
                # Check if it has 4 corners
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = float(w) / h
                    
                    # Check if it's roughly square (0.95 to 1.05)
                    if 0.95 <= aspect_ratio <= 1.05:
                        possible_boards.append((x, y, w, h, area))

        if not possible_boards:
            print("No board candidates found via contours.")
            return None

        # Sort by area, largest first. The board is likely the largest square container.
        possible_boards.sort(key=lambda x: x[4], reverse=True)
        
        # Pick the largest one
        bx, by, bw, bh, _ = possible_boards[0]
        
        self.board_top_left = (bx, by)
        self.square_size = bw / BOARD_SIZE
        print(f"Board found at: {bx}, {by}, size: {bw}x{bh}, square size: {self.square_size}")
        return bx, by, bw, bh

    def detect_side(self, image):
        """
        Detects if the player is playing as White or Black.
        Checks the color of the pieces in the bottom row (Rank 1 or 8).
        Returns True if White, False if Black.
        """
        if self.board_top_left is None or self.square_size is None:
            return True # Default to White
            
        bx, by = self.board_top_left
        s = self.square_size
        
        # Sample bottom row (Visual row 7), middle columns (d, e -> indices 3, 4)
        # If White: Bottom row has White King/Queen.
        # If Black: Bottom row has Black King/Queen.
        
        white_pixels = 0
        black_pixels = 0
        
        for col in [3, 4]: # Check King and Queen files
            x = int(bx + col * s)
            y = int(by + 7 * s) # Bottom row
            
            # Crop center
            roi = image[y+int(s*0.3):y+int(s*0.7), x+int(s*0.3):x+int(s*0.7)]
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Count bright and dark pixels
            white_pixels += np.sum(gray > 200)
            black_pixels += np.sum(gray < 80)
            
        print(f"Side Detection - White Pixels: {white_pixels}, Black Pixels: {black_pixels}")
        
        if white_pixels > black_pixels:
            print("Detected side: WHITE")
            return True
        else:
            print("Detected side: BLACK")
            return False

    def get_square_center_from_index(self, square_idx, is_white_perspective=True):
        """
        Returns (x, y) for a given chess square index (0-63).
        Handles perspective flipping.
        """
        if self.board_top_left is None or self.square_size is None:
            return 0, 0
            
        bx, by = self.board_top_left
        s = self.square_size
        
        if is_white_perspective:
            # White View:
            # A1 (0) is Bottom-Left (7, 0)
            # H8 (63) is Top-Right (0, 7)
            row = 7 - (square_idx // 8)
            col = square_idx % 8
        else:
            # Black View:
            # A1 (0) is Top-Right (0, 7)
            # H8 (63) is Bottom-Left (7, 0)
            row = square_idx // 8
            col = 7 - (square_idx % 8)
            
        center_x = int(bx + (col + 0.5) * s)
        center_y = int(by + (row + 0.5) * s)
        return center_x, center_y

    def get_square_image(self, image, rank, file):
        """Extracts the image of a specific square."""
        if self.board_top_left is None or self.square_size is None:
            return None
        
        bx, by = self.board_top_left
        x = int(bx + file * self.square_size)
        y = int(by + rank * self.square_size)
        s = int(self.square_size)
        
        return image[y:y+s, x:x+s]

    def get_square_status(self, image, rank, file):
        """
        Returns the status of a square: 'empty', 'white', 'black'.
        Based on color variance and brightness analysis.
        """
        if self.board_top_left is None or self.square_size is None:
            return 'empty'
            
        bx, by = self.board_top_left
        s = self.square_size
        x = int(bx + file * s)
        y = int(by + rank * s)
        
        # Crop center 40% (to avoid square color, focus on piece)
        roi = image[y+int(s*0.3):y+int(s*0.7), x+int(s*0.3):x+int(s*0.7)]
        if roi.size == 0:
            return 'empty'
        
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray_roi)
        std_dev = np.std(gray_roi)
        
        # Low variance indicates empty square
        if std_dev < 25:
            return 'empty'
        
        # High brightness = white piece, low = black piece
        if avg_brightness > 120:
            return 'white'
        else:
            return 'black'

    def is_square_occupied_by_our_color(self, image, square_idx, is_white_perspective, is_white_turn):
        """
        Checks if the given square index is occupied by a piece of our color.
        Returns True if it looks like our piece, False otherwise.
        """
        if self.board_top_left is None or self.square_size is None:
            return False

        row, col = self.get_row_col(square_idx, is_white_perspective)
        
        bx, by = self.board_top_left
        s = self.square_size
        x = int(bx + col * s)
        y = int(by + row * s)
        
        # Crop center 50%
        roi = image[y+int(s*0.25):y+int(s*0.75), x+int(s*0.25):x+int(s*0.75)]
        if roi.size == 0: return False
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 1. Check if Empty (Low Variance)
        std_dev = np.std(gray)
        # Empty squares usually have very low variance (solid color)
        # Pieces have high variance (texture, borders)
        if std_dev < 25: 
            print(f"Validation: Square {square_idx} seems empty (StdDev: {std_dev:.2f})")
            return False
            
        # 2. Check Color (Brightness)
        avg_brightness = np.mean(gray)
        print(f"Validation: Square {square_idx} Occupied. Brightness: {avg_brightness:.2f}, StdDev: {std_dev:.2f}")
        
        # Heuristic:
        # White pieces are bright (> 150?)
        # Black pieces are dark (< 100?)
        # This depends heavily on the board theme.
        
        is_piece_white = avg_brightness > 120 
        
        return is_piece_white == is_white_turn

    def get_square_color_prominent(self, image, square_idx, is_white_perspective):
        """
        Returns 'white', 'black', or 'empty' based on pixel statistics.
        """
        if self.board_top_left is None or self.square_size is None:
            return 'empty'

        row, col = self.get_row_col(square_idx, is_white_perspective)
        
        bx, by = self.board_top_left
        s = self.square_size
        x = int(bx + col * s)
        y = int(by + row * s)
        
        # Crop center 50%
        roi = image[y+int(s*0.25):y+int(s*0.75), x+int(s*0.25):x+int(s*0.75)]
        if roi.size == 0: return 'empty'
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        std_dev = np.std(gray)
        
        if std_dev < 25: 
            return 'empty'
            
        avg_brightness = np.mean(gray)
        if avg_brightness > 120:
            return 'white'
        else:
            return 'black'

    def get_row_col(self, square_idx, is_white_perspective):
        if is_white_perspective:
            row = 7 - (square_idx // 8)
            col = square_idx % 8
        else:
            row = square_idx // 8
            col = 7 - (square_idx % 8)
        return row, col

    def detect_move(self, before_image, after_image, legal_moves, is_white_perspective=True):
        """
        Robust Move Detection v3:
        1. Identify changed squares via Diff.
        2. Filter legal moves that match the changed squares.
        3. Verify the move logic:
           - Source square should become Empty (or match board color).
           - Target square should become Occupied (by the moving piece's color).
        """
        if before_image is None or after_image is None:
            return None

        # 1. Diff
        gray_before = cv2.cvtColor(before_image, cv2.COLOR_BGR2GRAY)
        gray_after = cv2.cvtColor(after_image, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray_before, gray_after)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        
        changed_squares = []
        bx, by = self.board_top_left
        s = self.square_size
        
        for r in range(8):
            for c in range(8):
                x = int(bx + c * s)
                y = int(by + r * s)
                roi = thresh[y+int(s*0.2):y+int(s*0.8), x+int(s*0.2):x+int(s*0.8)]
                score = np.sum(roi)
                # Threshold: 5% of the maximum possible score for this ROI
                max_score = roi.size * 255
                threshold = max_score * 0.05
                
                if score > threshold: 
                    print(f"Square {chr(97+c)}{8-r} changed. Score: {score}/{max_score} ({score/max_score:.2%})")
                    changed_squares.append((r, c))
        
        print(f"Changed squares: {changed_squares}")
        
        if len(changed_squares) < 2:
            return None
            
        # 2. Match Legal Moves
        candidates = []
        
        def get_row_col(square_idx):
            if is_white_perspective:
                # White View: A1 (0) is Bottom-Left (7, 0)
                row = 7 - (square_idx // 8)
                col = square_idx % 8
            else:
                # Black View: A1 (0) is Top-Right (0, 7)
                row = square_idx // 8
                col = 7 - (square_idx % 8)
            return row, col

        for move in legal_moves:
            r1, c1 = get_row_col(move.from_square)
            r2, c2 = get_row_col(move.to_square)
            
            # Check if from and to are in changed_squares
            if (r1, c1) in changed_squares and (r2, c2) in changed_squares:
                candidates.append(move)
                
        if not candidates:
            return None
            
        if len(candidates) == 1:
            print(f"Unique candidate found: {candidates[0]}")
            return candidates[0]
            
        # 3. Disambiguate (if multiple candidates, e.g. capture vs move)
        # Usually the move with the highest combined change score is the real one.
        # Or we can check pixel colors.
        
        # For now, return the first one or the one with max score.
        # Let's recalculate scores for candidates.
        best_move = None
        max_score = -1
        
        for move in candidates:
            r1, c1 = get_row_col(move.from_square)
            r2, c2 = get_row_col(move.to_square)
            
            def get_score(r, c):
                x = int(bx + c * s)
                y = int(by + r * s)
                roi = thresh[y+int(s*0.2):y+int(s*0.8), x+int(s*0.2):x+int(s*0.8)]
                return np.sum(roi)
                
            score = get_score(r1, c1) + get_score(r2, c2)
            if score > max_score:
                max_score = score
                best_move = move
                
        print(f"Best candidate: {best_move}")
        return best_move
