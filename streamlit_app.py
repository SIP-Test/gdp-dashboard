import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Set page to wide mode to give the map breathing room
st.set_page_config(layout="wide", page_title="Global Project Dashboard")

st.title("🗺️ Team Activity Tracker (Prototype)")
st.caption("A test playground using mock data to track global events.")

# 1. GENERATE FAKE DATA FOR TESTING
@st.cache_data
def get_mock_data():
    return pd.DataFrame({
        'Project Name': ['Project Alpha (Tech Hub)', 'APAC Expansion Kickoff', 'EMEA Logistics Sync', 'LATAM Field Trials'],
        'Region': ['North America', 'APAC', 'Europe', 'South America'],
        'Latitude': [37.7749, 1.3521, 48.8566, -23.5505],
        'Longitude': [-122.4194, 103.8198, 2.3522, -46.6333],
        'Status': ['Active', 'New', 'Active', 'Pending'],
        'Start Date': ['2026-08-01', '2026-09-15', '2026-07-20', '2026-11-05'],
        'Lead': ['Sarah Jenkins', 'Alex Wong', 'Elena Rostova', 'Carlos Silva']
    })

df = get_mock_data()

# 2. RENDER THE INTERACTIVE MAP
st.subheader("Active Regional Events")

# Initialize map centered on the ocean/equator
m = folium.Map(location=[15, 0], zoom_start=2, tiles="CartoDB positron")

# Color mapping helper for pins
status_colors = {'Active': 'green', 'New': 'blue', 'Pending': 'orange'}

# Drop the markers onto the map
for idx, row in df.iterrows():
    popup_text = f"""
    <div style='width: 200px;'>
        <h4>{row['Project Name']}</h4>
        <b>Status:</b> {row['Status']}<br>
        <b>Start Date:</b> {row['Start Date']}<br>
        <b>Team Lead:</b> {row['Lead']}
    </div>
    """
    folium.Marker(
        [row['Latitude'], row['Longitude']],
        popup=popup_text,
        icon=folium.Icon(color=status_colors.get(row['Status'], 'gray'), icon='info-sign')
    ).add_to(m)

# Display map in dashboard
st_folium(m, width="100%", height=450)

# 3. INTERACTIVE CALENDAR TIMELINE VIEW
st.markdown("---")
st.subheader("📅 Schedule Overviews")

# Convert strings to datetime for timeline manipulation
df['Start Date'] = pd.to_datetime(df['Start Date'])
sorted_df = df.sort_values(by='Start Date')

# Create a clean timeline summary layout
for idx, row in sorted_df.iterrows():
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.info(f"📆 {row['Start Date'].strftime('%b %d, %Y')}")
    with col2:
        st.markdown(f"**{row['Project Name']}** ({row['Region']})")
    with col3:
        st.markdown(f"Status: `{row['Status']}` | Lead: *{row['Lead']}*")

# 4. RAW DATA VIEW (Clickable Ledger)
st.markdown("---")
st.subheader("🗂️ Project Registry Ledger")
st.write("Click any column header to sort, or hover over cells to expand details.")
st.dataframe(df, use_container_width=True)