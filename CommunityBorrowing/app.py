\import sys
import os
import streamlit as st

# Fix import path so src becomes importable
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from services.borrow_service import BorrowService
from dao.user_dao import UserDAO
from dao.item_dao import ItemDAO

# === Page config & CSS ===
st.set_page_config(page_title="Community Borrowing", page_icon="🤝", layout="centered")

st.markdown("""
<style>
/* --- Global --- */
html, body {
  background-color: #f9fafb;
  font-family: 'Inter', sans-serif;
  margin: 0;
  padding: 0;
}

/* Title */
h1 {
  text-align: center;
  color: #1e293b;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

/* Nav bar */
.nav-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0 2rem 0;
}

.nav-button {
  background: #f3f4f6;
  border: none;
  border-radius: 10px;
  padding: 0.6rem 1rem;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.nav-button:hover {
  background: #e5e7eb;
}

.nav-button.active {
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  color: white;
  font-weight: 600;
}

/* Buttons */
.stButton>button {
  width: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  color: white !important;
  border: none;
  border-radius: 14px;
  padding: 0.9rem;
  font-size: 1rem;
  font-weight: 600;
  box-shadow: 0 4px 8px rgba(0,0,0,0.08);
  transition: all 0.25s ease-in-out;
}

.stButton>button:hover {
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  transform: translateY(-2px);
}

/* Inputs */
.stSelectbox, .stTextInput, .stNumberInput {
  border-radius: 12px !important;
  padding: 0.8rem !important;
  font-size: 1rem !important;
  background-color: #ffffff !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.04);
}

/* Container */
.block-container {
  padding-top: 1rem;
  padding-bottom: 3rem;
  max-width: 600px;
  margin: auto;
}

/* Card styles */
.card {
  background-color: #ffffff;
  border-radius: 14px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 3px 6px rgba(0,0,0,0.08);
}

/* Bill card */
.bill-card {
  background: #ffffff;
  border-left: 6px solid #6366f1;
  border-radius: 14px;
  padding: 1.2rem;
  margin-top: 1rem;
  box-shadow: 0 3px 6px rgba(0,0,0,0.12);
  font-size: 1rem;
  line-height: 1.6;
}

.bill-card h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #4f46e5;
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
            ok = BorrowService.return_items(user_id)
            if ok is not None:
                st.markdown(f"""
                <div class="bill-card">
                  <h3>🧾 Return Bill</h3>
                  <p><b>User ID:</b> {user_id}</p>
                  <p><b>Total Amount:</b> ₹{ok}</p>
                  <p>✅ Thank you for using the Community Borrowing System!</p>
                </div>
                """, unsafe_allow_html=True)
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
            <div class="card">
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
            <div class="card">
              <b>{it['item_id']} - {it['item_name']}</b><br>
              💰 Cost: ₹{it.get('cost')}<br>
              <span style="color:{color}; font-weight:600">{it.get('status')}</span>
            </div>
            """, unsafe_allow_html=True)

# === Main Navigation ===
def main():
    st.title("🤝 Community Borrowing System")

    pages = {
        "Create User": create_user_ui,
        "Insert Item": insert_item_ui,
        "Borrow Item": borrow_item_ui,
        "Return & Bill": return_items_ui,
        "List Users": list_users_ui,
        "List Items": list_items_ui
    }

    # --- Session state for active page ---
    if "active_page" not in st.session_state:
        st.session_state.active_page = list(pages.keys())[0]  # default first page

    # --- Custom nav bar ---
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    cols = st.columns(len(pages))
    for i, (name, func) in enumerate(pages.items()):
        if cols[i].button(name, use_container_width=True):
            st.session_state.active_page = name
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Render selected page ---
    pages[st.session_state.active_page]()

if __name__ == "__main__":
    main()
