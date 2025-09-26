import streamlit as st
from blockchain import Blockchain
from events_data import events

# --- Initialize blockchain ---
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
blockchain = st.session_state.blockchain

# --- Page Config ---
st.set_page_config(page_title="Ticket Verification", layout="centered", page_icon="✅")

# --- Header ---
st.markdown("<h1 style='text-align:center;color:#004AAD;'>✅ Ticket Verification Portal</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- CSS for Netflix-style input/button ---
st.markdown("""
<style>
input, div.stButton > button {
    border-radius:5px;
    padding:8px 12px;
    font-family: Arial, sans-serif;
    font-size:16px;
}
div.stButton > button {
    background-color: #E50914;
    color:white;
    font-weight:bold;
    cursor:pointer;
    box-shadow:2px 2px 6px #aaa;
    transition: transform 0.2s;
    width:200px;
    display:block;
    margin:10px auto;
}
div.stButton > button:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# --- Get Event from query params ---
query_params = st.experimental_get_query_params()
event_name = query_params.get("event", [""])[0]

if not event_name or event_name not in events:
    st.error("Invalid event or missing event parameter in URL")
else:
    st.markdown(f"<h2 style='text-align:center;color:#004AAD;'>{event_name} - Ticket Verification</h2>", unsafe_allow_html=True)

    # --- Ticket ID input ---
    ticket_id_input = st.text_input("Enter Your Ticket ID", key="ticket_id_input")

    if st.button("Verify Ticket", key="verify_ticket_btn"):
        if not ticket_id_input:
            st.warning("Please enter a Ticket ID")
        else:
            # Search blockchain for this ticket
            found = False
            for block in blockchain.chain:
                for txn in block["transactions"]:
                    if txn["ticket_id"] == ticket_id_input and txn["event_name"] == event_name:
                        found = True
                        if txn["scanned"]:
                            st.error("❌ Ticket has already been scanned")
                        else:
                            txn["scanned"] = True
                            events[event_name]["tickets_scanned"] += 1
                            events[event_name]["capacity"] -= 1
                            st.success(f"✅ Ticket Verified! Welcome to {event_name}")
                        break
                if found:
                    break
            if not found:
                st.error("❌ Ticket ID not found for this event")
