import streamlit as st
from utils import check_instructor_credentials

def login():
    st.subheader("Instructor Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        instructor = check_instructor_credentials(email, password)
        if instructor:
            st.session_state['instructor'] = instructor
            st.success("Logged in as {}".format(instructor['first_name']))
            return True
        else:
            st.error("Invalid credentials")
            return False

    if st.button("Forgot Password"):
        st.info("Contact admin to reset your password.")
    return False

def logout():
    if st.button("Logout"):
        del st.session_state['instructor']
        st.success("Logged out")
