// ==UserScript==
// @name         Chess Bot Connector V2
// @namespace    http://tampermonkey.net/
// @version      2.1
// @description  Sends Chess.com game state to local bot server
// @author       You
// @match        https://www.chess.com/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// ==/UserScript==

(function () {
    'use strict';

    console.log("%c[BOT] Chess Bot Connector V2.1 Started", "color: lime; font-weight: bold;");

    const SERVER_URL = "http://127.0.0.1:5000/update_fen";
    let lastFen = "";
    let boardFound = false;

    function getBoard() {
        // Strategy 1: wc-chess-board (current Chess.com)
        const wcBoard = document.querySelector('wc-chess-board');
        if (wcBoard) {
            if (wcBoard.game) return { board: wcBoard, game: wcBoard.game };
            if (wcBoard._game) return { board: wcBoard, game: wcBoard._game };
        }

        // Strategy 2: chess-board element
        const chessBoard = document.querySelector('chess-board');
        if (chessBoard && chessBoard.game) {
            return { board: chessBoard, game: chessBoard.game };
        }

        return null;
    }

    function getFEN(game) {
        // Try multiple methods to get FEN
        if (typeof game.getFEN === 'function') {
            return game.getFEN();
        }
        if (typeof game.fen === 'function') {
            return game.fen();
        }
        if (game.fen && typeof game.fen === 'string') {
            return game.fen;
        }
        if (game._fen) {
            return game._fen;
        }
        // Try to get from position
        if (game.getPosition && typeof game.getPosition === 'function') {
            const pos = game.getPosition();
            if (pos && pos.fen) return pos.fen;
        }
        return null;
    }

    function getPlayerColor(boardElement, game) {
        // Method 1: Check board orientation via flipped class
        if (boardElement.classList.contains('flipped')) {
            return 'black';
        }

        // Method 2: Check game methods
        if (typeof game.getPlayingAs === 'function') {
            const side = game.getPlayingAs();
            if (side === 2 || side === 'black') return 'black';
            return 'white';
        }

        if (typeof game.getOrientation === 'function') {
            const orient = game.getOrientation();
            if (orient === 2 || orient === 'black') return 'black';
            return 'white';
        }

        // Method 3: Check board element attributes
        const isFlipped = boardElement.getAttribute('flipped') === 'true' ||
            boardElement.hasAttribute('flipped');
        if (isFlipped) return 'black';

        // Default
        return 'white';
    }

    function sendToServer(fen, color) {
        // Use GM_xmlhttpRequest if available (bypasses CORS)
        if (typeof GM_xmlhttpRequest !== 'undefined') {
            GM_xmlhttpRequest({
                method: "POST",
                url: SERVER_URL,
                headers: { "Content-Type": "application/json" },
                data: JSON.stringify({ fen: fen, color: color }),
                onload: function (response) {
                    console.log("%c[BOT] Sent FEN successfully", "color: lime;");
                },
                onerror: function (err) {
                    console.error("[BOT] GM_xmlhttpRequest error:", err);
                }
            });
        } else {
            // Fallback to fetch
            fetch(SERVER_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ fen: fen, color: color })
            })
                .then(() => console.log("%c[BOT] Sent FEN successfully", "color: lime;"))
                .catch(err => console.error("[BOT] Fetch error:", err));
        }
    }

    function update() {
        const result = getBoard();

        if (!result) {
            if (boardFound) {
                console.log("%c[BOT] Board lost", "color: orange;");
                boardFound = false;
            }
            return;
        }

        if (!boardFound) {
            console.log("%c[BOT] Board found!", "color: lime; font-weight: bold;");
            console.log("[BOT] Board element:", result.board);
            console.log("[BOT] Game object:", result.game);
            boardFound = true;
        }

        const fen = getFEN(result.game);

        if (!fen) {
            console.warn("[BOT] Could not get FEN from game object");
            return;
        }

        if (fen !== lastFen) {
            lastFen = fen;
            const color = getPlayerColor(result.board, result.game);

            console.log("%c[BOT] New position detected", "color: cyan;");
            console.log("[BOT] FEN:", fen);
            console.log("[BOT] Playing as:", color);

            sendToServer(fen, color);
        }
    }

    // Check every 100ms
    setInterval(update, 100);

    // Also try to connect immediately
    console.log("[BOT] Waiting for board...");

})();
