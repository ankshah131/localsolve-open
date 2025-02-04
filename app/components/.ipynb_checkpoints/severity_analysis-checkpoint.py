import streamlit as st
import pydeck as pdk
import plotly.express as px

class SeverityAnalysis:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def create_map(self):
        severity_layer = pdk.Layer(
            "ScatterplotLayer",
            data=self.data_loader.burn_severity,
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

        return pdk.Deck(
            layers=[severity_layer],
            initial_view_state=view_state,
            tooltip={"text": "{severity} Severity: {area_acres:.1f} acres"},
            map_style="mapbox://styles/mapbox/satellite-v9"
        )

    def create_distribution_chart(self):
        severity_stats = self.data_loader.burn_severity.groupby('severity')['area_acres'].sum()
        return px.pie(
            values=severity_stats.values,
            names=severity_stats.index,
            color=severity_stats.index,
            color_discrete_map={
                'High': '#d9534f',
                'Medium': '#f0ad4e',
                'Low': '#f7e08a'
            },
            hole=0.4
        )

    def display(self):
        col1, col2 = st.columns([3, 2])
        with col1:
            st.pydeck_chart(self.create_map())
        with col2:
            st.markdown("### Severity Distribution")
            st.plotly_chart(self.create_distribution_chart(), use_container_width=True)