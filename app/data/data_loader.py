import pandas as pd
import numpy as np
import requests
import io
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self):
        self.load_data()

    def load_data(self):
        """Load all required datasets"""
        # Load fire hotspot data
        self.load_fire_hotspots()
        
        # Load processed vegetation and tree data
        self.load_vegetation_data()
        
        # Load infrastructure data
        self.load_infrastructure()
        
        # Generate burn severity from fire hotspots
        self.generate_burn_severity()
        
        # Load/generate tree species data
        self.load_tree_species()
        
        # Set date range based on actual fire data
        if hasattr(self, 'fire_hotspots') and not self.fire_hotspots.empty:
            self.dates = pd.date_range(
                start=self.fire_hotspots['acq_date'].min(),
                end=self.fire_hotspots['acq_date'].max()
            )
        else:
            self.dates = pd.date_range(start='2024-01-20', end='2024-02-03')

    def load_fire_hotspots(self):
        """Load fire hotspot data from GCS"""
        CSV_URL = "https://storage.googleapis.com/localsolve_assets/la_wildfires_jan_2025/filtered_la_january_2025_fire_hotspots_combined.csv"
        
        try:
            response = requests.get(CSV_URL)
            if response.status_code == 200:
                csv_data = response.content
                self.fire_hotspots = pd.read_csv(io.StringIO(csv_data.decode("utf-8")))
                self.fire_hotspots['acq_date'] = pd.to_datetime(self.fire_hotspots['acq_date'])
                self.fire_hotspots['acq_datetime'] = self.fire_hotspots['acq_date'] + pd.to_timedelta(
                    self.fire_hotspots['acq_time'].astype(str).str.zfill(4).str[:2] + ':' + 
                    self.fire_hotspots['acq_time'].astype(str).str.zfill(4).str[2:] + ':00'
                )
            else:
                print(f"Failed to load fire hotspot data. Status code: {response.status_code}")
                self.fire_hotspots = pd.DataFrame()
        except Exception as e:
            print(f"Error loading fire hotspot data: {str(e)}")
            self.fire_hotspots = pd.DataFrame()

    def generate_burn_severity(self):
        """Generate burn severity data from fire hotspots"""
        if hasattr(self, 'fire_hotspots') and not self.fire_hotspots.empty:
            # Map brightness to severity levels
            brightness_ranges = {
                'High': (350, float('inf')),
                'Medium': (325, 350),
                'Low': (0, 325)
            }
            
            # Create severity column based on brightness
            severity = pd.cut(
                self.fire_hotspots['brightness'],
                bins=[-float('inf'), 325, 350, float('inf')],
                labels=['Low', 'Medium', 'High']
            )
            
            # Calculate approximate area from scan and track
            # This is a simplified calculation - adjust based on your needs
            area_acres = self.fire_hotspots['scan'] * self.fire_hotspots['track'] * 0.000247105  # Convert m² to acres
            
            self.burn_severity = pd.DataFrame({
                'severity': severity,
                'latitude': self.fire_hotspots['latitude'],
                'longitude': self.fire_hotspots['longitude'],
                'area_acres': area_acres,
                'date': self.fire_hotspots['acq_date']
            })
        else:
            # Fallback to mock data if no fire hotspots available
            self.burn_severity = pd.DataFrame({
                'severity': ['High', 'Medium', 'Low'] * 100,
                'latitude': np.random.uniform(34.0, 34.2, 300),
                'longitude': np.random.uniform(-118.4, -118.2, 300),
                'area_acres': np.random.uniform(10, 100, 300),
                'date': pd.date_range(start='2024-01-20', end='2024-02-03').repeat(100)[:300]
            })

    def load_vegetation_data(self):
        """Load vegetation and tree data from local files"""
        try:
            self.veg_processed = pd.read_csv('data/Vegeation_withburn_mode_processed.csv')
            self.trees_withburn = pd.read_csv("data/LATreeswithburn_new.csv")
            self.trees_processed = pd.read_csv("data/LATrees_processed.csv")
        except Exception as e:
            print(f"Error loading vegetation data: {str(e)}")
            self.veg_processed = pd.DataFrame()
            self.trees_withburn = pd.DataFrame()
            self.trees_processed = pd.DataFrame()

    def load_infrastructure(self):
        """Load infrastructure data"""
        n_infra = 20
        self.infrastructure = pd.DataFrame({
            'type': np.repeat(['Hospital', 'School', 'Highway', 'Power Station'], 
                            n_infra // 4),
            'latitude': np.random.uniform(34.0, 34.2, n_infra),
            'longitude': np.random.uniform(-118.4, -118.2, n_infra),
            'status': np.repeat(['At Risk', 'Safe', 'Affected'], 
                              n_infra // 3 + 1)[:n_infra]
        })

    def load_tree_species(self):
        """Load or generate tree species data"""
        species_list = ['Coast Live Oak', 'California Bay', 'Monterey Pine', 
                       'Eucalyptus', 'Western Sycamore']
        n_trees = 100
        self.tree_species = pd.DataFrame({
            'species': np.repeat(species_list, n_trees // len(species_list)),
            'latitude': np.random.uniform(34.0, 34.2, n_trees),
            'longitude': np.random.uniform(-118.4, -118.2, n_trees),
            'affected_by_severity': np.repeat(['High', 'Medium', 'Low'], 
                                            n_trees // 3 + 1)[:n_trees]
        })

    def get_fire_data_for_date(self, selected_date):
        """Get fire hotspot data up to a specific date"""
        if hasattr(self, 'fire_hotspots') and not self.fire_hotspots.empty:
            return self.fire_hotspots[self.fire_hotspots['acq_date'].dt.date <= selected_date]
        return pd.DataFrame()

    def get_burn_severity_for_date(self, selected_date):
        """Get burn severity data up to a specific date"""
        if hasattr(self, 'burn_severity') and not self.burn_severity.empty:
            return self.burn_severity[self.burn_severity['date'].dt.date <= selected_date]
        return pd.DataFrame()