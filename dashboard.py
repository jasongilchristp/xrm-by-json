import logging
import numpy as np
import streamlit as st
from auth import logout
from contact_management import add_contact, delete_contact, view_contacts
from user_management import add_user, delete_user, view_users
from utils import CONTACTS_FILE, USERS_FILE, load_data, save_data

# --- Dashboard Functions ---
def user_dashboard(df):
    """User dashboard with contact management."""
    # Header with welcome message and logout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"Welcome, {st.session_state['user']}!")
    with col2:
        if st.button("Logout", key="user_logout_btn_1", use_container_width=True):
            logout()
    
    st.markdown("---")
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["View Contacts", "Add Contact", "Edit Contact"])
    
    with tab1:
        view_contacts(df)
    
    with tab2:
        add_contact(df)
    
    with tab3:
        # Edit Contact Section
        st.subheader("Edit Contact")
        st.markdown("---")
        
        if not df.empty:
            # Create a copy and ensure proper data types
            df = df.copy()
            df = df.astype({'Name': str, 'Email': str, 'Phone': str})
            
            logging.basicConfig(level=logging.INFO)
            logging.info(f"Data types in DataFrame: {df.dtypes}")
            logging.info(f"First few entries in 'Name' column: {df['Name'].head()}")
            
            # Sort contacts alphabetically by name
            df = df.sort_values('Name', ignore_index=True)
            
            # Display total contacts metric
            total_contacts = len(df)
            st.metric("Total Contacts", total_contacts)
            st.markdown("---")
            
            # Create filter options
            df['Name'] = df['Name'].fillna('').astype(str)
            df['FirstLetter'] = df['Name'].str[0].str.upper()
            df['FirstLetter'] = df['FirstLetter'].replace('', np.nan)
            
            letters = sorted(df['FirstLetter'].dropna().unique())
            
            # Create two columns for search and filter
            col1, col2 = st.columns([3, 1])
            
            with col1:
                search_term = st.text_input("Search contacts by name, email, or phone", key="user_edit_contact_search")
            
            with col2:
                selected_letter = st.selectbox(
                    "Filter by letter",
                    ["All"] + letters,
                    key="user_edit_contact_letter_filter"
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if search_term:
                # Apply search filter
                mask = filtered_df.apply(lambda x: x.astype(str).str.contains(search_term, case=False)).any(axis=1)
                filtered_df = filtered_df[mask]
            
            if selected_letter != "All":
                # Apply letter filter
                filtered_df = filtered_df[filtered_df['FirstLetter'] == selected_letter]
            
            # Display results with edit fields
            if not filtered_df.empty:
                for idx, contact in filtered_df.iterrows():
                    first_name = st.text_input("First Name", value=contact['First Name'], key=f"user_edit_first_name_{idx}")
                    middle_name = st.text_input("Middle Name", value=contact['Middle Name'], key=f"user_edit_middle_name_{idx}")
                    surname = st.text_input("Surname", value=contact['Surname'], key=f"user_edit_surname_{idx}")
                    email = st.text_input("Email", value=contact['Email'], key=f"user_edit_email_{idx}")
                    phone = st.text_input("Phone", value=contact['Phone'], key=f"user_edit_phone_{idx}")
                    if st.button("Save", key=f"user_edit_contact_save_{idx}_1", use_container_width=True):
                        try:
                            # Update contact using loc
                            df.loc[idx, 'First Name'] = first_name
                            df.loc[idx, 'Middle Name'] = middle_name
                            df.loc[idx, 'Surname'] = surname
                            df.loc[idx, 'Email'] = email
                            df.loc[idx, 'Phone'] = phone
                            save_data(df, CONTACTS_FILE)
                            full_name = f"{first_name} {middle_name} {surname}".strip()
                            st.success(f"Contact {full_name} updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating contact: {str(e)}")
                    
                    st.markdown("---")
            else:
                st.info("No matching contacts found.")
        else:
            st.info("No contacts available to edit.")

def admin_dashboard():
    """Admin dashboard with user and contact management."""
    # Header with welcome message and logout
    col1, col2 = st.columns([6, 1])
    with col1:
        st.subheader("Admin Dashboard")
        st.write("Welcome, Admin!")
    with col2:
        if st.button("Logout", key="admin_logout_btn", use_container_width=True):
            logout()
    
    st.markdown("---")

    # Create tabs for admin functionalities
    tabs = st.tabs(["User Management", "Contact Management"])
    
    with tabs[0]:
        st.subheader("User Management")
        st.markdown("---")
        
        # User metrics
        users_df = load_data(USERS_FILE)
        total_users = len(users_df)
        regular_users = len(users_df[users_df['Username'] != 'admin'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Regular Users", regular_users)
        with col3:
            st.metric("Admin Users", total_users - regular_users)
            
        st.markdown("---")
        
        # User management tabs
        user_tabs = st.tabs(["View Users","Add User", "Delete User"])
        with user_tabs[0]:
            view_users(users_df)
        with user_tabs[1]:
            add_user(users_df)
        with user_tabs[2]:
            delete_user(users_df)
    
    with tabs[1]:
        contacts_df = load_data(CONTACTS_FILE)
        st.subheader("Contact Management")
        st.markdown("---")
        
        # Create tabs for different functionalities
        contact_tabs = st.tabs(["View Contacts", "Add Contact", "Edit Contact", "Delete Contact"])
        
        with contact_tabs[0]:
            view_contacts(contacts_df)
        
        with contact_tabs[1]:
            add_contact(contacts_df)
        
        with contact_tabs[2]:
            # Edit Contact Section
            st.subheader("Edit Contact")
            st.markdown("---")
            
            if not contacts_df.empty:
                # Create a copy and ensure proper data types
                df = contacts_df.copy()
                df = df.astype({'First Name': str, 'Middle Name': str, 'Surname': str, 'Email': str, 'Phone': str})
                df['Name'] = (df['First Name'] + ' ' + df['Middle Name'] + ' ' + df['Surname']).str.strip()

                # Sort contacts alphabetically by name
                df = df.sort_values('Name', ignore_index=True)
                
                # Display total contacts metric
                total_contacts = len(df)
                st.metric("Total Contacts", total_contacts)
                st.markdown("---")
                
                # Create filter options
                df['Name'] = df['Name'].fillna('').astype(str)
                df['FirstLetter'] = df['Name'].str[0].str.upper()
                df['FirstLetter'] = df['FirstLetter'].replace('', np.nan)
                
                letters = sorted(df['FirstLetter'].dropna().unique())
                
                # Create two columns for search and filter
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    search_term = st.text_input("Search contacts by name, email, or phone", key="admin_edit_contact_search")
                
                with col2:
                    selected_letter = st.selectbox(
                        "Filter by letter",
                        ["All"] + letters,
                        key="admin_edit_contact_letter_filter"
                    )
                
                # Apply filters
                filtered_df = df.copy()
                
                if search_term:
                    # Apply search filter
                    mask = filtered_df.apply(lambda x: x.astype(str).str.contains(search_term, case=False)).any(axis=1)
                    filtered_df = filtered_df[mask]
                
                if selected_letter != "All":
                    # Apply letter filter
                    filtered_df = filtered_df[filtered_df['FirstLetter'] == selected_letter]
                
                # Display results with edit fields
                if not filtered_df.empty:
                    for idx, contact in filtered_df.iterrows():
                        first_name = st.text_input("First Name", value=contact['First Name'], key=f"admin_edit_first_name_{idx}")
                        middle_name = st.text_input("Middle Name", value=contact['Middle Name'], key=f"admin_edit_middle_name_{idx}")
                        surname = st.text_input("Surname", value=contact['Surname'], key=f"admin_edit_surname_{idx}")
                        email = st.text_input("Email", value=contact['Email'], key=f"admin_edit_email_{idx}")
                        phone = st.text_input("Phone", value=contact['Phone'], key=f"admin_edit_phone_{idx}")
                        if st.button("Save", key=f"admin_edit_contact_save_{idx}_1", use_container_width=True):
                            try:
                                # Update contact using loc
                                df.loc[idx, 'First Name'] = first_name
                                df.loc[idx, 'Middle Name'] = middle_name
                                df.loc[idx, 'Surname'] = surname
                                df.loc[idx, 'Email'] = email
                                df.loc[idx, 'Phone'] = phone
                                save_data(df, CONTACTS_FILE)
                                full_name = f"{first_name} {middle_name} {surname}".strip()
                                st.success(f"Contact {full_name} updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating contact: {str(e)}")
                        
                        st.markdown("---")
                else:
                    st.info("No matching contacts found.")
            else:
                st.info("No contacts available to edit.")
        
        with contact_tabs[3]:
            delete_contact(contacts_df)