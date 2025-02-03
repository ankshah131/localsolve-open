import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

class WildfireAnalysisDashboard:
    def __init__(self):
        st.set_page_config(layout="wide", page_title="LA Wildfire Analysis")
        self.load_data()
        self.setup_styling()

    def setup_styling(self):
        st.markdown("""
           <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f4f7fa; /* Soft background for readability */
        color: #333; /* Dark text for clarity */
    }
    .main {
        background-color: #ffffff; /* Clean white background */
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #d9534f; /* Red for urgency */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        transition: background-color 0.3s ease;
        padding: 12px 24px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #c9302c; /* Darker red on hover */
    }
    .stats-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        margin: 16px 0;
        border-left: 5px solid #d9534f; /* Red border for highlight */
    }
    .map-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    .severity-high { 
        color: #d9534f; /* Red for high severity */
        font-weight: bold;
    }
    .severity-medium { 
        color: #f0ad4e; /* Orange for medium severity */
        font-weight: bold;
    }
    .severity-low { 
        color: #f7e08a; /* Light yellow for low severity */
        font-weight: bold;
    }
    h1, h2, h3 {
        font-weight: 600;
        color: #d9534f; /* Unified red tone for titles */
    }
    h1 {
        font-size: 32px;
        margin-bottom: 12px;
    }
    h2 {
        font-size: 28px;
    }
    h3 {
        font-size: 22px;
    }
    .metric-card {
        text-align: center;
        background-color: #f9fafb; /* Light grayish-blue background */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-top: 16px;
    }
    .metric-card p {
        font-size: 16px;
        color: #666; /* Dark gray text for metric descriptions */
    }
    .metric-card h3 {
        font-size: 20px;
        font-weight: 600;
        color: #d9534f; /* Red for emphasis */
    }
</style>


        """, unsafe_allow_html=True)

    def load_data(self):
        self.dates = pd.date_range(start='2024-01-20', end='2024-02-03')
        self.burn_severity = pd.DataFrame({
            'severity': ['High', 'Medium', 'Low'] * 100,
            'latitude': np.random.uniform(34.0, 34.2, 300),
            'longitude': np.random.uniform(-118.4, -118.2, 300),
            'area_acres': np.random.uniform(10, 100, 300)
        })
        species_list = ['Coast Live Oak', 'California Bay', 'Monterey Pine', 'Eucalyptus', 'Western Sycamore']
        n_trees = 100
        self.tree_species = pd.DataFrame({
            'species': np.repeat(species_list, n_trees // len(species_list)),
            'latitude': np.random.uniform(34.0, 34.2, n_trees),
            'longitude': np.random.uniform(-118.4, -118.2, n_trees),
            'affected_by_severity': np.repeat(['High', 'Medium', 'Low'], n_trees // 3 + 1)[:n_trees]
        })
        n_infra = 20
        self.infrastructure = pd.DataFrame({
            'type': np.repeat(['Hospital', 'School', 'Highway', 'Power Station'], n_infra // 4),
            'latitude': np.random.uniform(34.0, 34.2, n_infra),
            'longitude': np.random.uniform(-118.4, -118.2, n_infra),
            'status': np.repeat(['At Risk', 'Safe', 'Affected'], n_infra // 3 + 1)[:n_infra]
        })

    def create_severity_analysis(self):
        col1, col2 = st.columns([3, 2])
        with col1:
            # Burn severity map
            severity_layer = pdk.Layer(
                "ScatterplotLayer",
                data=self.burn_severity,
                get_position=["longitude", "latitude"],
                get_radius="area_acres",
                get_fill_color=[
                    "severity == 'High' ? 215 : severity == 'Medium' ? 252 : 254",
                    "severity == 'High' ? 48 : severity == 'Medium' ? 141 : 224",
                    "severity == 'High' ? 39 : severity == 'Medium' ? 89 : 144",
                    180
                ],
                pickable=True
            )

            view_state = pdk.ViewState(
                latitude=34.1,
                longitude=-118.3,
                zoom=11,
                pitch=45
            )

            r = pdk.Deck(
                layers=[severity_layer],
                initial_view_state=view_state,
                tooltip={"text": "{severity} Severity: {area_acres:.1f} acres"},
                map_style="mapbox://styles/mapbox/satellite-v9"
            )

            st.pydeck_chart(r)

        with col2:
            st.markdown("### Severity Distribution")
            severity_stats = self.burn_severity.groupby('severity')['area_acres'].sum()
            fig = px.pie(
                values=severity_stats.values,
                names=severity_stats.index,
                color=severity_stats.index,
                color_discrete_map = {
                'High': '#d9534f',  
                'Medium': '#f0ad4e',   
                'Low': '#f7e08a'     

                },
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

    def create_vegetation_analysis(self):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Affected Tree Species by Severity")
            species_severity = pd.crosstab(self.tree_species['species'], self.tree_species['affected_by_severity'])
            fig = go.Figure(data=[
                go.Bar(name='High', x=species_severity.index, y=species_severity['High'], marker_color='#d9534f'),
                go.Bar(name='Medium', x=species_severity.index, y=species_severity['Medium'], marker_color='#f0ad4e'),
                go.Bar(name='Low', x=species_severity.index, y=species_severity['Low'], marker_color='#f7e08a')
            ])
            fig.update_layout(barmode='stack')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            
            st.subheader("Invasive Fire Hazard Species")
            
            invasive_data = pd.DataFrame({
                'Species': ['Yellow Star Thistle', 'Pampas Grass', 'French Broom', 'Ice Plant', 'Tree of Heaven'],
                'Risk_Score': [9.5, 8.7, 8.4, 7.2, 8.9],
                'Area_Affected': [456, 323, 234, 178, 289]
            })
            
            color_scale = ['#f7e08a', '#f0ad4e', '#d9534f']  # Red, Orange, and Yellow for severity
            
            fig = px.scatter(invasive_data, 
                             x='Risk_Score', 
                             y='Area_Affected', 
                             size='Area_Affected', 
                             text='Species', 
                             color='Risk_Score', 
                             color_continuous_scale=color_scale)
            
            st.plotly_chart(fig, use_container_width=True)


    def create_fire_progression(self):
        col1, col2 = st.columns([3, 2])
        with col1:
            selected_date = st.select_slider("Select Date", options=self.dates, format_func=lambda x: x.strftime('%Y-%m-%d'))
            st.write(f"Selected date: {selected_date}")
            view_state = pdk.ViewState(latitude=34.1, longitude=-118.3, zoom=11, pitch=45)
            layers = [
                pdk.Layer("ScatterplotLayer", data=self.infrastructure, get_position=["longitude", "latitude"],
                          get_radius=100, get_fill_color=[255, 0, 0, 100], pickable=True)
            ]
            r = pdk.Deck(layers=layers, initial_view_state=view_state, map_style="mapbox://styles/mapbox/satellite-v9", tooltip={"text": "{type}: {status}"})
            st.pydeck_chart(r)

        with col2:
            st.markdown("### Infrastructure Status")
            status_counts = self.infrastructure.groupby('status').size()
            fig = go.Figure(data=[go.Bar(x=status_counts.index, y=status_counts.values, marker_color=['#d9534f', '#f0ad4e', '#f7e08a'])])
            st.plotly_chart(fig, use_container_width=True)

    def run(self):

        
        st.title("LA Wildfire Impact App")


        st.markdown("""
        <div style='background-color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; color: #333;'>
        <p style='font-size: 14px; color: #444;'>
        LA Wildfire Impact App is a tool created by PlanetSampling LocalSolve Initiative for relief organisations, enabling them to prioritise response efforts and guide restoration plans. The app examines burn severity, vegetation damage, and infrastructure conditions, aiding in emergency response and recovery planning.
        </p>
        </div>
        """, unsafe_allow_html=True)

        # Key metrics with improved visual separation
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total Burned Area", f"{self.burn_severity['area_acres'].sum():,.0f} acres", "Critical", delta_color="inverse")
        with cols[1]:
            st.metric("Affected Trees", len(self.tree_species), "High Impact", delta_color="inverse")
        with cols[2]:
            st.metric("Infrastructure at Risk", len(self.infrastructure[self.infrastructure['status'] == 'At Risk']), "Urgent", delta_color="inverse")
        with cols[3]:
            st.metric("Active Fire Perimeters", "5", "Expanding", delta_color="inverse")

        # Create main analysis sections with tabs
        tab1, tab2, tab3 = st.tabs(["Burn Severity", "Vegetation Analysis", "Fire Progression & Infrastructure"])
        with tab1:
            self.create_severity_analysis()
        with tab2:
            self.create_vegetation_analysis()
        with tab3:
            self.create_fire_progression()

        st.markdown("""
        <div style='text-align: center; padding: 1rem; background-color: #f0f4f7; border-radius: 0.5rem; margin-top: 1rem;'>
            <p style='font-size: 14px; color: #444;'>
                This app was created as part of the PlanetSampling LocalSolve Initiative by a group of Data Scientists: 
                <br>
                <strong>Ankur Shah (USA)</strong>, 
                <strong>Keenan Eves (USA)</strong>, 
                <strong>Palak Agarwal (USA)</strong>, 
                <strong>Manuel A</strong>, 
                <strong>Kabir</strong>, 
                <strong>Aurelien Callens (FR)</strong>, 
                <strong>Vanesa Martin (USA)</strong>, 
                <strong>Magdalena Kortas (AU)</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True) #more members to be added here

if __name__ == "__main__":
    app = WildfireAnalysisDashboard()
    app.run()
