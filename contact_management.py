import streamlit as st
import pandas as pd
import numpy as np
from utils import generate_contact_id, save_data, CONTACTS_FILE
import logging # For debugging
import time 

# --- Contact Management Functions ---
def view_contacts(df):
    """Displays contacts in a DataFrame with search and filter functionality."""
    st.subheader("View Contacts")
    st.markdown("---")
    
    if not df.empty:
        # Create a copy and ensure proper data types
        df = df.copy()
        df = df.astype({'First Name': str, 'Middle Name': str, 'Surname': str, 'Email': str, 'Phone': str})
        
        # Sort contacts alphabetically by name
        df = df.sort_values(['First Name', 'Middle Name', 'Surname'], ignore_index=True)
        
        # Display total contacts metric
        total_contacts = len(df)
        st.metric("Total Contacts", total_contacts)
        st.markdown("---")
        
        # Create Full Name column for display
        df['Full Name'] = df[['First Name', 'Middle Name', 'Surname']].fillna('').agg(' '.join, axis=1).str.strip()
        
        # Handle any NaN or empty space issues in Full Name column
        df['Full Name'] = df['Full Name'].replace('', 'No Name')  # Set default value for empty names
        
        # Generate FirstLetter column for filter
        df['FirstLetter'] = df['First Name'].str[0].str.upper()  # Extract first letter from First Name
        df['FirstLetter'] = df['FirstLetter'].replace('', np.nan)  # Replace empty strings with NaN
        df['FirstLetter'] = df['FirstLetter'].astype(pd.StringDtype())  # Ensure proper string dtype
        
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Data types in DataFrame: {df.dtypes}")
        logging.info(f"First few entries in 'Name' column: {df['Full Name'].head()}")
        
        letters = sorted(df['FirstLetter'].dropna().unique())
        
        # Create two columns for search and filter
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input("Search contacts by name, email, or phone", key="contact_search")
        
        with col2:
            selected_letter = st.selectbox(
                "Filter by letter",
                ["All"] + letters,
                key="contact_letter_filter"
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
        
        # Display results
        if not filtered_df.empty:
            st.dataframe(
                filtered_df[['Full Name', 'Email', 'Phone']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Full Name": st.column_config.TextColumn("Full Name", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="medium"),
                    "Phone": st.column_config.TextColumn("Phone", width="small")
                }
            )
        else:
            st.info("No matching contacts found.")
    else:
        st.info("No contacts found. Add your first contact below.")

# --- Add Contact Function ---
def add_contact(df):
    """Add a new contact."""
    st.subheader("Add Contact")
    st.markdown("---")
    
    # Create fields for contact information
    first_name = st.text_input("First Name", key="add_first_name")
    middle_name = st.text_input("Middle Name", key="add_middle_name")
    surname = st.text_input("Surname", key="add_surname")
    email = st.text_input("Email", key="add_email")
    phone = st.text_input("Phone", key="add_phone")
    
    if st.button("Save", use_container_width=True):
        # Validation: Check if all fields are filled
        if not first_name or not middle_name or not surname or not email or not phone:
            st.error("Please fill in all the fields! First Name, Middle Name, Surname, Email, and Phone are required.")
            return
        
        # Add contact to the DataFrame
        new_contact = pd.DataFrame({
            'First Name': [first_name],
            'Middle Name': [middle_name],
            'Surname': [surname],
            'Email': [email],
            'Phone': [phone]
        })
        
        df = pd.concat([df, new_contact], ignore_index=True)
        save_data(df, "contacts.csv")
        st.success(f"✅ Contact for {first_name} {middle_name} {surname} added successfully!")
        st.balloons()  # 🎈 Fun visual effect for user addition
        time.sleep(1)  # Short delay for visibility 
        st.rerun()  


# --- Edit Contact Function ---
def edit_contact(df):
    """Edit an existing contact."""
    st.subheader("Edit Contact")
    st.markdown("---")

    # Ensure session state stores contacts
    if "contacts_df" not in st.session_state:
        st.session_state.contacts_df = df.copy()

    df = st.session_state.contacts_df

    if not df.empty:
        df = df.astype({'First Name': str, 'Middle Name': str, 'Surname': str, 'Email': str, 'Phone': str})
        
        # Sort contacts alphabetically
        df = df.sort_values(['First Name', 'Middle Name', 'Surname'], ignore_index=True)

        # Display total contacts
        st.metric("Total Contacts", len(df))
        st.markdown("---")

        # Create 'Full Name' for display
        df['Full Name'] = df[['First Name', 'Middle Name', 'Surname']].fillna('').agg(' '.join, axis=1).str.strip()
        df['FirstLetter'] = df['First Name'].str[0].str.upper()
        df['FirstLetter'] = df['FirstLetter'].replace('', np.nan)
        df['FirstLetter'] = df['FirstLetter'].astype(pd.StringDtype())

        letters = sorted(df['FirstLetter'].dropna().unique())

        # Search and Filter Controls
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("Search contacts by name, email, or phone", key="edit_contact_search")
        with col2:
            selected_letter = st.selectbox("Filter by letter", ["All"] + letters, key="edit_contact_letter_filter")

        # Apply search & filter
        filtered_df = df.copy()
        if search_term:
            mask = filtered_df.apply(lambda x: x.astype(str).str.contains(search_term, case=False)).any(axis=1)
            filtered_df = filtered_df[mask]

        if selected_letter != "All":
            filtered_df = filtered_df[filtered_df['FirstLetter'] == selected_letter]

        # Display editable fields
        if not filtered_df.empty:
            for idx, contact in filtered_df.iterrows():
                first_name = st.text_input("First Name", value=contact['First Name'], key=f"edit_first_name_{idx}")
                middle_name = st.text_input("Middle Name", value=contact['Middle Name'], key=f"edit_middle_name_{idx}")
                surname = st.text_input("Surname", value=contact['Surname'], key=f"edit_surname_{idx}")
                email = st.text_input("Email", value=contact['Email'], key=f"edit_email_{idx}")
                phone = st.text_input("Phone", value=contact['Phone'], key=f"edit_phone_{idx}")

                if st.button("Save", key=f"edit_contact_save_{idx}_1", use_container_width=True):
                    # Validate inputs
                    if not all([first_name, middle_name, surname, email, phone]):
                        st.error("All fields are required! Please fill them in.")
                        return

                    # Update contact in session state
                    st.session_state.contacts_df.loc[idx, 'First Name'] = first_name
                    st.session_state.contacts_df.loc[idx, 'Middle Name'] = middle_name
                    st.session_state.contacts_df.loc[idx, 'Surname'] = surname
                    st.session_state.contacts_df.loc[idx, 'Email'] = email
                    st.session_state.contacts_df.loc[idx, 'Phone'] = phone

                    save_data(st.session_state.contacts_df, "contacts.csv")
                    st.success(f"✅ Contact {first_name} {middle_name} {surname} updated successfully!")
                    st.snow()
                    time.sleep(1)  
                    st.rerun()

                st.markdown("---")
        else:
            st.info("No matching contacts found.")
    else:
        st.info("No contacts available to edit.")

def delete_contact(df):
    """Delete an existing contact."""
    st.subheader("Delete Contact")
    st.markdown("---")

    if not df.empty:
        # Create a copy and ensure proper data types
        df = df.copy()
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
            search_term = st.text_input("Search contacts by name, email, or phone", key="delete_contact_search")
        
        with col2:
            selected_letter = st.selectbox(
                "Filter by letter",
                ["All"] + letters,
                key="delete_contact_letter_filter"
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
        
        # Display results with delete buttons
        if not filtered_df.empty:
            for idx, contact in filtered_df.iterrows():
                cols = st.columns([4, 1])
                cols[0].write(contact['Name'])
                
                delete_key = f"delete_contact_{contact['Name']}_{idx}_1"
                confirm_key = f"confirm_delete_contact_{contact['Name']}_{idx}_1"
                
                if cols[1].button("Delete", key=delete_key, use_container_width=True):
                    if st.session_state.get(confirm_key, False):
                        try:
                            # Remove the contact from DataFrame
                            updated_df = df[df['Name'] != contact['Name']]
                            # Save the changes
                            save_data(updated_df, CONTACTS_FILE)
                            # Clear confirmation state
                            if confirm_key in st.session_state:
                                del st.session_state[confirm_key]
                            st.success(f"✅ Contact {contact['Name']} deleted successfully!")
                            time.sleep(1)  # Short delay for visibility 
                            st.rerun()  



                        except Exception as e:
                            st.error(f"Error deleting contact: {str(e)}")
                    else:
                        st.session_state[confirm_key] = True
                        st.warning(f"Click again to confirm deletion of contact {contact['Name']}")
                
                st.markdown("---")
        else:
            st.info("No matching contacts found.")
    else:
        st.info("No contacts available to delete.")