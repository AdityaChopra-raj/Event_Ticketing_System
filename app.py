import streamlit as st
import hashlib
import json
import time
from typing import List, Dict, Any

# -----------------------
# Blockchain Class
# -----------------------
class Blockchain:
    """
    Simple blockchain to store ticket transactions.
    Each block contains a list of ticket purchases.
    """
    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self.pending_tickets: List[Dict[str, Any]] = []
        # Create the genesis block
        self.new_block(proof=100, previous_hash="1")

    def new_block(self, proof: int, previous_hash: str = None) -> Dict[str, Any]:
        """
        Add a new block to the chain with all pending tickets.
        """
        block_tickets = [tx.copy() for tx in self.pending_tickets]  # avoid mutation
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "tickets": block_tickets,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }
        self.pending_tickets = []  # reset pending list
        block["hash"] = self.hash(block)  # store hash inside block
        self.chain.append(block)
        return block

    def new_ticket(self, buyer: str, event: str) -> str:
        """
        Record a new ticket purchase.
        Generates a unique ticket_id.
        """
        ticket_id = hashlib.sha256(
            f"{buyer}{event}{time.time()}".encode()
        ).hexdigest()[:10]  # short unique ID
        ticket = {"buyer": buyer, "event": event, "ticket_id": ticket_id}
        self.pending_tickets.append(ticket)
        return ticket_id

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """
        Create SHA-256 hash of a block, excluding its own hash.
        """
        block_copy = block.copy()
        block_copy.pop("hash", None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> Dict[str, Any]:
        return self.chain[-1]

    def is_chain_valid(self) -> bool:
        """
        Check blockchain integrity.
        """
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            if curr["previous_hash"] != prev["hash"]:
                return False
            if curr["hash"] != self.hash(curr):
                return False
        return True

    def verify_ticket(self, ticket_id: str) -> bool:
        """
        Check if a ticket ID exists in the blockchain.
        """
        for block in self.chain:
            for t in block["tickets"]:
                if t["ticket_id"] == ticket_id:
                    return True
        return False


# -----------------------
# Streamlit App
# -----------------------
st.set_page_config(page_title="🎟️ Blockchain Event Ticketing", layout="wide")

# Initialize blockchain in session
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

bc: Blockchain = st.session_state.blockchain

st.title("🎟️ Blockchain-based Event Ticketing System")

# Display chain info
col1, col2 = st.columns(2)
col1.metric("Chain Length", len(bc.chain))
col2.metric("Is Chain Valid?", "✅ Yes" if bc.is_chain_valid() else "❌ No")

# --- Purchase Ticket ---
st.header("➕ Purchase Ticket")
with st.form("purchase_form", clear_on_submit=True):
    buyer = st.text_input("Buyer Name")
    event = st.text_input("Event Name")
    submitted = st.form_submit_button("Buy Ticket")
    if submitted and buyer and event:
        ticket_id = bc.new_ticket(buyer, event)
        block = bc.new_block(proof=123)
        st.success(f"✅ Ticket purchased! Ticket ID: {ticket_id}")
        st.info(f"Recorded in Block {block['index']}.")

# --- Verify Ticket ---
st.header("🔍 Verify Ticket")
ticket_input = st.text_input("Enter Ticket ID to Verify")
if st.button("Check Ticket"):
    if bc.verify_ticket(ticket_input):
        st.success("✅ Valid ticket! This ticket exists on the blockchain.")
    else:
        st.error("❌ Invalid ticket! No such ticket recorded.")

# --- Blockchain Explorer ---
st.header("📜 Blockchain Explorer")
for block in reversed(bc.chain):
    with st.expander(f"Block {block['index']}"):
        st.write("Previous Hash:", block.get("previous_hash", "N/A"))
        st.write("Hash:", block.get("hash", "N/A"))
        st.json(block.get("tickets", []))
