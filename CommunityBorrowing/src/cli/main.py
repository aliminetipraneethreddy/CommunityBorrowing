from src.services.borrow_service import BorrowService
from src.dao.user_dao import UserDAO
from src.dao.item_dao import ItemDAO
from src.dao.supabase_client import supabase


def menu():
    print("\n===== Community Borrowing System =====")
    print("1. Create User")
    print("2. Insert Item")
    print("3. Borrow Item")
    print("4. Return Items & Generate Bill")
    print("5. Exit")
    print("6. List All Users")   # ✅ Added
    print("7. List All Items")
    
    choice = input("Enter choice: ")
    return choice
def list_all_items():
    items = ItemDAO.list_items()
    if not items:
        print("⚠️ No items found.")
        return
    print("\n===== Items =====")
    for i in items:
        print(f"ID: {i['item_id']}, Name: {i['item_name']}, Status: {i['status']}, Cost: {i['cost']}")



def list_all_users():
    users = UserDAO.list_users()
    if not users:
        print("⚠️ No users found.")
        return
    print("\n===== Users =====")
    for u in users:
        print(f"ID: {u['user_id']}, Name: {u['name']}, Phone: {u['phone_number']}")


def main():
    while True:
        choice = menu()
        if choice == "1":
            create_user()
        elif choice == "2":
            insert_item()
        elif choice == "3":
            borrow_item()
        elif choice == "4":
            return_items()
        elif choice == "5":
            print("👋 Exiting...")
            break
        elif choice == "6":
            list_all_users()   # ✅ Call new function
        elif choice == "7":
            list_all_items()
        else:
            print("❌ Invalid choice. Try again.")
            break


if __name__ == "__main__":
    main()
