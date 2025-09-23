from .supabase_client import supabase

class UserDAO:
    @staticmethod
    def create_user(name, phone):
        response = supabase.table("users").insert({
            "name": name,
            "phone_number": phone
        }).execute()
        return response.data[0]

    @staticmethod
    def get_user_by_id(user_id):
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None

    @staticmethod
    def list_users():
        """Fetch all users"""
        response = supabase.table("users").select("*").execute()
        return response.data
