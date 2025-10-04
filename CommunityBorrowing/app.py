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

    # Keep selection in session_state
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Create User"

    # Horizontal nav bar with rectangle buttons
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    cols = st.columns(len(pages))
    for i, (name, func) in enumerate(pages.items()):
        if cols[i].button(name, key=name):
            st.session_state.active_page = name
    st.markdown('</div>', unsafe_allow_html=True)

    # Run the active page
    pages[st.session_state.active_page]()
