import streamlit as st 

from database import (
   create_database,
   create_user,
   authenticate_user
) 

from styles import apply_theme

from auth import (
    landing_page,
    login_page,
    register_page
)

from sidebar import sidebar

from dashboard import dashboard

from transactions import transactions_page
from analytics import analytics_page
from import_statement import import_page

from settings import settings_page


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MoneyLeak",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)


create_database()


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "landing"

if "user" not in st.session_state:
    st.session_state.user = None

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


# ============================================================
# THEME
# ============================================================

apply_theme()


# ============================================================
# ROUTER
# ============================================================

if st.session_state.user:

    sidebar()

    if st.session_state.page == "dashboard":

        dashboard()

    elif st.session_state.page == "transactions":

        transactions_page()

    elif st.session_state.page == "analytics":

        analytics_page()

    elif st.session_state.page == "import":

        import_page()

    elif st.session_state.page == "settings":

        settings_page()

    else:

        dashboard()

else:

    if st.session_state.page == "landing":

        landing_page()

    elif st.session_state.page == "login":

        login_page()

    elif st.session_state.page == "register":

        register_page()

    else:

        landing_page()
