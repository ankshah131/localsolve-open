import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import io

# Data Loader Class
class FireDataLoader:
    def __init__(self):
        self.df = pd.DataFrame()  # Initialize to avoid NoneType errors
        self.infrastructure = None  # Placeholder if infrastructure data is needed

    def load_data(self):
        CSV_URL = "https://storage.googleapis.com/localsolve_assets/la_wildfires_jan_2025/filtered_la_january_2025_fire_hotspots_combined.csv"
        response = requests.get(CSV_URL)
        if response.status_code == 200:
            csv_data = response.content
            df = pd.read_csv(io.StringIO(csv_data.decode("utf-8")))
            df['acq_date'] = pd.to_datetime(df['acq_date'])
            df['acq_datetime'] = df['acq_date'] + pd.to_timedelta(
                df['acq_time'].astype(str).str.zfill(4).str[:2] + ':' + 
                df['acq_time'].astype(str).str.zfill(4).str[2:] + ':00'
            )
            self.df = df  # Assign df correctly
        else:
            st.error("Failed to load data. Please check the file URL.")


# Fire Progression Class
class FireProgression:
    def __init__(self, data_loader):
        self.data_loader = data_loader
        
        # Ensure session state for map settings #34.0486, -118.526
        if 'map_center' not in st.session_state:
            st.session_state.map_center = {'lat': 34.0486, 'lon': -118.5267, 'zoom': 12}



    def create_map(self, df_filtered):
        fig = px.scatter_mapbox(
            df_filtered,
            lat="latitude",
            lon="longitude",
            color="brightness",
            hover_data=["acq_datetime", "confidence"],
            mapbox_style="carto-positron",
            zoom=st.session_state.map_center['zoom'],
            center={"lat": st.session_state.map_center['lat'], "lon": st.session_state.map_center['lon']},
            color_continuous_scale=["black", "red"]  # Adjust this line for the red-black color scale
        )
        
        # Save the map state (center and zoom) to session state on map creation
        if 'mapbox' in fig.layout:
            if fig.layout.mapbox.center:
                st.session_state.map_center['lat'] = fig.layout.mapbox.center.lat
                st.session_state.map_center['lon'] = fig.layout.mapbox.center.lon
                st.session_state.map_center['zoom'] = fig.layout.mapbox.zoom
    
        return fig


    def create_infrastructure_chart(self):
        if self.data_loader.infrastructure is not None:
            status_counts = self.data_loader.infrastructure.groupby('status').size()
            return go.Figure(data=[
                go.Bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    marker_color=['#d73027', '#f0ad4e', '#78c679']
                )
            ]).update_layout(
                title="Infrastructure Status Distribution",
                xaxis_title="Status",
                yaxis_title="Count",
                showlegend=False
            )
        return None

    def display(self):
        st.title("LA January Fires Progression")
    
        # Ensure data is loaded before accessing it
        if self.data_loader.df.empty:
            self.data_loader.load_data()
    
        df = self.data_loader.df  # Now safe to use
    
        if not df.empty:

            col1, col2 = st.columns([3, 2])

            with col1:
                # Get date range
                date_range = df['acq_date'].dt.date.unique()
                date_min = min(date_range)
                date_max = max(date_range)

                # Date selection slider
                selected_date = st.slider("Select Date", min_value=date_min, max_value=date_max, value=date_min, format="YYYY-MM-DD")

                # Filter dataset
                df_filtered = df[df['acq_date'].dt.date <= selected_date]

                # Create and display map
                fig = self.create_map(df_filtered)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("### Infrastructure Status")
                infra_chart = self.create_infrastructure_chart()
                if infra_chart:
                    st.plotly_chart(infra_chart, use_container_width=True)
        else:
            st.warning("No data available to display.")

# Run Streamlit App
if __name__ == "__main__":
    data_loader = FireDataLoader()
    app = FireProgression(data_loader)
    app.display() 