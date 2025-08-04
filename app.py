import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
import time

# 🔐 Load environment variables
'''load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")'''

url="https://wpitatsigfjhcaqwkqvo.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwaXRhdHNpZ2ZqaGNhcXdrcXZvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwNDYzNjEsImV4cCI6MjA2OTYyMjM2MX0.8vg70wT9HhXa3XlBMnc68Jii8-qUYrz7q8khmUxlsKo"
supabase = create_client(url, key)

st.set_page_config(page_title="Toilettenstatus", page_icon="🚽")
st.title("🚽 Toilettenstatus Monitor")

# 📦 Fetch toilet status
def get_status():
    response = supabase.table("toilet_status").select("*").eq("id", 1).execute()
    if response.data:
        return response.data[0]["state"], response.data[0]["updated_at"]
    return "Unbekannt", None

# 📝 Update toilet status
def update_status(new_state):
    supabase.table("toilet_status").update({
        "state": new_state,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", 1).execute()

# ⏳ Auto-reset logic: If "Besetzt" for more than 5 minutes, set to "Frei"
def auto_reset_if_needed(state, updated):
    if state != "Besetzt" or not updated:
        return state, updated
    utc_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    now_utc = datetime.utcnow()
    elapsed = (now_utc - utc_dt).total_seconds()
    if elapsed > 300:
        update_status("Frei")
        return "Frei", datetime.utcnow().isoformat()
    return state, updated

# ⏱ Remaining time for auto-reset
def get_remaining_time(updated):
    if not updated:
        return None
    utc_dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
    now_utc = datetime.utcnow()
    elapsed = (now_utc - utc_dt).total_seconds()
    remaining = 300 - elapsed
    return max(0, int(remaining))

# 🕒 Convert UTC to German local time
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
        st.experimental_rerun()
with col2:
    if st.button("Setze auf Besetzt 🚫"):
        update_status("Besetzt")
        st.warning("Status wurde auf Besetzt gesetzt!")
        st.experimental_rerun()

# 🔄 Fetch and process status
state, updated = get_status()
state, updated = auto_reset_if_needed(state, updated)
formatted_time = format_german_time(updated)
remaining_seconds = get_remaining_time(updated) if state == "Besetzt" else None

# 🎨 Display status
if state == "Besetzt":
    st.markdown(f"""
        <div style="background-color:#d00000;padding:1.5rem;border-radius:0.5rem;text-align:center;">
            <h2 style="color:white;font-size:2rem;">🚫 BESETZT</h2>
        </div>
    """, unsafe_allow_html=True)

    if remaining_seconds is not None:
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        st.markdown(f"<p style='text-align:center;'>⏳ Automatische Freigabe in <b>{minutes:02d}:{seconds:02d}</b> Minuten</p>", unsafe_allow_html=True)

        # 🔁 Refresh every second for live countdown
        time.sleep(1)
        st.experimental_rerun()

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
