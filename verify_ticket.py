import streamlit as st
from blockchain import Blockchain
from events_data import events
from datetime import datetime

# --- Initialize blockchain ---
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
blockchain = st.session_state.blockchain

st.set_page_config(page_title="Verify Ticket", layout="centered", page_icon="✅")

st.markdown("<h1 style='text-align:center;color:#004AAD;'>🎫 Ticket Verification</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

event_name = st.text_input("Enter Event Name")
ticket_id = st.text_input("Enter Your Ticket ID")

if st.button("Verify Ticket"):
    tx = blockchain.find_ticket(ticket_id)
    if not tx:
        st.error("❌ Ticket ID not found")
    elif tx["scanned"]:
        st.warning("⚠️ Ticket already scanned!")
    elif tx["event_name"] != event_name:
        st.error("Event name does not match ticket")
    else:
        # Flip scanned to True
        tx["scanned"] = True
        events[event_name]["tickets_scanned"] += 1
        st.success(f"✅ Welcome to {event_name}, {tx['customer_name']}!")
        st.info(f"Tickets Scanned: {events[event_name]['tickets_scanned']} | Remaining Capacity: {events[event_name]['capacity']}")
