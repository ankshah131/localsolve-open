"""
Configuration settings for the Wildfire Analysis Dashboard
"""

# Map Settings
MAP_SETTINGS = {
    'CENTER_LAT': 34.1,
    'CENTER_LON': -118.3,
    'DEFAULT_ZOOM': 11,
    'DEFAULT_PITCH': 45,
    'MAP_STYLE': "mapbox://styles/mapbox/satellite-v9"
}

# Color Schemes
COLORS = {
    'SEVERITY': {
        'High': '#d9534f',
        'Medium': '#f0ad4e',
        'Low': '#f7e08a'
    },
    'STATUS': {
        'At Risk': '#d9534f',
        'Affected': '#f0ad4e',
        'Safe': '#5cb85c'
    }
}

# Data Settings
DATA_SETTINGS = {
    'DATE_RANGE': {
        'start': '2024-01-20',
        'end': '2024-02-03'
    },
    'SAMPLE_SIZES': {
        'burn_severity': 300,
        'tree_species': 100,
        'infrastructure': 20
    }
}

# Infrastructure Types
INFRASTRUCTURE_TYPES = ['Hospital', 'School', 'Highway', 'Power Station']

# Tree Species
TREE_SPECIES = [
    'Coast Live Oak',
    'California Bay',
    'Monterey Pine',
    'Eucalyptus',
    'Western Sycamore'
]

# Invasive Species
INVASIVE_SPECIES = [
    {
        'name': 'Yellow Star Thistle',
        'risk_score': 9.5,
        'area_affected': 456
    },
    {
        'name': 'Pampas Grass',
        'risk_score': 8.7,
        'area_affected': 323
    },
    {
        'name': 'French Broom',
        'risk_score': 8.4,
        'area_affected': 234
    },
    {
        'name': 'Ice Plant',
        'risk_score': 7.2,
        'area_affected': 178
    },
    {
        'name': 'Tree of Heaven',
        'risk_score': 8.9,
        'area_affected': 289
    }
]