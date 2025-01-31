import json
import pandas as pd
import streamlit as st
from utils import load_users, save_user_data, hash_password

# --- Authentication Functions ---
# Function to load session data from session.json
def load_session():
    try:
        with open("session.json", "r") as f:
            session_data = json.load(f)
        return session_data
    except FileNotFoundError:
        return {}  # Return an empty dict if session.json doesn't exist

# Function to save session data to session.json
def save_session(session_data):
    with open("session.json", "w") as f:
        json.dump(session_data, f)

# Load session on app start
session_data = load_session()
if "user" in session_data:
    st.session_state["user"] = session_data["user"]

# Login function
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
            # Update session data
            st.session_state["user"] = username
            save_session({'user': username})  # Save to session.json
            st.rerun()
        else:
            st.error("Invalid username or password.")

# Logout function
def logout():
    st.session_state["user"] = None
    save_session({'user': None})  # Clear session data in session.json
    st.rerun()

# Signup function
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

# Utility Functions for User Management (if needed)
def load_users():
    # This function loads users from a CSV or database
    try:
        users_df = pd.read_csv("users.csv")
    except FileNotFoundError:
        users_df = pd.DataFrame(columns=["Username", "Password"])
    return users_df

def save_user_data(users_df):
    # This function saves the user data to a CSV file
    users_df.to_csv("users.csv", index=False)

def hash_password(password):
    # This function hashes the password before saving it
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()
