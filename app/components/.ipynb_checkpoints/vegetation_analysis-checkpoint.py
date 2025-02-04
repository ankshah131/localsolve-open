import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class VegetationAnalysis:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def create_species_severity_chart(self):
        species_severity = pd.crosstab(
            self.data_loader.tree_species['species'],
            self.data_loader.tree_species['affected_by_severity']
        )
        
        return go.Figure(data=[
            go.Bar(name='High', x=species_severity.index, 
                  y=species_severity['High'], marker_color='#d9534f'),
            go.Bar(name='Medium', x=species_severity.index, 
                  y=species_severity['Medium'], marker_color='#f0ad4e'),
            go.Bar(name='Low', x=species_severity.index, 
                  y=species_severity['Low'], marker_color='#f7e08a')
        ]).update_layout(barmode='stack')

    def create_invasive_species_chart(self):
        invasive_data = pd.DataFrame({
            'Species': ['Yellow Star Thistle', 'Pampas Grass', 'French Broom', 
                       'Ice Plant', 'Tree of Heaven'],
            'Risk_Score': [9.5, 8.7, 8.4, 7.2, 8.9],
            'Area_Affected': [456, 323, 234, 178, 289]
        })
        
        return px.scatter(
            invasive_data,
            x='Risk_Score',
            y='Area_Affected',
            size='Area_Affected',
            text='Species',
            color='Risk_Score',
            color_continuous_scale=['#f7e08a', '#f0ad4e', '#d9534f']
        )

    def display(self):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("Affected Tree Species by Severity")
            st.plotly_chart(self.create_species_severity_chart(), 
                          use_container_width=True)

        with col2:
            st.subheader("Invasive Fire Hazard Species")
            st.plotly_chart(self.create_invasive_species_chart(), 
                          use_container_width=True)