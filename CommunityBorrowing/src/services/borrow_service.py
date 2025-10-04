from src.dao.user_dao import UserDAO
from src.dao.item_dao import ItemDAO
from src.dao.borrow_dao import BorrowDAO

class BorrowService:
    @staticmethod
    def borrow_item(user_id, item_name, name=None, phone=None):
        # Create user if doesn't exist
        user = UserDAO.get_user_by_id(user_id)
        if not user and name and phone:
            user = UserDAO.create_user(name, phone)

        # Find available item by name
        item = ItemDAO.find_available_item_by_name(item_name)
        if not item:
            return None, "No available item with that name."

        # Borrow item
        record = BorrowDAO.borrow_item(user["user_id"], item["item_id"])
        ItemDAO.update_item_status(item["item_id"], "borrowed")
        return record, f"Item '{item_name}' borrowed successfully."

    @staticmethod
    def return_items(user_id):
        borrowed_items = BorrowDAO.get_borrowed_items_by_user(user_id)
        if not borrowed_items:
            return None, 0

        total_cost = 0
        costs = []
        for record in borrowed_items:
            item = record["items"]
            total_cost += item["cost"]
            costs.append(item["cost"])

        BorrowDAO.return_items(user_id)
        return costs, total_cost
