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

# --- 2. SIDEBAR CONTEXT & FILTERS ---
st.sidebar.header("📂 Case File: 62-HQ-83894")

# Short lead-in
st.sidebar.write("Declassified investigative records of **Unidentified Flying Objects** (1947–1968).")

# Expander 1: Verbatim Official Description
with st.sidebar.expander("Archive Details"):
    st.write(
        "The FBI's **62-HQ-83894** case file includes investigative records, "
        "eyewitness testimonies, and public reports concerning Unidentified Flying Objects "
        "and flying discs documented between **June 1947 and July 1968**."
    )
    st.write(
        "The records include high-profile incident accounts, photographic evidence "
        "from sites like **Oak Ridge, TN**, and technical proposals regarding potential "
        "propulsion systems. Additional topics include convention programs, researcher "
        "accounts, and extensive media coverage from the period."
    )
    st.markdown("---")
    st.caption(
        "**Note on Completeness:** This file is partially posted on the FBI Vault with "
        "more redactions and some pages missing. Included here is the **complete case file** "
        "with several newly declassified pages and only minor redactions."
    )

# Expander 2: The Discovery Note
with st.sidebar.expander("Discovery Note"):
    st.info(
        "🔍 **Supplemental Data:** While the official description catalogs through 1968, "
        "this AI-powered analysis identified supplemental reports from the early 1970s "
        "(up to **July 1974**) physically contained within the Section 10 folder."
    )

st.sidebar.divider()

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

            
            # --- THE ANOMALY NOTE ---
            # Check if the date string contains a year after 1968
            # This handles both strings and datetime objects gracefully
            if any(yr in str(date) for yr in ["1969", "1970", "1971", "1972", "1973", "1974"]):
                st.divider()
                st.caption(
                    "🔍 **Archival Note:** While official metadata catalogs this file through 1968, "
                    "this entry was identified as a supplemental record located within the Section 10 archive."
                )