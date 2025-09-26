import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []

    def add_transaction(self, sender, receiver, ticket_id, event_name, customer_name=None, phone=None, uid=None, scanned=False):
        tx = {
            "sender": sender,
            "receiver": receiver,
            "ticket_id": ticket_id,
            "event_name": event_name,
            "customer_name": customer_name,
            "phone": phone,
            "uid": uid,
            "scanned": scanned,
            "timestamp": time.time()
        }
        self.pending_transactions.append(tx)
        return tx

    def mine_block(self):
        block = {
            "index": len(self.chain)+1,
            "timestamp": time.time(),
            "transactions": self.pending_transactions.copy(),
            "previous_hash": self.chain[-1]["hash"] if self.chain else "0"
        }
        block["hash"] = str(hash(str(block)))
        self.chain.append(block)
        self.pending_transactions = []
        return block

    def find_ticket(self, ticket_id):
        for block in self.chain:
            for tx in block["transactions"]:
                if tx["ticket_id"] == ticket_id:
                    return tx
        return None
