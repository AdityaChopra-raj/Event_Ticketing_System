import os
import streamlit as st
from blockchain import Blockchain
from events_data import events
from PIL import Image
import uuid
from io import BytesIO
import qrcode

# --- Initialize blockchain ---
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
blockchain = st.session_state.blockchain

# --- Set base directory ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Streamlit page config ---
st.set_page_config(page_title="Event Ticket Portal", layout="wide", page_icon="🎫")

# --- Header ---
st.markdown("<h1 style='text-align:center;color:#004AAD;'>🎫 Event Ticket Portal</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Netflix-style Event Selection with sleek centered buttons ---
st.markdown("<h2 style='color:#004AAD;'>Select Your Event</h2>", unsafe_allow_html=True)

cards_per_row = 4
cols = st.columns(cards_per_row)
selected_event = None

for i, (ename, data) in enumerate(events.items()):
    col = cols[i % cards_per_row]

    img_path = os.path.join(BASE_DIR, data["image"])
    if not os.path.exists(img_path):
        col.error(f"Image not found: {img_path}")
        continue

    img = Image.open(img_path)
    col.image(img, width=250, use_column_width=False)

    # Centered button + stats
    card_html = f"""
    <div style='text-align:center; margin-top:-10px;'>
        <div style="
            background-color:#E50914;
            color:white;
            font-weight:bold;
            padding:8px 12px;
            border-radius:5px;
            display:inline-block;
            cursor:pointer;
            font-family: Arial, sans-serif;
            box-shadow: 2px 2px 6px #aaa;
            transition: transform 0.2s;
        " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            {ename}
        </div>

        <p style='font-size:12px;margin:2px 0;'>Tickets Scanned: <b>{data['tickets_scanned']}</b></p>
        <p style='font-size:12px;margin:2px 0;'>Remaining Capacity: <b>{data['capacity']}</b></p>
    </div>
    """

    col.markdown(card_html, unsafe_allow_html=True)

    # Functional Streamlit button below
    if col.button(f"Select {ename}", key=f"btn_{i}"):
        selected_event = ename

# --- Buy or Scan Option ---
if selected_event:
    st.markdown(f"<h2 style='color:#004AAD;'>Selected Event: {selected_event}</h2>", unsafe_allow_html=True)
    choice = st.radio("Choose Action", ["Buy Ticket", "Scan Ticket"])

    # --- Buy Ticket Flow ---
    if choice == "Buy Ticket":
        st.markdown("### Enter Your Details")
        name = st.text_input("Name")
        phone = st.text_input("Phone Number")
        uid = st.text_input("Unique ID (UID)")

        if st.button("Confirm Purchase"):
            if not name or not phone or not uid:
                st.warning("Please fill all fields")
            elif events[selected_event]["capacity"] <= 0:
                st.error("Sorry, event is full!")
            else:
                ticket_id = str(uuid.uuid4())[:8]
                blockchain.add_transaction(
                    sender="system",
                    receiver="customer",
                    ticket_id=ticket_id,
                    event_name=selected_event,
                    customer_name=name,
                    phone=phone,
                    uid=uid,
                    scanned=False
                )
                blockchain.mine_block()
                events[selected_event]["capacity"] -= 1
                st.success(f"✅ Ticket Purchased Successfully! Your Ticket ID: {ticket_id}")

    # --- Scan Ticket Flow ---
    elif choice == "Scan Ticket":
        st.markdown("### Scan QR Code to Verify Ticket")
        qr_data = f"http://localhost:8501/verify_ticket?event={selected_event}"  # Replace with deployed URL
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        qr_img.save(buf)
        st.image(buf)
        st.info("Scan this QR Code to go to the ticket verification page")
