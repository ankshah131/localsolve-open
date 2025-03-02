import streamlit as st
from data.data_loader import DataLoader
from utils.styling import setup_styling
from components.severity_analysis import SeverityAnalysis
from components.vegetation_analysis import VegetationAnalysis
from components.fire_progression import FireDataLoader, FireProgression
from components.veg_burn import VegBurn
from components.invasive_species import InvasivesMap 


class WildfireAnalysisDashboard:
    def __init__(self):
        st.set_page_config(layout="wide", page_title="LA Wildfire Analysis")
        self.data_loader = DataLoader()
        self.fire_data_loader = FireDataLoader()
        setup_styling()
        
        # Initialize components
        self.severity_analysis = SeverityAnalysis(self.data_loader)
        self.vegetation_analysis = VegetationAnalysis(self.data_loader)
        self.fire_progression = FireProgression(self.fire_data_loader)
        self.veg_burn = VegBurn()
        self.invasive_species = InvasivesMap()

    def display_header(self):
        st.title("LA Wildfire Impact App")
        st.markdown("""
        <div style='background-color: white; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; color: #333;'>
        <p style='font-size: 14px; color: #444;'>
        LA Wildfire Impact App is a tool created by PlanetSapling's LocalSolve Initiative for ecological restoration organisations, enabling them to prioritise response efforts and guide restoration plans. The app examines burn severity, vegetation damage, and infrastructure conditions, aiding in long term response and recovery planning.
        </p>
        </div>
        """, unsafe_allow_html=True)

    def display_metrics(self):
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total Burned Area", 
                     f"{self.data_loader.burn_severity['area_acres'].sum():,.0f} acres", 
                     "Critical", delta_color="inverse")
        with cols[1]:
            st.metric("Affected Trees", 
                     len(self.data_loader.tree_species), 
                     "High Impact", delta_color="inverse")
        with cols[2]:
            at_risk = len(self.data_loader.infrastructure[
                self.data_loader.infrastructure['status'] == 'At Risk'])
            st.metric("Infrastructure at Risk", 
                     at_risk, 
                     "Urgent", delta_color="inverse")
        with cols[3]:
            st.metric("Active Fire Perimeters", 
                     "5", 
                     "Expanding", delta_color="inverse")

    def display_footer(self):
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background-color: #f0f4f7; border-radius: 0.5rem; margin-top: 1rem;'>
            <p style='font-size: 14px; color: #444;'>
                This app was created as part of the PlanetSapling LocalSolve Initiative by a group of Data Scientists: 
                <br>
                <strong>Ankur Shah (USA)</strong>, 
                <strong>Magdalena Kortas (AU)</strong>,
                <strong>Keenan Eves (USA)</strong>, 
                <strong>Palak Agarwal (USA)</strong>, 
                <strong>Manuel Alafaa (NGA)</strong>,
                <strong>Aurelien Callens (FRA)</strong>,
                <strong>Kabir Ahamad (CAN)</strong>
                <strong>Vanesa Martin (USA)</strong>.
            </p>

            <p style='font-size: 14px; color: #444; margin-top: 10px;'>
                Contact <strong>PlanetSapling</strong> to request the vegetation and urban tree species data files at 
                <strong>contact(at)planetsapling.com</strong>.
            </p>            
        </div>
        """, unsafe_allow_html=True)

    def run(self):
        self.display_header()
        #self.display_metrics()

        tab1, tab2, tab3, tab4 = st.tabs([
            "Burn Severity", 
            "Vegetation Analysis", 
            "Invasive Species",
            "Fire Progression & Infrastructure"
        ])
        
        with tab1:
            self.severity_analysis.display()
        with tab2:
            self.veg_burn.display()
            self.vegetation_analysis.display()
        with tab3:
            self.invasive_species.display()
        with tab4:
            self.fire_progression.display()


        self.display_footer()

if __name__ == "__main__":
    app = WildfireAnalysisDashboard()
    app.run()
