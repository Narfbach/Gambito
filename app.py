from flask import Flask, render_template, jsonify
from bot_controller import bot
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_bot():
    bot.start()
    return jsonify({"status": "started"})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    bot.stop()
    return jsonify({"status": "stopped"})

@app.route('/api/pause', methods=['POST'])
def pause_bot():
    bot.toggle_pause()
    return jsonify({"status": "paused" if bot.is_paused else "resumed"})

@app.route('/api/status')
def get_status():
    return jsonify({
        "running": bot.is_running,
        "paused": bot.is_paused,
        "logs": bot.log_messages[-10:] # Send last 10 logs
    })

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
