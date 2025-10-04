import streamlit as st
from src.services.borrow_service import BorrowService
from src.dao.user_dao import UserDAO
from src.dao.item_dao import ItemDAO
from src.dao.supabase_client import supabase

# =============================
# GLOBAL PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Community Borrowing System",
    page_icon="🤝",
    layout="centered"
)

# =============================
# CUSTOM MOBILE-FIRST CSS
# =============================
st.markdown("""
<style>
/* Mobile-first approach */
html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background-color: #f8fafc;
}

h1, h2, h3 {
    text-align: center;
    color: #2d3436;
    font-weight: 700;
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

# =============================
# HELPER FUNCTIONS
# =============================

def show_message(success, msg):
    if success:
        st.success(f"✅ {msg}")
    else:
        st.error(f"❌ {msg}")


# =============================
# PAGE FUNCTIONS
# =============================

def create_user_ui():
    st.header("🧍 Create User")
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")

    if st.button("Create User"):
        if not name or not phone:
            st.warning("Please enter both name and phone.")
            return
        result = UserDAO.create_user(name, phone)
        if result:
            show_message(True, f"User '{name}' created successfully!")
        else:
            show_message(False, "Failed to create user.")


def insert_item_ui():
    st.header("📦 Insert New Item")
    name = st.text_input("Item Name")
    cost = st.number_input("Cost per Day", min_value=0.0, step=1.0)

    if st.button("Add Item"):
        if not name:
            st.warning("Please enter item name.")
            return
        result = ItemDAO.insert_item(name, cost)
        if result:
            show_message(True, f"Item '{name}' added successfully!")
        else:
            show_message(False, "Failed to add item.")


def borrow_item_ui():
    st.header("📥 Borrow Item")

    users = UserDAO.list_users() or []
    items = ItemDAO.list_items() or []

    available_items = [i for i in items if i.get("status", "").lower() == "available"]

    if not users:
        st.warning("No users found. Please create a user first.")
        return
    if not available_items:
        st.warning("No items available to borrow.")
        return

    user_choice = st.selectbox(
        "Select User",
        [f"{u['user_id']} - {u['name']}" for u in users]
    )
    item_choice = st.selectbox(
        "Select Item",
        [f"{i['item_id']} - {i['item_name']} (available)" for i in available_items]
    )

    if st.button("📦 Borrow Item"):
        try:
            user_id = int(user_choice.split(" - ")[0])
            # Extract item name (BorrowService expects name)
            name_part = item_choice.split(" - ", 1)[1]
            item_name = name_part.rsplit("(", 1)[0].strip()

            result = BorrowService.borrow_item(user_id, item_name)
            if result:
                show_message(True, f"'{item_name}' borrowed successfully!")
            else:
                show_message(False, f"Could not borrow '{item_name}'. Check logs.")
        except Exception as e:
            show_message(False, f"Error: {e}")


def return_item_ui():
    st.header("🔁 Return Items & Generate Bill")
    user_choice = st.text_input("Enter User ID")

    if st.button("Return Items"):
        try:
            result = BorrowService.return_items(user_choice)
            if result:
                show_message(True, "Items returned and bill generated successfully!")
            else:
                show_message(False, "Failed to return items.")
        except Exception as e:
            show_message(False, f"Error: {e}")


def list_users_ui():
    st.header("👥 All Users")
    users = UserDAO.list_users() or []
    if not users:
        st.info("No users found.")
        return
    for u in users:
        st.markdown(f"**{u['user_id']} - {u['name']}**  📞 {u['phone_number']}")


def list_items_ui():
    st.header("📋 All Items")
    items = ItemDAO.list_items() or []
    if not items:
        st.info("No items found.")
        return
    for i in items:
        status_color = "#10b981" if i["status"].lower() == "available" else "#ef4444"
        st.markdown(f"""
        <div style='background-color:#fff;border-radius:10px;padding:10px;margin-bottom:6px;
        box-shadow:0 2px 4px rgba(0,0,0,0.05)'>
        <b>{i['item_id']} - {i['item_name']}</b><br>
        💲 {i['cost']} | 
        <span style='color:{status_color};font-weight:600'>{i['status']}</span>
        </div>
        """, unsafe_allow_html=True)

# =============================
# MAIN NAVIGATION
# =============================

def main():
    st.title("🤝 Community Borrowing System")

    pages = {
        "Create User": create_user_ui,
        "Insert Item": insert_item_ui,
        "Borrow Item": borrow_item_ui,
        "Return Items & Bill": return_item_ui,
        "List Users": list_users_ui,
        "List Items": list_items_ui
    }

    choice = st.sidebar.radio("📍 Navigation", list(pages.keys()))

    # Render selected page
    pages[choice]()

if __name__ == "__main__":
    main()
