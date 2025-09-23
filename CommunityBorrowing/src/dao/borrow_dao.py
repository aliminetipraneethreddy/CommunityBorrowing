from .supabase_client import supabase

class BorrowDAO:
    @staticmethod
    def borrow_item(user_id, item_id):
        response = supabase.table("borrows").insert({
            "user_id": user_id,
            "item_id": item_id
        }).execute()
        return response.data[0] if response.data else None

    @staticmethod
    def get_borrowed_items_by_user(user_id):
        response = supabase.table("borrows").select("*, items(*)").eq("user_id", user_id).execute()
        return response.data

    @staticmethod
    def return_items(user_id):
        borrowed_items = supabase.table("borrows").select("*").eq("user_id", user_id).execute()

        for record in borrowed_items.data:
            # ✅ Update item back to available
            supabase.table("items").update({"status": "available"}).eq("item_id", record["item_id"]).execute()

            # ✅ Delete borrow record using borrow_id (correct PK)
            supabase.table("borrows").delete().eq("borrow_id", record["borrow_id"]).execute()

        return borrowed_items.data
