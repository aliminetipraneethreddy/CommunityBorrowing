import streamlit as st
from src.services.borrow_service import BorrowService
from src.dao.user_dao import UserDAO
from src.dao.item_dao import ItemDAO
from src.dao.supabase_client import supabase

# -----------------------
# Custom CSS - Full Responsive Layout
# -----------------------
def load_css():
    st.markdown("""
        <style>
        /* General Layout */
        .block-container {
            padding: 1rem;
            max-width: 100% !important;
        }

        body {
            background-color: #f5f7fa;
        }

        /* Top Navigation Bar */
        .nav-container {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            background-color: #ffffff;
            border-radius: 12px;
            padding: 0.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1.2rem;
        }

        .nav-button {
            flex: 1 1 auto;
            text-align: center;
            background-color: #3498db;
            color: white;
            padding: 0.6rem;
            margin: 0.2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
        }

        .nav-button:hover {
            background-color: #2980b9;
        }

        /* Headings */
        h1, h2 {
            text-align: center;
            color: #2C3E50;
        }

        /* Cards */
        .stForm, .stTable, .css-1r6slb0 {
            background: #ffffff;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }

        /* Buttons */
        button[kind="primary"] {
            background-color: #3498db !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            width: 100% !important;
            padding: 0.7rem !important;
        }

        /* Table responsiveness */
        .stTable {
            overflow-x: auto;
        }

        input, select {
            width: 100% !important;
        }

        /* Hide Streamlit default hamburger menu & footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# -----------------------
# Pages
# -----------------------

def create_user_ui():
    st.header("👤 Create User")
    with st.form("create_user_form"):
        name = st.text_input("Enter Name")
        phone = st.text_input("Enter Phone Number")
        submit = st.form_submit_button("➕ Create User")
    if submit:
        if not name or not phone:
            st.warning("⚠️ Please enter all details")
        else:
            user = UserDAO.create_user(name, phone)
            if user:
                st.success(f"✅ User created: {user['name']} (ID: {user['user_id']})")
            else:
                st.error("❌ Failed to create user")

def insert_item_ui():
    st.header("📦 Insert Item")
    with st.form("insert_item_form"):
        name = st.text_input("Item Name")
        cost = st.number_input("Cost", min_value=0.0, step=0.5)
        submit = st.form_submit_button("➕ Add Item")
    if submit:
        if not name:
            st.warning("⚠️ Item name required")
        else:
            item = ItemDAO.insert_item(name, cost)
            if item:
                st.success(f"✅ Item added: {item['item_name']} (ID: {item['item_id']})")
            else:
                st.error("❌ Failed to add item")

def borrow_item_ui():
    st.header("📑 Borrow Item")
    users = UserDAO.list_users()
    items = ItemDAO.list_items()

    if not users or not items:
        st.warning("⚠️ Need users and items before borrowing.")
        return

    user_choice = st.selectbox("Select User", [f"{u['user_id']} - {u['name']}" for u in users])
    item_choice = st.selectbox("Select Item", [f"{i['item_id']} - {i['item_name']} ({i['status']})" for i in items])
    borrow_btn = st.button("📥 Borrow Item")

    if borrow_btn:
        user_id = int(user_choice.split(" - ")[0])
        item_id = int(item_choice.split(" - ")[0])
        result = BorrowService.borrow_item(user_id, item_id)
        if result:
            st.success("✅ Item borrowed successfully")
        else:
            st.error("❌ Failed to borrow item")

def return_items_ui():
    st.header("🔄 Return Items & Generate Bill")
    users = UserDAO.list_users()

    if not users:
        st.warning("⚠️ No users found")
        return

    user_choice = st.selectbox("Select User", [f"{u['user_id']} - {u['name']}" for u in users])
    return_btn = st.button("📤 Return Items")

    if return_btn:
        user_id = int(user_choice.split(" - ")[0])
        bill = BorrowService.return_items(user_id)
        if bill:
            st.success(f"✅ Items returned. Total Bill: ₹{bill}")
        else:
            st.error("❌ Failed to return items")

def list_all_users_ui():
    st.header("👥 All Users")
    users = UserDAO.list_users()
    if not users:
        st.warning("⚠️ No users found")
        return
    st.table(users)

def list_all_items_ui():
    st.header("📦 All Items")
    items = ItemDAO.list_items()
    if not items:
        st.warning("⚠️ No items found")
        return
    st.table(items)

# -----------------------
# Main App
# -----------------------

def main():
    st.set_page_config(page_title="Community Borrowing System", page_icon="🤝", layout="centered")
    load_css()
    st.title("🤝 Community Borrowing System")

    # Create a top navigation bar (mobile-friendly)
    nav_options = ["Create User", "Insert Item", "Borrow Item", "Return Items", "All Users", "All Items"]
    nav_labels = {
        "Create User": "👤",
        "Insert Item": "📦",
        "Borrow Item": "📑",
        "Return Items": "🔄",
        "All Users": "👥",
        "All Items": "📋"
    }

    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    cols = st.columns(len(nav_options))
    selected_page = None
    for i, page in enumerate(nav_options):
        if cols[i].button(f"{nav_labels[page]} {page}"):
            st.session_state["page"] = page
    st.markdown("</div>", unsafe_allow_html=True)

    # Default page
    if "page" not in st.session_state:
        st.session_state["page"] = "Create User"

    selected_page = st.session_state["page"]

    # Route to correct UI
    if selected_page == "Create User":
        create_user_ui()
    elif selected_page == "Insert Item":
        insert_item_ui()
    elif selected_page == "Borrow Item":
        borrow_item_ui()
    elif selected_page == "Return Items":
        return_items_ui()
    elif selected_page == "All Users":
        list_all_users_ui()
    elif selected_page == "All Items":
        list_all_items_ui()


if __name__ == "__main__":
    main()
