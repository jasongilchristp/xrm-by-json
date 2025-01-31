CONTACTS_FILE = 'contacts.csv'
USERS_FILE = 'users.csv'

import os
import json
import pandas as pd
import hashlib

ADMIN_PASSWORD = "MMMGA45678"

# --- Utility Functions ---
def load_session():
    if os.path.exists("session.json"):
        try:
            with open("session.json", 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_session(session_data):
    with open("session.json", 'w') as f:
        json.dump(session_data, f)

def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    if file_path == "contacts.csv":
        return pd.DataFrame(columns=['ID', 'First Name', 'Middle Name', 'Surname', 'Email', 'Phone'])
    return pd.DataFrame(columns=['Username', 'Password'])

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    users_df = load_data("users.csv")
    if users_df.empty:
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
        users_df = pd.DataFrame({
            'Username': ['admin'],
            'Password': [hash_password(admin_password)]
        })
        save_data(users_df, "users.csv")
    return users_df

def save_user_data(users_df):
    save_data(users_df, "users.csv")

def generate_contact_id(name):
    prefix = name[0].upper()
    timestamp = pd.Timestamp.now().strftime('%Y%m%d%H%M%S')
    return f"{prefix}{timestamp}"