import streamlit as st
import pandas as pd
from auth import login, logout, signup
from contact_management import view_contacts
from user_management import delete_user, add_user
from dashboard import user_dashboard, admin_dashboard
from utils import load_data, save_data, load_session, save_session, load_users
import logging
import os
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the path to the contacts file
CONTACTS_FILE = os.path.join(os.path.dirname(__file__), 'contacts.csv')
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.csv')
# --- Main Application Function ---
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state['user'] = None

def main():
    """Main application function."""
    init_session_state()
    
    st.title("XRM BY JSON")
    st.markdown("---")
    
    # Load data only when needed
    df = None
    
    if not st.session_state.get("user"):
        st.subheader("Welcome! Please Login or Create an Account")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        with tab1:
            login()
        with tab2:
            signup()
    else:
        if st.session_state["user"] == "admin":
            admin_dashboard()
        else:
            df = load_data(CONTACTS_FILE)
            user_dashboard(df)

if __name__ == '__main__':
    main()
    debug = True