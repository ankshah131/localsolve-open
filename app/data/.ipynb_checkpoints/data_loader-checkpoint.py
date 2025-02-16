
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self):
        self.load_data()

    def load_data(self):
        self.dates = pd.date_range(start='2024-01-20', end='2024-02-03')
        self.load_burn_severity()
        self.load_tree_species()
        self.load_infrastructure()
        self.veg_processed = pd.read_csv('data/Vegeation_withburn_mode_processed.csv')
        self.trees_withburn = pd.read_csv("data/LATreeswithburn_new.csv")
        self.trees_processed = pd.read_csv("data/LATrees_processed.csv")
    
    def load_burn_severity(self):
        self.burn_severity = pd.DataFrame({
            'severity': ['High', 'Medium', 'Low'] * 100,
            'latitude': np.random.uniform(34.0, 34.2, 300),
            'longitude': np.random.uniform(-118.4, -118.2, 300),
            'area_acres': np.random.uniform(10, 100, 300)
        })

    def load_tree_species(self):
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

    def load_infrastructure(self):
        n_infra = 20
        self.infrastructure = pd.DataFrame({
            'type': np.repeat(['Hospital', 'School', 'Highway', 'Power Station'], 
                            n_infra // 4),
            'latitude': np.random.uniform(34.0, 34.2, n_infra),
            'longitude': np.random.uniform(-118.4, -118.2, n_infra),
            'status': np.repeat(['At Risk', 'Safe', 'Affected'], 
                              n_infra // 3 + 1)[:n_infra]
        })

