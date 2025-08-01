import streamlit as st
from dotenv import load_dotenv
import logging
import warnings
from utils import get_config, initialize_session_state_with_token, reset_conversation_state
from client_utils import get_supabase_client
from supabase import AuthApiError

# --- Initial Setup ---

# Suppress specific DeprecationWarning from pydantic v1 typing
# Reason: Avoids cluttering the console with warnings from dependencies like mem0.
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.v1.typing")

# Configure logging
# Reason: Provides visibility into the application's execution flow and potential issues during development/debugging.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Streamlit Page Config (MUST be the first Streamlit command) ---
# Reason: Sets basic page properties like title and layout. Must be called before other st commands.
st.set_page_config(page_title="mem0 Demo Chat", layout="wide")

# --- Configuration Loading ---
# Load environment variables from .env file
load_dotenv()
logging.info("App: Loaded environment variables.")
config = get_config(logging)

# Load the clients (cached resources)
try:
    supabase_client = get_supabase_client(config)
except Exception as e:
    logging.error(f"App: Failed to initialize Supabase client: {e}", exc_info=True)
    st.error(f"Failed to initialize Supabase client: {e}")    
    st.stop() # Stop execution if clients fail to initialize
    
initialize_session_state_with_token(st)

# --- Authentication Logic ---

# Initialize session state for user session if it doesn't exist
if 'user_session' not in st.session_state:
    st.session_state.user_session = None
    logging.info("App: Initialized user_session in session state.")

@st.fragment
def show_login_form():
    """
    Displays the login/signup form and handles authentication logic.
    """

    st.title("Login / Sign Up")
    st.caption("Please log in to access the chat functionality.")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login")
        with col2:
            signup_button = st.form_submit_button("Sign Up")

        if login_button:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    logging.info(f"App: Attempting login for user: {email}")
                    # Call Supabase Auth to sign the user in.
                    session = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user_session = session # Store session info
                    logging.info(f"App: Login successful for user: {email}")
                    st.success("Login successful!")
                    st.rerun() # Rerun to show the main app
                except AuthApiError as e:
                    logging.error(f"App: Login failed for {email}: {e.message}")
                    st.error(f"Login failed: {e.message}")
                except Exception as e:
                    logging.error(f"App: An unexpected error occurred during login: {e}", exc_info=True)
                    st.error("An unexpected error occurred during login.")

        if signup_button:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    logging.info(f"App: Attempting signup for user: {email}")
                    # Reason: Calls Supabase Auth to sign the user up.
                    session = supabase_client.auth.sign_up({"email": email, "password": password})
                    # Note: Supabase often requires email confirmation by default.
                    # The session returned here might not be fully active until confirmation.
                    # st.session_state.user_session = session # Optionally log in immediately, or wait for confirmation
                    logging.info(f"App: Signup successful for user: {email}. Session: {session}")
                    st.success("Sign up successful! Please check your email for a confirmation link if required by your Supabase settings.")
                    # Don't rerun automatically on signup, let user log in after confirming.
                except AuthApiError as e:
                    logging.error(f"App: Signup failed for {email}: {e.message}")
                    st.error(f"Sign up failed: {e.message}")
                except Exception as e:
                    logging.error(f"App: An unexpected error occurred during signup: {e}", exc_info=True)
                    st.error("An unexpected error occurred during signup.")

# --- Main Application Logic ---

# Define the pages for navigation
pg = st.navigation(
    [
        st.Page("page_Chat.py", title="Chat", default=True),
        st.Page("page_Memory.py", title="Memory"),
    ]
)

# Gate access based on login status
# Reason: Ensures only authenticated users can access the chat functionality.
if 'user_session' not in st.session_state or st.session_state.user_session is None:
    show_login_form()
else:
    # --- Logged-in User Experience ---
    # This section runs only if the user is logged in.

    # --- Sidebar Setup (Global for Logged-in Users) ---
    with st.sidebar:

        # --- Authentication Display and Logout ---
        user_email = st.session_state.user_session.user.email
        st.subheader(f"👤 {user_email}")

        if st.button("Logout", icon=":material/logout:", use_container_width=True):
            try:
                logging.info(f"App: Logging out user: {user_email}")
                supabase_client.auth.sign_out()
                st.session_state.user_session = None # Clear session state
                reset_conversation_state(st) # Clear chat history and tokens
                logging.info("App: Logout successful.")
                st.rerun() # Rerun to show the login form
            except AuthApiError as e:
                logging.error(f"App: Logout failed: {e.message}")
                st.sidebar.error(f"Logout failed: {e.message}")
            except Exception as e:
                logging.error(f"App: An unexpected error occurred during logout: {e}", exc_info=True)
                st.sidebar.error("An unexpected error occurred during logout.")

        # --- Model Information ---
        with st.expander("🤖 Models", expanded=False):
            st.markdown("LLM model:")
            st.code(config.llm_model, language=None)
            st.markdown("Embedding model:")
            st.code(config.embedding_model, language=None)

    pg.run()
