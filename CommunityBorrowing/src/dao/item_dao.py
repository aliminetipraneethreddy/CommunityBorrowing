from .supabase_client import supabase

class ItemDAO:
    @staticmethod
    def insert_item(item_name, cost):
        response = supabase.table("items").insert({
            "item_name": item_name,
            "status": "available",
            "cost": cost
        }).execute()
        return response.data[0]

    @staticmethod
    def get_available_item_by_name(item_name):
        response = supabase.table("items").select("*").eq("item_name", item_name).eq("status", "available").execute()
        return response.data[0] if response.data else None

    @staticmethod
    def update_item_status(item_id, status):
        supabase.table("items").update({"status": status}).eq("item_id", item_id).execute()

    @staticmethod
    def list_items():
        """Fetch all items"""
        response = supabase.table("items").select("*").execute()
        return response.data
    from .supabase_client import supabase

class ItemDAO:
    @staticmethod
    def insert_item(item_name, cost):
        response = supabase.table("items").insert({
            "item_name": item_name,
            "status": "available",
            "cost": cost
        }).execute()
        return response.data[0]

    @staticmethod
    def get_available_item_by_name(item_name):
        response = supabase.table("items").select("*").eq("item_name", item_name).eq("status", "available").execute()
        return response.data[0] if response.data else None

    @staticmethod
    def update_item_status(item_id, status):
        supabase.table("items").update({"status": status}).eq("item_id", item_id).execute()

    @staticmethod
    def list_items():
        """Fetch all items"""
        response = supabase.table("items").select("*").execute()
        return response.data

