import time
import random
import numpy as np

# Constants
BOARD_SIZE = 8
SQUARE_SIZE_GUESS = 100  # Initial guess, will be calculated dynamically
OFFSET_X = 0
OFFSET_Y = 0

# Colors (BGR format for OpenCV)
# These are approximate colors for the standard chess.com green board
# We will use these for color matching if needed, but edge detection is better
GREEN_SQUARE = (118, 150, 86)
WHITE_SQUARE = (238, 238, 210)

def random_delay(min_seconds=0.1, max_seconds=0.5):
    """Sleeps for a random amount of time."""
    time.sleep(random.uniform(min_seconds, max_seconds))

def euclidean_distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
