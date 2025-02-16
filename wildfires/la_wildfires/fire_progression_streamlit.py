import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import io

# Google Cloud Storage URL (ensure it is publicly accessible or use signed URLs)
CSV_URL = "https://storage.googleapis.com/localsolve_assets/la_wildfires_jan_2025/filtered_la_january_2025_fire_hotspots_combined.csv"

# Function to fetch and load data
@st.cache_data
def load_data():
    response = requests.get(CSV_URL)
    if response.status_code == 200:
        csv_data = response.content  # Get binary content
        df = pd.read_csv(io.StringIO(csv_data.decode("utf-8")))  # Read into pandas
        df['acq_date'] = pd.to_datetime(df['acq_date'])  # Convert to datetime
        
        # Add acq_time as hour and minute to acq_date
        df['acq_datetime'] = df['acq_date'] + pd.to_timedelta(df['acq_time'].astype(str).str.zfill(4).str[:2] + ':' + df['acq_time'].astype(str).str.zfill(4).str[2:] + ':00')
        
        return df
    else:
        st.error("Failed to load data. Please check the file URL.")
        return pd.DataFrame()  # Return empty DataFrame if request fails

# Load dataset
df = load_data()

# Initialize session state for map settings if not already set
if 'map_center' not in st.session_state:
    st.session_state.map_center = {'lat': 34.0522, 'lon': -118.2437, 'zoom': 10}  # Default to LA center

# Streamlit App Title
st.title("LA January Fires Progression")

# Ensure data is loaded before proceeding
if not df.empty:
    # Select date range for filtering
    date_range = df['acq_date'].dt.date.unique()
    date_min = min(date_range)
    date_max = max(date_range)

    # Date selection slider
    date_selected = st.slider("Select Date", min_value=date_min, max_value=date_max, value=date_min, format="YYYY-MM-DD")

    # Filter dataset to include fires up to the selected date
    df_filtered = df[df['acq_date'].dt.date <= date_selected]

    # Display map with Plotly
    st.subheader(f"Fire Hotspots up to {date_selected}")
    fig = px.scatter_mapbox(
        df_filtered,
        lat="latitude",
        lon="longitude",
        color="brightness",
        hover_data=["acq_datetime", "confidence"],
        mapbox_style="carto-positron",
        zoom=st.session_state.map_center['zoom'],
        center={"lat": st.session_state.map_center['lat'], "lon": st.session_state.map_center['lon']}
    )
    
    # Capture zoom and center location changes using Plotly event handling
    if 'mapbox' in fig.layout:
        st.session_state.map_center['lat'] = fig.layout.mapbox.center.lat
        st.session_state.map_center['lon'] = fig.layout.mapbox.center.lon
        st.session_state.map_center['zoom'] = fig.layout.mapbox.zoom
    
    # Render map
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available to display.")
