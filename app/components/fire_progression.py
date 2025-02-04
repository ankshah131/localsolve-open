import streamlit as st
import pydeck as pdk
import plotly.graph_objects as go

class FireProgression:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def create_map(self, selected_date):
        view_state = pdk.ViewState(
            latitude=34.1,
            longitude=-118.3,
            zoom=11,
            pitch=45
        )

        # Create infrastructure layer
        infrastructure_layer = pdk.Layer(
            "ScatterplotLayer",
            data=self.data_loader.infrastructure,
            get_position=["longitude", "latitude"],
            get_radius=100,
            get_fill_color=[
                "status == 'At Risk' ? 215 : status == 'Affected' ? 240 : 120",
                "status == 'At Risk' ? 48 : status == 'Affected' ? 173 : 190",
                "status == 'At Risk' ? 39 : status == 'Affected' ? 78 : 120",
                180
            ],
            pickable=True
        )

        return pdk.Deck(
            layers=[infrastructure_layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/satellite-v9",
            tooltip={"text": "{type}: {status}"}
        )

    def create_infrastructure_chart(self):
        status_counts = self.data_loader.infrastructure.groupby('status').size()
        
        return go.Figure(data=[
            go.Bar(
                x=status_counts.index,
                y=status_counts.values,
                marker_color=['#d9534f', '#f0ad4e', '#f7e08a']
            )
        ]).update_layout(
            title="Infrastructure Status Distribution",
            xaxis_title="Status",
            yaxis_title="Count",
            showlegend=False
        )

    def display(self):
        col1, col2 = st.columns([3, 2])
        
        with col1:
            selected_date = st.select_slider(
                "Select Date",
                options=self.data_loader.dates,
                format_func=lambda x: x.strftime('%Y-%m-%d')
            )
            st.write(f"Selected date: {selected_date}")
            st.pydeck_chart(self.create_map(selected_date))

        with col2:
            st.markdown("### Infrastructure Status")
            st.plotly_chart(
                self.create_infrastructure_chart(),
                use_container_width=True
            )