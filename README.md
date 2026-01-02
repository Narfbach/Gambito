# Gambito

Chess bot for Chess.com with computer vision, Stockfish integration, and humanized mouse movements.

## Features

- **Computer Vision**: Automatic board detection using OpenCV
- **Stockfish Engine**: Configurable ELO (1350-2850)
- **Humanized Input**: Bezier curve mouse movements with variable delays
- **Bullet Mode**: Smart timing for fast games (ultra-fast openings, random hesitations)
- **Dual Interface**: Native GUI (PySide6) + Web Dashboard (Flask)
- **Browser Bridge**: Userscript for real-time game state sync

## Requirements

- Python 3.10+
- Stockfish executable ([download](https://stockfishchess.org/download/))

## Installation

```bash
pip install -r requirements.txt
```

Download Stockfish and place `stockfish.exe` (or `stockfish` on Linux/Mac) in the project root.

## Usage

### GUI Mode (Recommended)

```bash
python gui.py
```

This starts both the native control panel and the Flask bridge server.

### Browser Setup

1. Install [Tampermonkey](https://www.tampermonkey.net/)
2. Create a new script with the contents of `connector.js`
3. Open Chess.com and start a game

## Architecture

```
┌─────────────────┐      ┌──────────────────┐
│   Chess.com     │──────│  connector.js    │
│   (Browser)     │      │  (Userscript)    │
└─────────────────┘      └────────┬─────────┘
                                  │ HTTP POST
                         ┌────────▼─────────┐
                         │    server.py     │
                         │  (Flask Bridge)  │
                         └────────┬─────────┘
                                  │ HTTP GET
┌─────────────────┐      ┌────────▼─────────┐
│    gui.py       │◄─────│ bot_controller   │
│  (PySide6 UI)   │      │  (Game Loop)     │
└─────────────────┘      └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
     ┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
     │   vision.py     │ │   engine.py     │ │    input.py     │
     │ (Board Detect)  │ │  (Stockfish)    │ │ (Mouse Control) │
     └─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Files

| File | Description |
|------|-------------|
| `gui.py` | Native PySide6 control panel |
| `bot_controller.py` | Core game loop and bot logic |
| `vision.py` | Board detection and move recognition |
| `engine.py` | Stockfish wrapper with ELO control |
| `input.py` | Humanized mouse movements |
| `server.py` | Flask bridge for browser communication |
| `connector.js` | Tampermonkey userscript for Chess.com |
| `app.py` | Web dashboard (alternative to gui.py) |

## Configuration

| Setting | Range | Default |
|---------|-------|---------|
| ELO Rating | 1350-2850 | 2850 |
| Min Delay | 0-5s | 0.1s |
| Max Delay | 0-10s | 0.5s |
| Bullet Mode | On/Off | Off |

## License

MIT
