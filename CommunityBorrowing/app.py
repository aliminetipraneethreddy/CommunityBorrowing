# app.py (place at root of CommunityBorrowing folder, next to src/)

import sys
import os
import streamlit as st

# Fix import path so src becomes importable
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from services.borrow_service import BorrowService
from dao.user_dao import UserDAO
from dao.item_dao import ItemDAO
from dao.supabase_client import supabase

# === Page config & CSS ===
st.set_page_config(page_title="Community Borrowing", page_icon="🤝", layout="centered")

st.markdown("""
<style>
/* Mobile-first styling */
html, body {
  background-color: #f5f7fa;
  font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
  text-align: center;
  color: #2d3436;
}

.stButton>button {
  width: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.75rem;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.stButton>button:hover {
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  transform: scale(1.02);
}

.stSelectbox, .stTextInput, .stNumberInput {
  border-radius: 10px !important;
  padding: 0.6rem !important;
  font-size: 1rem !important;
}

.block-container {
  padding-top: 1rem;
  padding-bottom: 3rem;
  max-width: 600px;
  margin: auto;
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
            # Extract item name for BorrowService
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
    user_id = st.text_input("User ID to Return Items")
    if st.button("Return Items"):
        try:
            ok = BorrowService.return_items(user_id)
            if ok is not None:
                show_message(True, f"Returned items. Bill = {ok}")
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
            st.markdown(f"**{u['user_id']} - {u['name']}** • 📞 {u['phone_number']}")

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
              padding:10px;
              margin-bottom:6px;
              box-shadow:0 2px 4px rgba(0,0,0,0.05);
            ">
              <b>{it['item_id']} - {it['item_name']}</b><br>
              Cost: ₹{it.get('cost')} | <span style="color:{color}; font-weight:600">{it.get('status')}</span>
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
    choice = st.sidebar.radio("Menu", list(pages.keys()))
    pages[choice]()

if __name__ == "__main__":
    main()
