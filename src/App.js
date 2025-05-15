import React, { useState } from "react";
import "./App.css";

function App() {
    const [balance, setBalance] = useState(100);
    const [playerHand, setPlayerHand] = useState([]);
    const [dealerHand, setDealerHand] = useState([]);
    const [communityCards, setCommunityCards] = useState([]);
    const [pot, setPot] = useState(0);
    const [message, setMessage] = useState("");
    const [stage, setStage] = useState("pre-start");
    const [gameActive, setGameActive] = useState(false);

    const fetchJSON = async (url, method = "GET", body = null) => {
        const res = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: body ? JSON.stringify(body) : null,
        });
        return await res.json();
    };

    const startGame = async () => {
        const response = await fetchJSON("http://127.0.0.1:5000/start", "POST", { buy_in: balance });
        if (response.error) {
            setMessage(response.error);
            return;
        }
        setPlayerHand(response.player_hand || []);
        setDealerHand([]);
        setCommunityCards([]);
        setPot(response.pot);
        setStage(response.stage);
        setMessage("New hand started. Place your pre-flop bet.");
        setGameActive(true);
    };

    const placeBet = async (multiplier) => {
        const res = await fetchJSON("http://127.0.0.1:5000/bet", "POST", { multiplier });
        if (res.error) {
            setMessage(res.error);
            return;
        }
        setPot(res.pot);
        setBalance(res.balance);
        setPlayerHand(res.player_hand);
        setDealerHand(res.dealer_hand);
        setCommunityCards(res.community_cards);
        setStage("complete");
        setMessage(`Winner: ${res.winner}. Balance: $${res.balance}`);
    };

    const check = async () => {
        const res = await fetchJSON("http://127.0.0.1:5000/check", "POST");
        if (res.error) {
            setMessage(res.error);
            return;
        }

        if (res.cards) {
            setCommunityCards(res.cards);
        } else if (res.card) {
            setCommunityCards(prev => [...prev, res.card]);
        }

        if (res.stage === "complete") {
            setDealerHand(res.dealer_hand);
            setPlayerHand(res.player_hand);
            setStage("complete");
            setBalance(res.balance);
            setMessage(`Winner: ${res.winner}. Balance: $${res.balance}`);
        } else {
            setStage(res.stage);
            setMessage("Next community card dealt.");
        }
    };

    const fold = async () => {
        await fetchJSON("http://127.0.0.1:5000/fold", "POST");
        setMessage("You folded. Dealer wins.");
        setStage("complete");
    };

    const renderCard = (card) => {
        const suitSymbols = {
            Hearts: "♥",
            Diamonds: "♦",
            Clubs: "♣",
            Spades: "♠"
        };
        const isRed = card[1] === "Hearts" || card[1] === "Diamonds";

        return (
            <div className={`card ${isRed ? "red" : ""}`} key={card[0] + card[1]}>
                <div className="corner top">{card[0]}<br />{suitSymbols[card[1]]}</div>
                <div className="suit">{suitSymbols[card[1]]}</div>
                <div className="corner bottom">{card[0]}<br />{suitSymbols[card[1]]}</div>
            </div>
        );
    };

    return (
        <div className="app">
            <div className="dealer">
                <h2>Dealer Hand</h2>
                <div className="card-group">
                    {stage === "complete" ? dealerHand.map(renderCard) : <div className="hidden-text">Hidden</div>}
                </div>
            </div>

            <div className="center">
                <h2>Community Cards</h2>
                <div className="card-group">
                    {communityCards.length > 0 ? communityCards.map(renderCard) : <div className="hidden-text">None</div>}
                </div>
                <div className="stats">
                    <span>Balance: ${balance}</span>
                    <span>Pot: ${pot}</span>
                </div>
                <div className="message">{message}</div>
            </div>

            <div className="bottom">
                <div className="player">
                    <h2>Player Hand</h2>
                    <div className="card-group">{playerHand.map(renderCard)}</div>
                </div>

                <div className="controls">
                    <button onClick={() => placeBet(4)} disabled={stage !== "pre-flop"}>Bet 4x</button>
                    <button onClick={() => placeBet(2)} disabled={stage !== "flop"}>Bet 2x</button>
                    <button onClick={() => placeBet(1)} disabled={stage !== "turn"}>Bet 1x</button>
                    <button onClick={check} disabled={stage === "complete" || stage === "river"}>Check</button>
                    <button onClick={fold} disabled={stage === "complete"}>Fold</button>
                </div>

                {stage === "complete" && gameActive && (
                    <div className="after-hand">
                        {balance >= 5 ? (
                            <button onClick={startGame}>Play Next Hand</button>
                        ) : (
                            <p className="out-of-money">You're out of money.</p>
                        )}
                        <button onClick={() => {
                            setGameActive(false);
                            setStage("pre-start");
                            setMessage("You left the table.");
                        }}>Leave Table</button>
                    </div>
                )}

                {!gameActive && stage === "pre-start" && (
                    <div className="start-area">
                        <button onClick={startGame}>Start Game</button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
