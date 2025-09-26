import streamlit as st
from datetime import datetime
from blockchain import Blockchain
from events_data import events
from PIL import Image

# --- Streamlit setup ---
st.set_page_config(page_title="Event Ticket Scanner", layout="wide", page_icon="🎫")

# Initialize blockchain
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
blockchain = st.session_state.blockchain

# --- Header ---
st.markdown("<h1 style='text-align:center;color:#004AAD;'>🎫 Event Ticket Scanner</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Sidebar scanning ---
st.sidebar.header("Scan Ticket")
event_name = st.sidebar.selectbox("Select Event", list(events.keys()))
ticket_id = st.sidebar.text_input("Scan QR / Enter Ticket ID")

if st.sidebar.button("Scan Ticket") and ticket_id:

    already_scanned = any(
        tx["ticket_id"] == ticket_id and tx["scanned"]
        for block in blockchain.chain
        for tx in block["transactions"]
    )

    if already_scanned:
        st.sidebar.warning(f"Ticket {ticket_id} already scanned for {event_name}!")
    elif events[event_name]["tickets_scanned"] >= 150:
        st.sidebar.error(f"Event {event_name} is full!")
    else:
        blockchain.add_transaction(
            sender="scanner_1", receiver="event_system",
            ticket_id=ticket_id, event_name=event_name, scanned=True
        )
        blockchain.mine_block()
        events[event_name]["tickets_scanned"] += 1
        events[event_name]["capacity"] = 150 - events[event_name]["tickets_scanned"]
        st.sidebar.success(f"Ticket {ticket_id} scanned successfully!")

# --- Event Dashboard ---
st.markdown("<h2 style='color:#004AAD;'>Event Dashboard</h2>", unsafe_allow_html=True)
cols = st.columns(2)  # 2 cards per row

for i, (ename, data) in enumerate(events.items()):
    color = "#28a745"
    ratio = data["tickets_scanned"] / 150
    if ratio >= 0.9: color = "#dc3545"
    elif ratio >= 0.5: color = "#fd7e14"

    with cols[i % 2]:
        img = Image.open(data["image"])
        st.image(img, use_column_width=True)
        st.markdown(f"""
        <div style='background-color:#F5F5F5;padding:15px;border-radius:15px;text-align:center;box-shadow: 2px 2px 5px #ccc;'>
            <h3 style='color:#004AAD;'>{ename}</h3>
            <p>Tickets Scanned: <b>{data['tickets_scanned']}</b></p>
            <p>Remaining Capacity: <b>{data['capacity']}</b></p>
            <div style='width:100%;background:#ddd;border-radius:10px;'>
                <div style='width:{ratio*100}%;background:{color};height:15px;border-radius:10px;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Blockchain audit ---
st.markdown("<h2 style='color:#004AAD;'>Recent Scanned Tickets (Blockchain)</h2>", unsafe_allow_html=True)
recent_txs = []
for block in blockchain.chain[-10:]:
    recent_txs.extend(block["transactions"])

for tx in recent_txs[::-1]:
    st.markdown(f"**Event:** {tx['event_name']} | **Ticket ID:** {tx['ticket_id']} | **Scanned At:** {datetime.fromtimestamp(tx['timestamp'])}")
