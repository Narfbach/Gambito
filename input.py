"""Human-like mouse movement using Bezier curves."""
import pyautogui
import random
import time
import numpy as np

# Disable pyautogui fail-safe to allow corner movement if necessary, 
# but usually good to keep on. We'll keep it on for safety.
pyautogui.FAILSAFE = True

def get_point_on_curve(p0, p1, p2, p3, t):
    """
    Cubic Bezier curve formula.
    """
    return (1-t)**3 * p0 + 3*(1-t)**2 * t * p1 + 3*(1-t) * t**2 * p2 + t**3 * p3

def human_move_mouse(target_x, target_y, duration=None):
    """
    Moves the mouse to (target_x, target_y) using a human-like path (Bezier curve).
    """
    start_x, start_y = pyautogui.position()
    
    # If already there, just return
    if start_x == target_x and start_y == target_y:
        return

    # Randomize duration if not provided, based on distance
    distance = np.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
    if duration is None:
        # Faster for short distances, slower for long
        duration = random.uniform(0.3, 0.8) + (distance / 2000.0)

    # Control points for Bezier curve
    # We want the curve to be somewhat random but generally forward
    # P0 is start, P3 is end
    p0 = np.array([start_x, start_y])
    p3 = np.array([target_x, target_y])

    # P1 and P2 are control points. 
    # We'll place them somewhat randomly between start and end, with some perpendicular offset
    
    # Vector from start to end
    vec = p3 - p0
    perp_vec = np.array([-vec[1], vec[0]]) # Perpendicular vector
    
    # Normalize perp_vec
    if np.linalg.norm(perp_vec) != 0:
        perp_vec = perp_vec / np.linalg.norm(perp_vec)
    
    # Random offsets
    offset1 = random.uniform(-100, 100)
    offset2 = random.uniform(-100, 100)
    
    p1 = p0 + vec * random.uniform(0.2, 0.4) + perp_vec * offset1
    p2 = p0 + vec * random.uniform(0.6, 0.8) + perp_vec * offset2

    # Generate points along the curve
    steps = int(duration * 60) # 60 FPS roughly
    if steps < 10: steps = 10
    
    points = []
    for i in range(steps + 1):
        t = i / steps
        # Apply easing to t (ease-in-out) to simulate acceleration/deceleration
        # Sigmoid-like function or simple smoothstep
        t_eased = t * t * (3 - 2 * t) 
        
        point = get_point_on_curve(p0, p1, p2, p3, t_eased)
        points.append(point)

    # Execute movement
    # We can use pyautogui.moveTo for each point with 0 duration, 
    # but sleeping manually gives more control
    
    start_time = time.time()
    for i, point in enumerate(points):
        pyautogui.moveTo(point[0], point[1], _pause=False)
        # Small sleep to match duration, but pyautogui overhead might be enough
        # Let's try to sync with time
        elapsed = time.time() - start_time
        target_time = (i / steps) * duration
        if elapsed < target_time:
            time.sleep(target_time - elapsed)

    # Ensure we land exactly on target
    pyautogui.moveTo(target_x, target_y, _pause=False)

def human_click(x=None, y=None):
    """
    Performs a human-like click.
    """
    if x is not None and y is not None:
        human_move_mouse(x, y)
    
    # Slight delay before down
    time.sleep(random.uniform(0.05, 0.15))
    pyautogui.mouseDown()
    # Hold for a bit
    time.sleep(random.uniform(0.05, 0.15))
    pyautogui.mouseUp()

def human_drag(start_x, start_y, end_x, end_y):
    """
    Drags from start to end.
    """
    human_move_mouse(start_x, start_y)
    time.sleep(random.uniform(0.05, 0.15))
    pyautogui.mouseDown()
    time.sleep(random.uniform(0.05, 0.15))
    human_move_mouse(end_x, end_y)
    time.sleep(random.uniform(0.05, 0.15))
    pyautogui.mouseUp()
