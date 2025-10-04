import sys
import os
import streamlit as st

# Fix import path so src becomes importable
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from services.borrow_service import BorrowService
from dao.user_dao import UserDAO
from dao.item_dao import ItemDAO
from dao.supabase_client import supabase

# === Page config ===
st.set_page_config(page_title="Community Borrowing", page_icon="🤝", layout="centered")

# === Global CSS ===
st.markdown("""
<style>
/* Global styles */
html, body {
  background-color: #f5f7fa;
  font-family: 'Inter', sans-serif;
  color: #111827 !important; /* Force dark readable text globally */
}

/* Title */
h1, h2, h3 {
  text-align: center;
  color: #111827 !important;
}

/* Buttons */
.stButton>button {
  background: #f3f4f6;
  color: #111827 !important;
  border: none;
  border-radius: 12px;
  padding: 0.7rem 1rem;
  font-size: 0.95rem;
  font-weight: 500;
  width: 100%;
  transition: all 0.2s ease-in-out;
}

.stButton>button:hover {
  background: #e5e7eb;
}

.stButton>button:focus, .stButton>button:active {
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  color: white !important;
  font-weight: 600;
}

/* Inputs */
.stSelectbox, .stTextInput, .stNumberInput {
  border-radius: 10px !important;
  padding: 0.6rem !important;
  font-size: 1rem !important;
  color: #111827 !important;
}

/* Container */
.block-container {
  padding-top: 1rem;
  padding-bottom: 3rem;
  max-width: 600px;
  margin: auto;
  color: #111827 !important;
}

/* Bill Card */
.bill-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-top: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  font-size: 1rem;
  color: #111827 !important;
}
.bill-header {
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 8px;
  color: #111827 !important;
}
.bill-line {
  margin: 4px 0;
  color: #111827 !important;
}
.bill-total {
  font-weight: 700;
  color: #4f46e5 !important;
  margin-top: 10px;
  font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

# === Helper for messages ===
def show_message(success: bool, msg: str):
    if success:
        st.success(f"✅ {msg}")
    else:
        st.error(f"❌ {msg}")

# === UI Pages ===
def create_user_ui():
    st.header("🧍 Create User")
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    if st.button("Create User"):
        if not name or not phone:
            st.warning("Please fill both name and phone.")
        else:
            res = UserDAO.create_user(name, phone)
            if res:
                show_message(True, f"User '{name}' created!")
            else:
                show_message(False, "Failed to create user.")

def insert_item_ui():
    st.header("📦 Insert Item")
    name = st.text_input("Item Name")
    cost = st.number_input("Cost per Day", min_value=0.0, step=1.0)
    if st.button("Add Item"):
        if not name:
            st.warning("Enter item name.")
        else:
            res = ItemDAO.insert_item(name, cost)
            if res:
                show_message(True, f"Item '{name}' added!")
            else:
                show_message(False, "Failed to add item.")

def borrow_item_ui():
    st.header("📥 Borrow Item")
    users = UserDAO.list_users() or []
    items = ItemDAO.list_items() or []
    available = [it for it in items if it.get("status", "").lower() == "available"]

    if not users:
        st.warning("No users found. Please create user first.")
        return
    if not available:
        st.warning("No items available to borrow.")
        return

    user_choice = st.selectbox("Select User", [f"{u['user_id']} - {u['name']}" for u in users])
    item_choice = st.selectbox("Select Item", [f"{it['item_id']} - {it['item_name']} (available)" for it in available])

    if st.button("Borrow Item"):
        try:
            user_id = int(user_choice.split(" - ")[0])
            # Extract item name
            name_part = item_choice.split(" - ", 1)[1]
            item_name = name_part.rsplit("(", 1)[0].strip()

            ok = BorrowService.borrow_item(user_id, item_name)
            if ok:
                show_message(True, f"Borrowed '{item_name}' successfully.")
            else:
                show_message(False, f"Could not borrow '{item_name}'.")
        except Exception as e:
            show_message(False, f"Error: {e}")

def return_items_ui():
    st.header("🔁 Return Items & Generate Bill")
    user_id = st.text_input("Enter User ID")

    if st.button("Return Items"):
        try:
            bill = BorrowService.return_items(user_id)
            if bill is not None:
                # Fancy Bill UI
                st.markdown("<div class='bill-card'>", unsafe_allow_html=True)
                st.markdown("<div class='bill-header'>🧾 Borrowing Bill</div>", unsafe_allow_html=True)

                for line in bill.get("items", []):
                    st.markdown(f"<div class='bill-line'>• {line['item_name']} → ₹{line['cost']} x {line['days']} days = ₹{line['total']}</div>", unsafe_allow_html=True)

                st.markdown(f"<div class='bill-total'>Total Bill: ₹{bill.get('total', 0)}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                show_message(False, "Failed to return items.")
        except Exception as e:
            show_message(False, f"Error: {e}")

def list_users_ui():
    st.header("👥 Users")
    users = UserDAO.list_users() or []
    if not users:
        st.info("No users found.")
    else:
        for u in users:
            st.markdown(f"""
            <div style="
              background-color:#fff;
              border-radius:10px;
              padding:10px;
              margin-bottom:6px;
              box-shadow:0 2px 4px rgba(0,0,0,0.05);
              color:#111827;
            ">
              <b>{u['user_id']} - {u['name']}</b><br>
              📞 {u['phone_number']}
            </div>
            """, unsafe_allow_html=True)

def list_items_ui():
    st.header("📋 Items")
    items = ItemDAO.list_items() or []
    if not items:
        st.info("No items found.")
    else:
        for it in items:
            color = "#10b981" if it.get("status","").lower() == "available" else "#ef4444"
            st.markdown(f"""
            <div style="
              background-color:#fff;
              border-radius:10px;
              padding:12px;
              margin-bottom:10px;
              box-shadow:0 2px 6px rgba(0,0,0,0.08);
              color:#111827;
            ">
              <b>{it['item_id']} - {it['item_name']}</b><br>
              💰 Cost: ₹{it.get('cost')}<br>
              <span style="color:{color}; font-weight:600">{it.get('status')}</span>
            </div>
            """, unsafe_allow_html=True)

# === Main Navigation ===
def main():
    st.title("🤝 Community Borrowing System")

    pages = {
        "👤 Create User": create_user_ui,
        "📦 Insert Item": insert_item_ui,
        "📥 Borrow Item": borrow_item_ui,
        "🔁 Return & Bill": return_items_ui,
        "👥 List Users": list_users_ui,
        "📋 List Items": list_items_ui
    }

    # Track active page
    if "active_page" not in st.session_state:
        st.session_state.active_page = list(pages.keys())[0]

    # Horizontal nav bar
    cols = st.columns(len(pages))
    for i, (name, func) in enumerate(pages.items()):
        if cols[i].button(name, key=f"nav_{i}"):
            st.session_state.active_page = name

    # Render selected page
    pages[st.session_state.active_page]()

if __name__ == "__main__":
    main()
