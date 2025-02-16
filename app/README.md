# Streamlit App

This guide explains how to set up and run a Streamlit application on your local machine.

## Prerequisites

Before running the Streamlit app, ensure you have the following installed:

- **Python** (version 3.7 or later) - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package manager) - Comes pre-installed with Python
- **Streamlit** - Install using pip if not already installed

## Installation

1. **Clone the Repository** 

2. **Create and Activate a Virtual Environment (Recommended)**
   ```bash
   # Create virtual environment (Windows)
   python -m venv venv
   venv\Scripts\activate

   # Create virtual environment (Mac/Linux)
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   If there is no `requirements.txt` file, install Streamlit manually:
   ```bash
   pip install streamlit
   ```

## Running the Streamlit App

Execute the following command in the project directory:
```bash
streamlit run app.py
```

## Accessing the App

Once the command runs successfully, Streamlit will start a local server and provide a URL like:
```
http://localhost:8501/
```
Open this link in your web browser to access the app.

## Troubleshooting

- **Module Not Found:** Ensure dependencies are installed by running `pip install -r requirements.txt`.
- **Port Already in Use:** Change the port using:
  ```bash
  streamlit run app.py --server.port=8502
  ```
- **Virtual Environment Issues:** Ensure the virtual environment is activated before installing or running the app.

## Additional Resources
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python Virtual Environments](https://docs.python.org/3/library/venv.html)

