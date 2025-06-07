# auth.py
import hashlib
import streamlit as st

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password, stored_hash):
    """Verify a stored password against one provided by user"""
    return hash_password(input_password) == stored_hash

def init_user_database():
    """Initialize the user database in session state"""
    if "users_db" not in st.session_state:
        st.session_state.users_db = {
            "admin": {
                "password_hash": hash_password("admin123"),
                "role": "admin",
                "email": "admin@chilimate.com"
            },
            "staff": {
                "password_hash": hash_password("staff123"),
                "role": "staff",
                "email": "staff@chilimate.com"
            }
        }

def authenticate_user(username, password):
    """Authenticate a user and return user data if successful"""
    if username in st.session_state.users_db:
        user_data = st.session_state.users_db[username]
        if verify_password(password, user_data["password_hash"]):
            return {
                "authenticated": True,
                "username": username,
                "role": user_data["role"],
                "email": user_data.get("email", "")
            }
    return {
        "authenticated": False,
        "username": None,
        "role": None,
        "email": None
    }

def register_user(username, password, email=None, role="customer"):
    """Register a new user"""
    if username in st.session_state.users_db:
        return False, "Username already exists"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    st.session_state.users_db[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "email": email
    }
    return True, "Registration successful"

def show_auth_form():
    """Display login/register tabs"""
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                auth_result = authenticate_user(username, password)
                if auth_result["authenticated"]:
                    st.session_state.auth = auth_result
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Username")
            new_email = st.text_input("Email (optional)")
            new_pass = st.text_input("Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Register"):
                if new_pass != confirm_pass:
                    st.error("Passwords don't match")
                else:
                    success, message = register_user(new_user, new_pass, new_email)
                    if success:
                        st.success(message + " Please login.")
                    else:
                        st.error(message)