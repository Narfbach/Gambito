/**
 * Gambito Chess Connector - Content Script v6
 * Based on A.C.A.S methods for accurate board reading
 */

(function () {
    'use strict';

    const SERVER_URL = "http://127.0.0.1:5000/update_fen";
    const POLL_INTERVAL = 100;

    let lastFenSent = "";
    let isConnected = false;
    let lastPlayerColor = null;

    console.log('%c[GAMBITO] Chess Connector v6.0', 'color: #5DADE2; font-weight: bold;');

    // Piece class to FEN mapping
    const PIECE_MAP = {
        'wp': 'P', 'wr': 'R', 'wn': 'N', 'wb': 'B', 'wq': 'Q', 'wk': 'K',
        'bp': 'p', 'br': 'r', 'bn': 'n', 'bb': 'b', 'bq': 'q', 'bk': 'k'
    };

    // Get the board element
    function getBoardElem() {
        return document.querySelector('#board-layout-chessboard > .board') ||
            document.querySelector('wc-chess-board') ||
            document.querySelector('chess-board');
    }

    // Get board orientation (player color)
    function getBoardOrientation() {
        const boardElem = getBoardElem();
        if (!boardElem) return 'w';
        return boardElem.classList.contains('flipped') ? 'b' : 'w';
    }

    // Parse piece coordinates from class (e.g., "square-45" -> [3, 4])
    function getPieceCoords(pieceElem) {
        const match = pieceElem.className.match(/square-(\d)(\d)/);
        if (!match) return null;
        return [parseInt(match[1]) - 1, parseInt(match[2]) - 1];
    }

    // Get piece FEN character from element
    function getPieceFen(pieceElem) {
        const classList = pieceElem.classList;
        for (const cls of classList) {
            if (PIECE_MAP[cls]) {
                return PIECE_MAP[cls];
            }
        }
        return null;
    }

    // Build 8x8 board matrix from DOM
    function getBoardMatrix() {
        const boardElem = getBoardElem();
        if (!boardElem) return null;

        // Initialize 8x8 board with empty squares (1 = empty in FEN notation)
        const board = Array.from({ length: 8 }, () => Array(8).fill(1));

        const pieces = boardElem.querySelectorAll('.piece');
        if (pieces.length === 0) return null;

        pieces.forEach(pieceElem => {
            const pieceFen = getPieceFen(pieceElem);
            const coords = getPieceCoords(pieceElem);

            if (pieceFen && coords) {
                const [file, rank] = coords;
                // Convert to matrix indices (rank 1 = index 7, rank 8 = index 0)
                board[7 - rank][file] = pieceFen;
            }
        });

        return board;
    }

    // Get piece at specific square (e.g., 'e1' -> 'K')
    function getBoardPiece(fenCoord) {
        const file = fenCoord.charCodeAt(0) - 97; // 'a' = 0, 'b' = 1, etc.
        const rank = parseInt(fenCoord[1]) - 1;   // '1' = 0, '8' = 7
        const board = getBoardMatrix();
        if (!board) return null;
        return board[7 - rank]?.[file];
    }

    // Calculate castling rights by checking king and rook positions
    function getCastlingRights() {
        let rights = '';

        // White castling
        const e1 = getBoardPiece('e1');
        const h1 = getBoardPiece('h1');
        const a1 = getBoardPiece('a1');

        if (e1 === 'K' && h1 === 'R') rights += 'K';
        if (e1 === 'K' && a1 === 'R') rights += 'Q';

        // Black castling
        const e8 = getBoardPiece('e8');
        const h8 = getBoardPiece('h8');
        const a8 = getBoardPiece('a8');

        if (e8 === 'k' && h8 === 'r') rights += 'k';
        if (e8 === 'k' && a8 === 'r') rights += 'q';

        return rights || '-';
    }

    // Squeeze empty squares: "1111" -> "4"
    function squeezeEmptySquares(fenStr) {
        return fenStr.replace(/1+/g, match => match.length.toString());
    }

    // Get basic FEN (just the piece positions)
    function getBasicFen() {
        const board = getBoardMatrix();
        if (!board) return null;

        return squeezeEmptySquares(
            board.map(row => row.join('')).join('/')
        );
    }

    // Detect whose turn it is by looking at the last move highlights
    function detectTurn() {
        const boardElem = getBoardElem();
        if (!boardElem) return 'w';

        // Find highlight elements (last move indicators)
        const highlights = boardElem.querySelectorAll('.highlight');

        if (highlights.length >= 2) {
            // Find which piece is on a highlighted square (the piece that just moved)
            for (const h of highlights) {
                const squareClass = Array.from(h.classList).find(c => c.startsWith('square-'));
                if (!squareClass) continue;

                const piece = boardElem.querySelector(`.piece.${squareClass}`);
                if (piece) {
                    const pieceFen = getPieceFen(piece);
                    if (pieceFen) {
                        // If the piece is uppercase (white), white just moved -> black's turn
                        // If lowercase (black), black just moved -> white's turn
                        return pieceFen === pieceFen.toUpperCase() ? 'b' : 'w';
                    }
                }
            }
        }

        // Fallback: Check if starting position (all 32 pieces, white moves first)
        const pieces = boardElem.querySelectorAll('.piece');
        if (pieces.length === 32) {
            return 'w';
        }

        // Can't determine - default to white
        return 'w';
    }

    // Get full FEN string
    function getFen() {
        const basicFen = getBasicFen();
        if (!basicFen) return null;

        const playerColor = getBoardOrientation();
        const turn = detectTurn();
        const castling = getCastlingRights();

        // FEN structure: [position] [turn] [castling] [en passant] [halfmove] [fullmove]
        return `${basicFen} ${turn} ${castling} - 0 1`;
    }

    // Send to server
    async function sendToServer(fen, playerColor, turn) {
        try {
            const response = await fetch(SERVER_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ fen, color: playerColor, turn })
            });

            if (response.ok && !isConnected) {
                isConnected = true;
                console.log('%c[GAMBITO] Connected to bot server!', 'color: #58D68D; font-weight: bold;');
            }
            return true;
        } catch (e) {
            if (isConnected) {
                isConnected = false;
                console.warn('[GAMBITO] Lost connection to bot server');
            }
            return false;
        }
    }

    // Main update function
    function update() {
        const fen = getFen();
        if (!fen) return;

        const playerColor = getBoardOrientation();
        const turn = detectTurn();

        // Only send if FEN changed
        if (fen !== lastFenSent) {
            lastFenSent = fen;

            console.log('%c[GAMBITO] Position update', 'color: #F39C12;');
            console.log('[GAMBITO] FEN:', fen);
            console.log('[GAMBITO] Turn:', turn === 'w' ? 'White' : 'Black');
            console.log('[GAMBITO] Playing as:', playerColor === 'w' ? 'White' : 'Black');

            sendToServer(fen, playerColor === 'w' ? 'white' : 'black', turn);
        }
    }

    // Set up MutationObserver for more responsive updates
    function setupObserver() {
        const boardElem = getBoardElem();
        if (!boardElem) {
            setTimeout(setupObserver, 500);
            return;
        }

        const observer = new MutationObserver(mutations => {
            // Check if this is a significant change (move, not just hover)
            const isSignificant = mutations.length >= 2 ||
                mutations.some(m => m.target.classList?.contains('highlight')) ||
                mutations.some(m => m.type === 'childList');

            if (isSignificant) {
                update();
            }
        });

        observer.observe(boardElem, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class', 'style']
        });

        console.log('%c[GAMBITO] MutationObserver active', 'color: #5DADE2;');
    }

    // Initialize
    function init() {
        setupObserver();

        // Also poll as fallback
        setInterval(update, POLL_INTERVAL);

        // Initial update
        update();

        console.log('%c[GAMBITO] Monitoring Chess.com...', 'color: #5DADE2;');
    }

    // Wait for DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
