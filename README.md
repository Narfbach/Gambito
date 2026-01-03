# Gambito

Chess bot for Chess.com with computer vision, Stockfish integration, and humanized mouse movements.

## Features

- **Computer Vision**: Automatic board detection using OpenCV
- **Stockfish Engine**: Configurable ELO (1350-2850) with auto-restart on crash
- **Humanized Input**: Bezier curve mouse movements with variable delays
- **Bullet Mode**: Smart timing for fast games (ultra-fast openings, random hesitations)
- **Global Hotkeys**: Control the bot from anywhere (F6 Start, F7 Pause, F8 Stop)
- **Chrome Extension**: Reliable board state detection via DOM parsing
- **FEN Validation**: Automatic correction of invalid FEN positions

## Requirements

- Python 3.10+
- Stockfish executable ([download](https://stockfishchess.org/download/))
- Google Chrome

## Installation

```bash
pip install -r requirements.txt
```

Download Stockfish and place `stockfish.exe` (or `stockfish` on Linux/Mac) in the project root.

### Chrome Extension Setup

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `chrome-extension` folder from this project
5. The extension will automatically activate on Chess.com

## Usage

### GUI Mode (Recommended)

```bash
python gui.py
```

This starts both the native control panel and the Flask bridge server.

### Global Hotkeys

| Key | Action |
|-----|--------|
| **F6** | Start bot |
| **F7** | Pause/Resume |
| **F8** | Stop bot |

## Architecture

```
┌─────────────────┐      ┌──────────────────┐
│   Chess.com     │──────│ Chrome Extension │
│   (Browser)     │      │  (content.js)    │
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
| `gui.py` | Native PySide6 control panel with hotkeys |
| `bot_controller.py` | Core game loop and bot logic |
| `vision.py` | Board detection and move execution |
| `engine.py` | Stockfish wrapper with ELO control and FEN validation |
| `input.py` | Humanized mouse movements |
| `server.py` | Flask bridge for browser communication |
| `chrome-extension/` | Chrome extension for Chess.com integration |

## Configuration

| Setting | Range | Default |
|---------|-------|---------|
| ELO Rating | 1350-2850 | 2850 |
| Min Delay | 0-5s | 0.1s |
| Max Delay | 0-10s | 0.5s |
| Bullet Mode | On/Off | Off |

## License

MIT
