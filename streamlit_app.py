import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(layout="wide", page_title="Where's Owen?")

# Clean, professional sans-serif styling
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Where's Owen?")
st.markdown("Real-time tracking of Owen's global engagements, field trials, and upcoming travel.")
st.markdown("---")

# 1. SIDEBAR FILE UPLOADER
st.sidebar.markdown("### Update Dashboard Data")
uploaded_file = st.sidebar.file_uploader("Upload a new schedule CSV file", type=["csv"])

# 2. DATA PROCESSING (Fallback to mock data if no upload)
@st.cache_data
def get_default_data():
    data = [
        {'Event': 'APAC Expansion Kickoff', 'Location Name': 'Singapore', 'Latitude': 1.3521, 'Longitude': 103.8198, 'Start Date': '2026-06-10', 'End Date': '2026-06-18', 'Type': 'Conference'},
        {'Event': 'London Tech Roundtable', 'Location Name': 'London, UK', 'Latitude': 51.5074, 'Longitude': -0.1278, 'Start Date': '2026-07-10', 'End Date': '2026-07-22', 'Type': "Owen's Events"},
        {'Event': 'Municipal Smart Grid Sync', 'Location Name': 'Paris, France', 'Latitude': 48.8566, 'Longitude': 2.3522, 'Start Date': '2026-08-05', 'End Date': '2026-08-12', 'Type': 'Current RFPs'},
        {'Event': 'LATAM Partner Field Trials', 'Location Name': 'São Paulo, Brazil', 'Latitude': -23.5505, 'Longitude': -46.6333, 'Start Date': '2026-09-15', 'End Date': '2026-09-30', 'Type': 'Current Explorers'}
    ]
    return pd.DataFrame(data)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("Successfully loaded uploaded CSV data!")
    except Exception as e:
        st.sidebar.error("Error reading file. Falling back to defaults.")
        df = get_default_data()
else:
    df = get_default_data()

# Clean dates
df['Start Date'] = pd.to_datetime(df['Start Date'])
df['End Date'] = pd.to_datetime(df['End Date'])

# 3. CHRONOLOGICAL CALCULATIONS
today = datetime.now()

def determine_status(row):
    if row['End Date'] < today:
        return 'Past'
    elif row['Start Date'] <= today <= row['End Date']:
        return 'Current'
    else:
        return 'Upcoming'

df['Timeline Status'] = df.apply(determine_status, axis=1)


# ==========================================
# SECTION 1 (TOP): CHRONOLOGICAL STATUS BOARDS
# ==========================================
col_curr, col_up, col_past = st.columns(3)

with col_curr:
    st.subheader("Right Now")
    current_trip = df[df['Timeline Status'] == 'Current']
    if not current_trip.empty:
        for _, row in current_trip.iterrows():
            st.error(f"**{row['Event']}**\n\n{row['Location Name']}\n\nEnds {row['End Date'].strftime('%B %d, %Y')}")
    else:
        st.write("Owen is currently at the home office.")

with col_up:
    st.subheader("Coming Up")
    upcoming_trips = df[df['Timeline Status'] == 'Upcoming'].sort_values('Start Date')
    if not upcoming_trips.empty:
        for _, row in upcoming_trips.iterrows():
            st.markdown(f"**{row['Start Date'].strftime('%b %d')}**: {row['Event']} ({row['Location Name']})")
    else:
        st.write("No upcoming travel scheduled.")

with col_past:
    st.subheader("Past Engagements")
    past_trips = df[df['Timeline Status'] == 'Past'].sort_values('Start Date', ascending=False)
    if not past_trips.empty:
        for _, row in past_trips.iterrows():
            st.markdown(f"*{row['Start Date'].strftime('%b %Y')}* — {row['Event']}")
    else:
        st.write("No historical entries logged.")


# ==========================================
# SECTION 2 (MIDDLE): SCHEDULE REGISTRY LEDGER
# ==========================================
st.markdown("---")
st.subheader("Full Schedule Registry")
st.dataframe(df, use_container_width=True, hide_index=True)


# ==========================================
# SECTION 3 (BOTTOM): REGIONAL MAP
# ==========================================
st.markdown("---")
st.subheader("Regional Engagements Map")

m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

# Muted, corporate color configuration
color_map = {'Current': 'red', 'Upcoming': 'purple', 'Past': 'gray'}

for idx, row in df.iterrows():
    status = row['Timeline Status']
    icon_type = 'star' if status == 'Current' else 'info-sign'
    
    popup_html = f"""
    <div style='font-family: sans-serif; font-size: 13px; line-height: 1.4; width: 200px;'>
        <b style='color: { "red" if status=="Current" else "#333" }; font-size: 14px;'>[{status}] {row['Event']}</b><br>
        <b>Where:</b> {row['Location Name']}<br>
        <b>Dates:</b> {row['Start Date'].strftime('%b %d')} - {row['End Date'].strftime('%b %d, %Y')}
    </div>
    """
    
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=popup_html,
        icon=folium.Icon(color=color_map[status], icon=icon_type)
    ).add_to(m)

st_folium(m, width="100%", height=450, key="owen_map")