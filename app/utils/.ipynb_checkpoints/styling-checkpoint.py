import streamlit as st

def setup_styling():
    st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f4f7fa;
        color: #333;
    }
    .main {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #d9534f;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        transition: background-color 0.3s ease;
        padding: 12px 24px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #c9302c;
    }
    .stats-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
        margin: 16px 0;
        border-left: 5px solid #d9534f;
    }
    .map-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    .severity-high { color: #d9534f; font-weight: bold; }
    .severity-medium { color: #f0ad4e; font-weight: bold; }
    .severity-low { color: #f7e08a; font-weight: bold; }
    h1, h2, h3 { font-weight: 600; color: #d9534f; }
    h1 { font-size: 32px; margin-bottom: 12px; }
    h2 { font-size: 28px; }
    h3 { font-size: 22px; }
    .metric-card {
        text-align: center;
        background-color: #f9fafb;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-top: 16px;
    }
    .metric-card p {
        font-size: 16px;
        color: #666;
    }
    .metric-card h3 {
        font-size: 20px;
        font-weight: 600;
        color: #d9534f;
    }
    </style>
    """, unsafe_allow_html=True)