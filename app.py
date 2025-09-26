
import streamlit as st
import hashlib
import json
import time
from typing import List, Dict, Any
import qrcode
from io import BytesIO

# -----------------------
# Blockchain Class
# -----------------------
class Blockchain:
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.pending_tickets: List[Dict[str, Any]] = []
        # Genesis block
        self.new_block(proof=100, previous_hash="1")

    def new_block(self, proof: int, previous_hash: str = None) -> Dict[str, Any]:
        block_tickets = [tx.copy() for tx in self.pending_tickets]
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "tickets": block_tickets,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }
        self.pending_tickets = []
        block["hash"] = self.hash(block)
        self.chain.append(block)
        return block

    def new_ticket(self, buyer: str, event: str):
        ticket_id = hashlib.sha256(f"{buyer}{event}{time.time()}".encode()).hexdigest()[:10]
        tx = {"buyer": buyer, "event": event, "ticket_id": ticket_id, "scanned": False}
        self.pending_tickets.append(tx)
        return ticket_id, self.last_block["index"] + 1

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        block_copy = block.copy()
        block_copy.pop("hash", None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    def verify_ticket(self, ticket_id: str) -> bool:
        for block in self.chain:
            for tx in block['tickets']:
                if tx['ticket_id'] == ticket_id:
                    return True
        return False

    def scan_ticket(self, ticket_id: str) -> bool:
        for block in self.chain:
            for tx in block['tickets']:
                if tx['ticket_id'] == ticket_id:
                    tx['scanned'] = True
                    return True
        return False

    def scanned_count(self, event: str) -> int:
        count = 0
        for block in self.chain:
            for tx in block['tickets']:
                if tx['event'] == event and tx.get('scanned'):
                    count += 1
        return count

# -----------------------
# Streamlit App
# -----------------------
st.set_page_config(page_title="Blockchain Event Ticketing", layout="wide")

# Predefined events and capacities
EVENTS = {
    "Navratri Pooja": 100,
    "Diwali Dance": 150,
    "Freshers": 200,
    "Ravan Dehan": 120
}

# Initialize blockchain
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

bc: Blockchain = st.session_state.blockchain

# Event selection dropdown on top
selected_event = st.selectbox("🎉 Select Event", list(EVENTS.keys()))

st.title("🎟️ Blockchain-based Event Ticketing System")

# --- Tabs ---
tabs = st.tabs(["Buy Ticket", "Verify Ticket", "Blockchain Explorer"])

with tabs[0]:
    st.header("➕ Buy Ticket")
    with st.form("buy_form", clear_on_submit=True):
        buyer = st.text_input("Your Name")
        submitted = st.form_submit_button("Buy Ticket")
        if submitted and buyer:
            ticket_id, block_index = bc.new_ticket(buyer, selected_event)
            block = bc.new_block(proof=123)
            st.success(f"✅ Ticket purchased for {selected_event}! Ticket ID: {ticket_id}")
            # Generate QR code
            img = qrcode.make(ticket_id)
            buf = BytesIO()
            img.save(buf)
            st.image(buf.getvalue(), caption="Your Ticket QR Code")

with tabs[1]:
    st.header("🔍 Verify / Scan Ticket")
    verify_id = st.text_input("Enter Ticket ID to Verify")
    if st.button("Check Ticket"):
        if bc.verify_ticket(verify_id):
            st.success("✅ Ticket is valid!")
            if st.button("Mark as Scanned"):
                if bc.scan_ticket(verify_id):
                    st.info("🎫 Ticket marked as scanned.")
        else:
            st.error("❌ Ticket not found!")

with tabs[2]:
    st.header("🔎 Blockchain Explorer")
    for block in reversed(bc.chain):
        index = block.get("index", "N/A")
        with st.expander(f"Block {index}"):
            st.write("Previous Hash:", block.get("previous_hash", "N/A"))
            st.write("Hash:", block.get("hash", "N/A"))
            st.json(block.get("tickets", []))

# Sidebar Stats
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Event Stats")
    capacity = EVENTS[selected_event]
    scanned = bc.scanned_count(selected_event)
    st.markdown(f"**Event:** {selected_event}")
    st.markdown(f"**Capacity:** {capacity}")
    st.markdown(f"**Tickets Scanned:** {scanned}")
    st.caption("Tickets are recorded on a tamper-proof blockchain ledger.")
