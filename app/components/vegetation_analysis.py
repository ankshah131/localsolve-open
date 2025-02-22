
# components/vegetation_analysis.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

class VegetationAnalysis:
    def __init__(self, data_loader):
        self.data_loader = data_loader
        
    def create_vegetation_burn_severity_chart(self):
        # Get top 10 vegetation types by burn area
        veg_data = self.data_loader.veg_processed
        top10 = veg_data.sort_values(by='Total_Burnt_Area', ascending=False)[:10]
        burn_data = top10[['Class_Cnam', 'Area_of_Burn1', 'Area_of_Burn2', 
                          'Area_of_Burn3', 'Area_of_Burn4']]
        
        return go.Figure(data=[
            go.Bar(name='Low', x=burn_data['Class_Cnam'], 
                  y=burn_data['Area_of_Burn4'], marker_color='#000000'),
            go.Bar(name='Moderate-Low', x=burn_data['Class_Cnam'], 
                  y=burn_data['Area_of_Burn3'], marker_color='#8B4513'),
            go.Bar(name='Moderate-High', x=burn_data['Class_Cnam'], 
                  y=burn_data['Area_of_Burn2'], marker_color='#FFA500'),
            go.Bar(name='High', x=burn_data['Class_Cnam'], 
                  y=burn_data['Area_of_Burn1'], marker_color='#FFFF00')
        ]).update_layout(
            barmode='stack',
            xaxis_tickangle=-45,
            xaxis_title="Species that burned",
            yaxis_title="Area",
            height=500,
            showlegend=True,
            legend=dict(title='Burn Severity', yanchor="top", y=0.99, xanchor="right", x=0.99)
        )

    def create_tree_burn_severity_chart(self):
        trees_data = self.data_loader.trees_withburn
        severity_counts = trees_data.groupby(['sum', 'category'])['species'].count().reset_index()
        severity_counts = severity_counts.sort_values('species', ascending=False)
        
        severity_colors = {
            1: '#008000',  # green
            2: '#90EE90',  # lightgreen
            3: '#FFFF00',  # yellow
            4: '#FFA500',  # orange
            5: '#FF0000',  # red
            6: '#8B4513',  # brown
            7: '#000000'   # black
        }
        
        fig = go.Figure()
        for severity in sorted(severity_counts['sum'].unique()):
            mask = severity_counts['sum'] == severity
            fig.add_trace(go.Bar(
                x=severity_counts[mask]['category'],
                y=severity_counts[mask]['species'],
                name=f'Severity {severity}',
                marker_color=severity_colors[severity]
            ))
            
        fig.update_layout(
            barmode='group',
            xaxis_tickangle=-45,
            xaxis_title="Species that burned",
            yaxis_title="Number of trees",
            height=500,
            showlegend=True,
            legend=dict(title='Burn Severity', yanchor="top", y=0.99, xanchor="right", x=0.99)
        )
        return fig

    def create_tree_burn_comparison_chart(self):
        trees_processed = self.data_loader.trees_processed
        return px.scatter(
            trees_processed,
            x='Proportion of trees that burnt',
            y='Proportion of trees that burnt in the 1km buffer',
            size='Total number of trees',
            color='category',
            hover_data=['category', 'Total number of trees'],
            labels={
                'Proportion of trees that burnt': 'Proportion Burnt (Overall)',
                'Proportion of trees that burnt in the 1km buffer': 'Proportion Burnt (1km Buffer)',
                'category': 'Tree Category'
            }
        ).update_layout(
            height=500,
            showlegend=True,
            legend=dict(title='Tree Category', yanchor="top", y=0.99, xanchor="right", x=0.99)
        )

    def display(self):
        st.header("Vegetation Burn Analysis")
        
        st.subheader("Burn Severity by Vegetation Type")
        st.plotly_chart(
            self.create_vegetation_burn_severity_chart(), 
            use_container_width=True
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Tree Burn Severity by Category")
            st.plotly_chart(
                self.create_tree_burn_severity_chart(),
                use_container_width=True
            )
            
        with col2:
            st.subheader("Tree Burn Proportion Comparison")
            st.plotly_chart(
                self.create_tree_burn_comparison_chart(),
                use_container_width=True
            )
