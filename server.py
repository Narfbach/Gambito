from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Disable Flask logging to keep console clean
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Global state
current_fen = None
player_color = None # 'white' or 'black'

@app.route('/update_fen', methods=['POST'])
def update_fen():
    global current_fen, player_color
    data = request.json
    if data:
        current_fen = data.get('fen')
        player_color = data.get('color')
        # print(f"Received FEN: {current_fen} (Color: {player_color})")
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/get_state', methods=['GET'])
def get_state():
    global current_fen, player_color
    return jsonify({
        "fen": current_fen,
        "color": player_color
    }), 200

if __name__ == '__main__':
    print("Starting Chess Bot Server on port 5000...")
    app.run(host='127.0.0.1', port=5000)
