import streamlit as st
from supabase import create_client
from datetime import datetime

# Supabase credentials
url = "https://your-project-id.supabase.co"
key = "your-anon-key"
supabase = create_client(url, key)

st.set_page_config(page_title="Toilet Status", page_icon="🚽")
st.title("🚽 Toilet Usage Monitor")

def get_status():
    response = supabase.table("toilet_status").select("*").eq("id", 1).execute()
    if response.data:
        return response.data[0]["state"], response.data[0]["updated_at"]
    return "Unknown", None

def update_status(new_state):
    supabase.table("toilet_status").update({
        "state": new_state,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", 1).execute()

state, updated = get_status()
st.markdown(f"### 🚽 Toilet is: `{state}`")
st.markdown(f"_Last updated: {updated}_")

col1, col2 = st.columns(2)
with col1:
    if st.button("Set to Free ✅"):
        update_status("Free")
        st.success("Status updated to Free!")
with col2:
    if st.button("Set to Occupied 🚫"):
        update_status("Occupied")
        st.warning("Status updated to Occupied!")
