from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Disable Flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Global state
current_fen = None
player_color = None
current_turn = None
move_count = 0

@app.route('/update_fen', methods=['POST'])
def update_fen():
    global current_fen, player_color, current_turn, move_count
    data = request.json
    if data:
        current_fen = data.get('fen')
        player_color = data.get('color')
        current_turn = data.get('turn', 'w')
        move_count = data.get('moveCount', 0)
        
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/get_state', methods=['GET'])
def get_state():
    global current_fen, player_color, current_turn, move_count
    return jsonify({
        "fen": current_fen,
        "color": player_color,
        "turn": current_turn,
        "moveCount": move_count
    }), 200

if __name__ == '__main__':
    print("Starting Chess Bot Server on port 5000...")
    app.run(host='127.0.0.1', port=5000)
