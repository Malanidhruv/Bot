import streamlit as st

def get_user_credentials():
    """Get user credentials from Streamlit input fields."""
    user_id = st.text_input("Enter User ID", value="", type="default")
    api_key = st.text_input("Enter API Key", value="", type="password")  # Hide API Key input
    return user_id, api_key

# Example usage
user_id, api_key = get_user_credentials()

if user_id and api_key:
    st.success("Credentials received!")
    st.write(f"User ID: {user_id}")
else:
    st.warning("Please enter your credentials.")
