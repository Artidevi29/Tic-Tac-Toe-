import streamlit as st
import json
import os
from datetime import datetime

# ------------------ Unbeatable AI: Minimax ------------------
def minimax(board, depth, is_maximizing, bot_symbol, player_symbol):
    winner = check_winner(board)
    if winner == bot_symbol:
        return 10 - depth
    elif winner == player_symbol:
        return depth - 10
    elif is_full(board):
        return 0

    if is_maximizing:
        best = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = bot_symbol
                    score = minimax(board, depth + 1, False, bot_symbol, player_symbol)
                    board[i][j] = " "
                    best = max(best, score)
        return best
    else:
        best = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = player_symbol
                    score = minimax(board, depth + 1, True, bot_symbol, player_symbol)
                    board[i][j] = " "
                    best = min(best, score)
        return best

def bot_best_move(board, bot_symbol, player_symbol):
    best_score = -float('inf')
    best_move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == " ":
                board[i][j] = bot_symbol
                score = minimax(board, 0, False, bot_symbol, player_symbol)
                board[i][j] = " "
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    if best_move:
        board[best_move[0]][best_move[1]] = bot_symbol
        return True
    return False

# ------------------ Game Logic ------------------
def init_board():
    return [[" " for _ in range(3)] for _ in range(3)]

def check_winner(board):
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != " ":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != " ":
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]
    return None

def is_full(board):
    return all(cell != " " for row in board for cell in row)

# ------------------ Match & History ------------------
def save_history(record):
    history_file = "match_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = []
    history.append(record)
    history = history[-50:]
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

def load_history():
    history_file = "match_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            return json.load(f)
    return []

# ------------------ Session State Init ------------------
def init_match():
    if st.session_state.mode == "Two Player":
        st.session_state.scores = {
            st.session_state.p1_name: 0,
            st.session_state.p2_name: 0,
            "Ties": 0
        }
    else:
        st.session_state.scores = {
            st.session_state.p1_name: 0,
            "Bot": 0,
            "Ties": 0
        }
    st.session_state.match_active = True
    st.session_state.round_over = False
    st.session_state.starting_player = "X"
    start_new_round()

def start_new_round():
    st.session_state.board = init_board()
    st.session_state.current_player = st.session_state.starting_player
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.tie = False
    st.session_state.round_over = False
    st.session_state.winner_of_round = None
    st.session_state.tie_round = False

def end_round(winner_symbol=None, tie=False):
    st.session_state.round_over = True
    if tie:
        st.session_state.tie_round = True
        st.session_state.scores["Ties"] += 1
        st.session_state.starting_player = "O" if st.session_state.starting_player == "X" else "X"
    else:
        st.session_state.winner_of_round = winner_symbol
        if st.session_state.mode == "Two Player":
            winner_name = st.session_state.p1_name if winner_symbol == "X" else st.session_state.p2_name
            st.session_state.scores[winner_name] += 1
        else:
            if winner_symbol == "X":
                st.session_state.scores[st.session_state.p1_name] += 1
            else:
                st.session_state.scores["Bot"] += 1
        st.session_state.starting_player = winner_symbol
    st.session_state.game_over = True

def finish_match():
    st.session_state.match_active = False
    if st.session_state.mode == "Two Player":
        p1_wins = st.session_state.scores.get(st.session_state.p1_name, 0)
        p2_wins = st.session_state.scores.get(st.session_state.p2_name, 0)
        if p1_wins > p2_wins:
            winner = st.session_state.p1_name
        elif p2_wins > p1_wins:
            winner = st.session_state.p2_name
        else:
            winner = "Tie"
        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "Two Player",
            "p1": st.session_state.p1_name,
            "p2": st.session_state.p2_name,
            "score1": p1_wins,
            "score2": p2_wins,
            "ties": st.session_state.scores["Ties"],
            "match_winner": winner
        }
    else:
        p_wins = st.session_state.scores.get(st.session_state.p1_name, 0)
        bot_wins = st.session_state.scores.get("Bot", 0)
        if p_wins > bot_wins:
            winner = st.session_state.p1_name
        elif bot_wins > p_wins:
            winner = "Bot"
        else:
            winner = "Tie"
        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "vs Bot",
            "player": st.session_state.p1_name,
            "player_wins": p_wins,
            "bot_wins": bot_wins,
            "ties": st.session_state.scores["Ties"],
            "match_winner": winner
        }
    save_history(record)
    st.rerun()

# ------------------ UI Styling ------------------
st.set_page_config(page_title="Ultimate Tic Tac Toe", page_icon="🏆")
st.markdown("""
<style>
    .stButton button {
        font-size: 36px !important;
        height: 80px !important;
        width: 80px !important;
        border-radius: 15px !important;
        background-color: #1e1e2f !important;
        color: white !important;
        transition: 0.2s;
    }
    .stButton button:hover {
        background-color: #4a4a6a !important;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Ultimate Tic‑Tac‑Toe")
st.caption("Unbeatable Bot • Match History • Animations")

# ------------------ Sidebar Settings ------------------
st.sidebar.header("⚙️ Game Settings")
mode = st.sidebar.radio("Mode", ["Two Player", "vs Bot"])

if mode == "Two Player":
    p1_name = st.sidebar.text_input("Player X Name", "Player 1")
    p2_name = st.sidebar.text_input("Player O Name", "Player 2")
else:
    p1_name = st.sidebar.text_input("Your Name (X)", "You")

needs_reset = False
if "mode" not in st.session_state:
    st.session_state.mode = mode
    needs_reset = True
elif st.session_state.mode != mode:
    st.session_state.mode = mode
    needs_reset = True
if mode == "Two Player":
    if st.session_state.get("p1_name") != p1_name or st.session_state.get("p2_name") != p2_name:
        st.session_state.p1_name = p1_name
        st.session_state.p2_name = p2_name
        needs_reset = True
else:
    if st.session_state.get("p1_name") != p1_name:
        st.session_state.p1_name = p1_name
        needs_reset = True

if needs_reset:
    init_match()
    st.rerun()

# ------------------ Match History Sidebar ------------------
st.sidebar.subheader("📜 Match History")
history = load_history()
if history:
    latest = history[-1]
    st.sidebar.write(f"**Last match:** {latest['date'][:10]}")
    st.sidebar.write(f"Winner: {latest['match_winner']}")
    if st.sidebar.button("📋 View Full History"):
        st.sidebar.write("---")
        for h in reversed(history[-5:]):
            st.sidebar.write(f"{h['date'][:16]} → {h['match_winner']}")
else:
    st.sidebar.write("No history yet.")
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear History"):
    if os.path.exists("match_history.json"):
        os.remove("match_history.json")
    st.rerun()

# ------------------ Scoreboard ------------------
if st.session_state.match_active:
    st.sidebar.subheader("🏅 Current Match Scores")
    if mode == "Two Player":
        col1, col2, col3 = st.sidebar.columns(3)
        col1.metric(st.session_state.p1_name, st.session_state.scores.get(st.session_state.p1_name, 0))
        col2.metric(st.session_state.p2_name, st.session_state.scores.get(st.session_state.p2_name, 0))
        col3.metric("🤝 Ties", st.session_state.scores.get("Ties", 0))
    else:
        col1, col2, col3 = st.sidebar.columns(3)
        col1.metric(st.session_state.p1_name, st.session_state.scores.get(st.session_state.p1_name, 0))
        col2.metric("🤖 Bot", st.session_state.scores.get("Bot", 0))
        col3.metric("🤝 Ties", st.session_state.scores.get("Ties", 0))

    if st.sidebar.button("❌ Quit Match"):
        finish_match()
        st.rerun()
    if st.sidebar.button("🔄 Reset Match Scores"):
        init_match()
        st.rerun()
else:
    st.header("🏆 Match Finished 🏆")
    if mode == "Two Player":
        p1_wins = st.session_state.scores.get(st.session_state.p1_name, 0)
        p2_wins = st.session_state.scores.get(st.session_state.p2_name, 0)
        if p1_wins > p2_wins:
            st.success(f"🎉 {st.session_state.p1_name} wins the match {p1_wins} - {p2_wins}!")
        elif p2_wins > p1_wins:
            st.success(f"🎉 {st.session_state.p2_name} wins the match {p2_wins} - {p1_wins}!")
        else:
            st.info(f"Match tied {p1_wins} - {p2_wins}")
    else:
        p_wins = st.session_state.scores.get(st.session_state.p1_name, 0)
        bot_wins = st.session_state.scores.get("Bot", 0)
        if p_wins > bot_wins:
            st.success(f"🎉 {st.session_state.p1_name} wins the match {p_wins} - {bot_wins}!")
        elif bot_wins > p_wins:
            st.success(f"🎉 Bot wins the match {bot_wins} - {p_wins}!")
        else:
            st.info(f"Match tied {p_wins} - {bot_wins}")
    if st.button("🆕 Start New Match"):
        init_match()
        st.rerun()
    st.stop()

# ------------------ Main Game Area (Fixed Bot) ------------------
board = st.session_state.board
round_over = st.session_state.get("round_over", False)

if round_over:
    st.info("🏁 Round finished!")
    if st.session_state.tie_round:
        st.write("🤝 It's a tie! Next round starting player switches.")
    else:
        if mode == "Two Player":
            winner_name = st.session_state.p1_name if st.session_state.winner_of_round == "X" else st.session_state.p2_name
            st.success(f"🥇 {winner_name} won this round!")
            st.balloons()
        else:
            if st.session_state.winner_of_round == "X":
                st.success(f"🥇 {st.session_state.p1_name} won this round!")
                st.balloons()
            else:
                st.success("🤖 Bot won this round!")
                st.snow()
    col1, col2 = st.columns(2)
    if col1.button("▶️ Continue to next round"):
        start_new_round()
        st.rerun()
    if col2.button("🏁 Quit Match"):
        finish_match()
        st.rerun()
    st.stop()

# Show turn info
if not round_over:
    if mode == "Two Player":
        player_turn = st.session_state.p1_name if st.session_state.current_player == "X" else st.session_state.p2_name
        st.write(f"### 🎯 {player_turn}'s turn ({st.session_state.current_player})")
    else:
        if st.session_state.current_player == "X":
            st.write(f"### 🎯 {st.session_state.p1_name}'s turn (X)")
        else:
            st.write("### 🤖 Bot is thinking...")

# Draw board
cols = st.columns(3)
for i in range(3):
    for j in range(3):
        cell = board[i][j]
        label = cell if cell != " " else "⬜"
        if cell == "X":
            label = "❌"
        elif cell == "O":
            label = "⭕"
        disabled = (cell != " ") or round_over
        if mode == "vs Bot" and not round_over and st.session_state.current_player == "O":
            disabled = True
        if cols[j].button(label, key=f"{i}{j}_{st.session_state.current_player}", use_container_width=True, disabled=disabled):
            if not round_over and board[i][j] == " " and (mode == "Two Player" or (mode == "vs Bot" and st.session_state.current_player == "X")):
                board[i][j] = "X" if st.session_state.current_player == "X" else "O"
                winner_sym = check_winner(board)
                if winner_sym:
                    end_round(winner_symbol=winner_sym, tie=False)
                elif is_full(board):
                    end_round(tie=True)
                else:
                    if mode == "Two Player":
                        st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"
                    else:
                        st.session_state.current_player = "O"
                st.rerun()

# Bot move (triggered automatically after rerun)
if mode == "vs Bot" and not round_over and st.session_state.current_player == "O":
    bot_best_move(board, "O", "X")
    winner_sym = check_winner(board)
    if winner_sym:
        end_round(winner_symbol="O", tie=False)
    elif is_full(board):
        end_round(tie=True)
    else:
        st.session_state.current_player = "X"
    st.rerun()