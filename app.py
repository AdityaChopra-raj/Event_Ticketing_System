import streamlit as st
from blockchain import Blockchain
from events_data import events
from PIL import Image
import uuid
from io import BytesIO
import qrcode  # Now guaranteed to work

# --- Initialize blockchain ---
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
blockchain = st.session_state.blockchain

st.set_page_config(page_title="Event Ticket Portal", layout="wide", page_icon="🎫")

# --- Header ---
st.markdown("<h1 style='text-align:center;color:#004AAD;'>🎫 Event Ticket Portal</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Event Selection ---
st.markdown("<h2 style='color:#004AAD;'>Select Your Event</h2>", unsafe_allow_html=True)
cols = st.columns(2)
selected_event = None

for i, (ename, data) in enumerate(events.items()):
    with cols[i % 2]:
        img = Image.open(data["image"])
        st.image(img, use_column_width=True)
        st.markdown(f"""
        <div style='background-color:#F5F5F5;padding:10px;border-radius:15px;text-align:center;
                    box-shadow:2px 2px 8px #ccc;margin-bottom:15px;'>
            <h3 style='color:#004AAD;font-weight:bold;'>{ename}</h3>
            <p>Tickets Scanned: <b>{data['tickets_scanned']}</b></p>
            <p>Remaining Capacity: <b>{data['capacity']}</b></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Select {ename}"):
            selected_event = ename

# --- Buy or Scan Option ---
if selected_event:
    st.markdown(f"<h2 style='color:#004AAD;'>Selected Event: {selected_event}</h2>", unsafe_allow_html=True)
    choice = st.radio("Choose Action", ["Buy Ticket", "Scan Ticket"])

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

    elif choice == "Scan Ticket":
        st.markdown("### Scan QR Code to Verify Ticket")
        # Generate QR code linking to verification page
        qr_data = f"http://localhost:8501/verify_ticket?event={selected_event}"
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        qr_img.save(buf)
        st.image(buf)
        st.info("Scan this QR Code to go to ticket verification page")
