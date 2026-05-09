import streamlit as st
import pydeck as pdk
import pandas as pd
import json
import os

# Page Config
st.set_page_config(layout="wide", page_title="Case 001: FBI File 62-HQ-83894 (Section 10)")
st.title("Case 001: FBI File 62-HQ-83894 (Section 10)")

# 1. Load Data
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "extracted_sightings.json")
    
    with open(file_path, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    
    # The Ultimate Coordinate Parser
    def parse_coords(coord):
        try:
            # THE FIX: If it's a dictionary like {"latitude": 34.0, "longitude": -106.8}
            if isinstance(coord, dict):
                lat = coord.get('latitude', coord.get('lat'))
                lon = coord.get('longitude', coord.get('lon'))
                if lat is not None and lon is not None:
                    return float(lat), float(lon)
                    
            # If it's a list: [34.0, -118.0]
            if isinstance(coord, list) and len(coord) >= 2:
                return float(coord[0]), float(coord[1])
                
            # If it's a string: "34.0, -118.0"
            if isinstance(coord, str):
                cleaned = coord.replace('[', '').replace(']', '').replace('"', '').replace("'", "")
                parts = cleaned.split(',')
                if len(parts) >= 2:
                    return float(parts[0].strip()), float(parts[1].strip())
        except Exception:
            pass
        return None, None
        
    if 'coordinates' in df.columns:
        df['lat'], df['lon'] = zip(*df['coordinates'].apply(parse_coords))
    else:
        df['lat'], df['lon'] = None, None
        
    return df

df = load_data()

# 2. Sidebar Filters
st.sidebar.header("Typology Filters")

shapes = df['craft_shape'].dropna().unique() if 'craft_shape' in df.columns else []
witnesses = df['witness_type'].dropna().unique() if 'witness_type' in df.columns else []

selected_shapes = st.sidebar.multiselect("Select Craft Shape:", options=shapes, default=shapes)
selected_witness = st.sidebar.multiselect("Select Witness Type:", options=witnesses, default=witnesses)

# --- NEW COMPACT PROVENANCE DISCLAIMER ---
st.sidebar.divider() # Adds a clean visual line to separate the filters from the note
st.sidebar.caption(
    "⚠️ **Data Provenance:** Extracted from FBI file `65_HS1-834228961_62-HQ-83894_Section_10` via AI. "
    "May contain inaccuracies due to faded 1960s typewriter text and handwritten margins. "
    "Always verify against the original source document."
)
# -----------------------------------------

# Apply Filters
if 'craft_shape' in df.columns and 'witness_type' in df.columns:
    filtered_df = df[(df['craft_shape'].isin(selected_shapes)) & (df['witness_type'].isin(selected_witness))]
else:
    filtered_df = df

map_df = filtered_df.dropna(subset=['lat', 'lon'])

# 3. Create Tabs
tab1, tab2 = st.tabs(["Geospatial Heatmap", "Witness vs. Bureaucracy"])

with tab1:
    st.subheader("Sighting Locations")
    if not map_df.empty:
        layer = pdk.Layer(
            "ScatterplotLayer",
            map_df,
            get_position="[lon, lat]",
            get_color="[200, 30, 0, 160]",
            get_radius=50000,
            pickable=True
        )
        
        view_state = pdk.ViewState(
            latitude=map_df['lat'].mean(),
            longitude=map_df['lon'].mean(),
            zoom=3,
            pitch=0
        )
        
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{location}"})
        st.pydeck_chart(r)
    else:
        st.warning("Still waiting for valid coordinates...")

with tab2:
    st.subheader("Accounts vs. Official Reports")
    for index, row in filtered_df.iterrows():
        loc = row.get('location', 'Unknown')
        date = row.get('date', 'Unknown')
        wit = row.get('witness_type', 'Unknown')
        with st.expander(f"{date} - {loc} ({wit})"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Witness Account:**")
                st.info(row.get('witness_quote_summary', 'No data provided.'))
            with col2:
                st.markdown("**FBI Response:**")
                st.warning(row.get('fbi_response_summary', 'No data provided.'))