import streamlit as st
from supabase import create_client
from datetime import datetime

# Supabase credentials
url = "https://wpitatsigfjhcaqwkqvo.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwaXRhdHNpZ2ZqaGNhcXdrcXZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwNDYzNjEsImV4cCI6MjA2OTYyMjM2MX0.8vg70wT9HhXa3XlBMnc68Jii8-qUYrz7q8khmUxlsKo"
supabase = create_client(url, key)

st.set_page_config(page_title="Toilettenstatus", page_icon="🚽")
st.title("🚽 Toilettenstatus Monitor")

def get_status():
    response = supabase.table("toilet_status").select("*").eq("id", 1).execute()
    if response.data:
        return response.data[0]["state"], response.data[0]["updated_at"]
    return "Unbekannt", None

def update_status(new_state):
    supabase.table("toilet_status").update({
        "state": new_state,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", 1).execute()

# 🟢 Handle button clicks first
if st.button("Setze auf Frei ✅"):
    update_status("Frei")
    st.success("Status wurde auf Frei gesetzt!")

if st.button("Setze auf Besetzt 🚫"):
    update_status("Besetzt")
    st.warning("Status wurde auf Besetzt gesetzt!")

# 🔄 Fetch and display latest status
state, updated = get_status()

# 🎨 Styled status box
if state == "Besetzt":
    st.markdown(f"""
        <div style="background-color:#d00000;padding:1rem;border-radius:0.5rem;text-align:center;">
            <h2 style="color:white;">🚫 BESETZT</h2>
        </div>
    """, unsafe_allow_html=True)
elif state == "Frei":
    st.markdown(f"""
        <div style="background-color:#00b300;padding:1rem;border-radius:0.5rem;text-align:center;">
            <h2 style="color:white;">✅ FREI</h2>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"### 🚽 Toilettenstatus: `{state}`")

st.markdown(f"_Zuletzt aktualisiert: {updated}_")
