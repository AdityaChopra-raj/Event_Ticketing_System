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
    """Simple blockchain to store ticket transactions."""
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

    def new_ticket(self, buyer: str, event: str) -> str:
        ticket_id = hashlib.sha256(
            f"{buyer}{event}{time.time()}".encode()
        ).hexdigest()[:10]
        ticket = {"buyer": buyer, "event": event, "ticket_id": ticket_id}
        self.pending_tickets.append(ticket)
        return ticket_id

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        block_copy = block.copy()
        block_copy.pop("hash", None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            if curr["previous_hash"] != prev["hash"]:
                return False
            if curr["hash"] != self.hash(curr):
                return False
        return True

    def verify_ticket(self, ticket_id: str) -> bool:
        for block in self.chain:
            for t in block["tickets"]:
                if t["ticket_id"] == ticket_id:
                    return True
        return False

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="🎟️ Blockchain Event Ticketing", layout="wide")

# Initialize blockchain
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
bc: Blockchain = st.session_state.blockchain

st.title("🎟️ Blockchain-based Event Ticketing System")
st.markdown("Secure, verifiable event tickets powered by blockchain.")

# Metrics
col1, col2 = st.columns(2)
col1.metric("Chain Length", len(bc.chain))
col2.metric("Is Chain Valid?", "✅ Yes" if bc.is_chain_valid() else "❌ No")

# Tabs for navigation
tabs = st.tabs(["➕ Purchase Ticket", "🔍 Verify Ticket", "📜 Blockchain Explorer"])

# --- Purchase Ticket ---
with tabs[0]:
    st.subheader("Buy a Ticket")
    with st.form("purchase_form", clear_on_submit=True):
        buyer = st.text_input("Buyer Name")
        event = st.text_input("Event Name")
        submitted = st.form_submit_button("Buy Ticket")
        if submitted:
            if not buyer or not event:
                st.error("Please fill out all fields.")
            else:
                ticket_id = bc.new_ticket(buyer, event)
                block = bc.new_block(proof=123)
                st.success(f"✅ Ticket purchased for {event}! Ticket ID: {ticket_id}")
                st.info(f"Recorded in Block {block['index']}.")

                # Generate QR code for ticket
                img = qrcode.make(ticket_id)
                buf = BytesIO()
                img.save(buf)
                st.image(buf.getvalue(), caption="Scan this QR code for Ticket ID")

# --- Verify Ticket ---
with tabs[1]:
    st.subheader("Verify a Ticket")
    ticket_input = st.text_input("Enter Ticket ID to Verify")
    if ticket_input:
        if bc.verify_ticket(ticket_input):
            st.success("✅ Valid ticket! This ticket exists on the blockchain.")
        else:
            st.error("❌ Invalid ticket! No such ticket recorded.")

# --- Blockchain Explorer ---
with tabs[2]:
    st.subheader("Blockchain Explorer")
    for block in reversed(bc.chain):
        num_tickets = len(block.get("tickets", []))
        with st.expander(f"Block {block['index']} — {num_tickets} Tickets"):
            st.write("Previous Hash:", block.get("previous_hash", "N/A"))
            st.write("Hash:", block.get("hash", "N/A"))
            st.json(block.get("tickets", []))
