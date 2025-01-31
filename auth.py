import streamlit as st
import pandas as pd
from utils import load_users, save_user_data, save_session, hash_password

# --- Authentication Functions ---
def login():
    from user_management import delete_user  # Move import here to avoid circular import
    st.subheader("Login")
    st.markdown("---")
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", use_container_width=True):
        if not username or not password:
            st.error("Please enter both username and password.")
            return
        
        users_df = load_users()
        user = users_df[users_df["Username"] == username]
        
        if not user.empty and user.iloc[0]["Password"] == hash_password(password):
            st.session_state["user"] = username
            save_session({'user': username})
            st.rerun()
        else:
            st.error("Invalid username or password.")

def logout():
    st.session_state["user"] = None
    st.rerun()

def signup():
    st.subheader("Create Account")
    st.markdown("---")
    
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
    
    if st.button("Create Account", use_container_width=True):
        users_df = load_users()
        if not username or not password or not confirm_password:
            st.error("All fields are required.")
        elif username in users_df["Username"].values:
            st.error("Username already exists. Please choose a different one.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters.")
        else:
            hashed_password = hash_password(password)
            new_user = pd.DataFrame({'Username': [username], 'Password': [hashed_password]})
            users_df = pd.concat([users_df, new_user], ignore_index=True)
            save_user_data(users_df)
            st.success("Account created successfully! You can now login.")
            st.session_state["user"] = username
            save_session({'user': username})
            st.rerun()