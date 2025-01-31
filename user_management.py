import streamlit as st
import pandas as pd
from utils import USERS_FILE, hash_password, load_users, save_data, save_user_data
import time
# --- User Management Functions ---

def delete_user(users_df):
    """Handles deleting a user."""
    st.subheader("Delete User")
    st.markdown("---")
    
    if not users_df.empty:
        users_df = users_df.copy().astype({'Username': str})
        users_df = users_df.sort_values('Username', ignore_index=True)

        non_admin_df = users_df[users_df['Username'] != 'admin'].copy()

        if not non_admin_df.empty:
            total_users = len(non_admin_df)
            st.metric("Total Users (excluding admin)", total_users)
            st.markdown("---")

            non_admin_df['FirstLetter'] = non_admin_df['Username'].str[0].str.upper().astype(str)
            letters = sorted(non_admin_df['FirstLetter'].unique())

            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input("Search users by username", key="delete_user_search")
            with col2:
                selected_letter = st.selectbox("Filter by letter", ["All"] + letters, key="delete_user_letter_filter")

            filtered_df = non_admin_df.copy()
            if search_term:
                mask = filtered_df['Username'].str.contains(search_term, case=False)
                filtered_df = filtered_df[mask]

            if selected_letter != "All":
                filtered_df = filtered_df[filtered_df['FirstLetter'] == selected_letter]

            if not filtered_df.empty:
                for idx, user in filtered_df.iterrows():
                    cols = st.columns([4, 1])
                    cols[0].write(user['Username'])

                    delete_key = f"delete_user_{user['Username']}_{idx}_1"
                    confirm_key = f"confirm_delete_user_{user['Username']}_{idx}_1"

                    if cols[1].button("Delete", key=delete_key, use_container_width=True):
                        if st.session_state.get(confirm_key, False):
                            try:
                                updated_df = users_df[users_df['Username'] != user['Username']]
                                save_data(updated_df, USERS_FILE)
                                
                                del st.session_state[confirm_key]
                                
                                st.success(f"✅ User **{user['Username']}** deleted successfully! 🗑️")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting user: {str(e)}")
                        else:
                            st.session_state[confirm_key] = True
                            st.warning(f"⚠️ Click again to confirm deletion of user **{user['Username']}**")
                    
                    st.markdown("---")
            else:
                st.info("🔍 No matching users found.")
        else:
            st.info("ℹ️ No non-admin users available to delete.")
    else:
        st.info("ℹ️ No users available to delete.")

def add_user(users_df):
    """Handles adding a new user (Admin function)."""
    st.subheader("Add New User")
    st.markdown("---")
    
    # Create a container to match delete user section style
    with st.container():
        username = st.text_input("Username", key="add_username")
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("Password", type="password", key="add_password")
        with col2:
            confirm_password = st.text_input("Confirm Password", type="password", key="add_confirm")
        
        if st.button("Add User", use_container_width=True):
            if not username or not password or not confirm_password:
                st.error("❌ All fields are required.")
            elif username in users_df["Username"].values:
                st.error("⚠️ Username already exists. Please choose a different one.")
            elif password != confirm_password:
                st.error("⚠️ Passwords do not match.")
            elif len(password) < 8:
                st.error("⚠️ Password must be at least 8 characters.")
            else:
                hashed_password = hash_password(password)
                new_user = pd.DataFrame({'Username': [username], 'Password': [hashed_password]}, index=[0])
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                save_user_data(users_df)
                
                st.success(f"✅ User **{username}** added successfully! 🎉")
                time.sleep(1)
                st.rerun()

                
def view_users(users_df):
                    """Displays users in a DataFrame with search and filter functionality."""
                    st.subheader("View Users")
                    st.markdown("---")
                    
                    if not users_df.empty:
                        # Create a copy and ensure proper data types
                        users_df = users_df.copy()
                        users_df = users_df.astype({'Username': str})
                        
                        # Sort users alphabetically by username
                        users_df = users_df.sort_values('Username', ignore_index=True)
                        
                        # Display total users metric
                        total_users = len(users_df)
                        st.metric("Total Users", total_users)
                        st.markdown("---")
                        
                        # Create filter options
                        users_df['FirstLetter'] = users_df['Username'].str[0].str.upper()
                        letters = sorted(users_df['FirstLetter'].unique())
                        
                        # Create two columns for search and filter
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            search_term = st.text_input("Search users by username", key="view_user_search")
                        
                        with col2:
                            selected_letter = st.selectbox(
                                "Filter by letter",
                                ["All"] + letters,
                                key="view_user_letter_filter"
                            )
                        
                        # Apply filters
                        filtered_df = users_df.copy()
                        
                        if search_term:
                            # Apply search filter
                            mask = filtered_df['Username'].str.contains(search_term, case=False)
                            filtered_df = filtered_df[mask]
                        
                        if selected_letter != "All":
                            # Apply letter filter
                            filtered_df = filtered_df[filtered_df['FirstLetter'] == selected_letter]
                        
                        # Display results
                        if not filtered_df.empty:
                            st.dataframe(
                                filtered_df[['Username']],
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Username": st.column_config.TextColumn("Username", width="medium")
                                }
                            )
                        else:
                            st.info("No matching users found.")
                    else:
                        st.info("No users found.")