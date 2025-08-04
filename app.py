import streamlit as st
from supabase import create_client
from datetime import datetime
import pytz

# Supabase credentials
url = "https://wpitatsigfjhcaqwkqvo.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwaXRhdHNpZ2ZqaGNhcXdrcXZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwNDYzNjEsImV4cCI6MjA2OTYyMjM2MX0.8vg70wT9HhXa3XlBMnc68Jii8-qUYrz7q8khmUxlsKo"
supabase = create_client(url, key)

st.set_page_config(page_title="Toilettenstatus", page_icon="🚽")
st.title("🚽 Toilettenstatus Monitor")

# 🔧 Functions
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

def format_german_time(utc_string):
    if not utc_string:
        return "Unbekannt"
    utc_dt = datetime.fromisoformat(utc_string.replace("Z", "+00:00"))
    german_tz = pytz.timezone("Europe/Berlin")
    local_dt = utc_dt.astimezone(german_tz)
    return local_dt.strftime("%H:%M:%S")

# 🟢 Handle button clicks
col1, col2 = st.columns(2)
with col1:
    if st.button("Setze auf Frei ✅"):
        update_status("Frei")
        st.success("Status wurde auf Frei gesetzt!")
        st.rerun()
with col2:
    if st.button("Setze auf Besetzt 🚫"):
        update_status("Besetzt")
        st.warning("Status wurde auf Besetzt gesetzt!")
        st.rerun()

# 🔄 Fetch and display latest status
state, updated = get_status()
formatted_time = format_german_time(updated)

# ⏳ Timeout logic: 5 minutes after "Besetzt"
timeout_minutes = 5
now_utc = datetime.utcnow()

if state == "Besetzt" and updated:
    updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    elapsed = (now_utc - updated_dt).total_seconds()
    remaining = timeout_minutes * 60 - elapsed

    if remaining <= 0:
        update_status("Frei")
        st.rerun()
    else:
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        st.info(f"⏳ Automatisch frei in: **{minutes:02d}:{seconds:02d} Minuten**")

# 🎨 Styled status box
if state == "Besetzt":
    st.markdown(f"""
        <div style="background-color:#d00000;padding:1.5rem;border-radius:0.5rem;text-align:center;">
            <h2 style="color:white;font-size:2rem;">🚫 BESETZT</h2>
        </div>
    """, unsafe_allow_html=True)
elif state == "Frei":
    st.markdown(f"""
        <div style="background-color:#00b300;padding:1.5rem;border-radius:0.5rem;text-align:center;">
            <h2 style="color:white;font-size:2rem;">✅ FREI</h2>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"### 🚽 Toilettenstatus: `{state}`")

# 🕒 Show last update time
st.markdown(f"<p style='text-align:center;'>🕒 Zuletzt aktualisiert um <b>{formatted_time}</b></p>", unsafe_allow_html=True)
