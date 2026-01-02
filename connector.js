// ==UserScript==
// @name         Chess Bot Connector V2
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Sends Chess.com game state to local bot server
// @author       You
// @match        https://www.chess.com/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    console.log("Chess Bot Connector V2 Started");

    const SERVER_URL = "http://127.0.0.1:5000/update_fen";
    let lastFen = "";

    function getBoard() {
        // Strategy 1: Standard <chess-board> element
        const board1 = document.querySelector('chess-board');
        if (board1 && board1.game) return board1.game;

        // Strategy 2: <wc-chess-board> (older/alternative)
        const board2 = document.querySelector('wc-chess-board');
        if (board2 && board2.game) return board2.game;

        // Strategy 3: Look for the game object in the global scope (sometimes exposed)
        if (window.game) return window.game;

        // Strategy 4: Search specifically for the chessboard controller in the DOM
        // This is a bit hacky but often works if the web component is wrapped
        const boards = document.querySelectorAll('*');
        for (let el of boards) {
            if (el.game && typeof el.game.getFEN === 'function') {
                return el.game;
            }
        }

        return null;
    }

    function update() {
        const game = getBoard();
        if (!game) {
            // console.log("Board not found yet...");
            return;
        }

        const fen = game.getFEN();
        // Orientation might be a property or method depending on version
        let orientation = 'white';
        if (typeof game.getOrientation === 'function') {
            orientation = game.getOrientation();
        } else if (game.getPlayingAs) {
            orientation = game.getPlayingAs(); // Sometimes returns 1 (white) or 2 (black)
            if (orientation === 2) orientation = 'black';
            else orientation = 'white';
        }

        if (fen !== lastFen) {
            lastFen = fen;
            console.log("New FEN:", fen);
            console.log("Orientation:", orientation);

            fetch(SERVER_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    fen: fen,
                    color: orientation
                })
            }).catch(err => console.error("Error sending to bot:", err));
        }
    }

    // Check every 100ms
    setInterval(update, 100);

})();
