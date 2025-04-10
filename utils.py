import streamlit as st
import os

class Config:
    """
    A class to load and store configuration variables from environment variables.
    """

    def __init__(self):
        """
        Initializes the Config object by loading environment variables.
        """
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.supabase_connection_string = os.getenv("SUPABASE_CONNECTION_STRING")
        self.supabase_table_name = os.getenv("SUPABASE_TABLE_NAME", "documents")  # Default table name if not specified
        self.neo4j_url = os.getenv("NEO4J_URI")
        self.neo4j_username = os.getenv("NEO4J_USERNAME")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")  # Default embedding model
        self.embedding_model_dims = int(os.getenv("EMBEDDING_MODEL_DIMS", "768"))  # Default dimensions, ensure integer type
        self.llm_model = os.getenv("LLM_MODEL", "gemini-1.5-flash-latest")  # Default LLM model
        self.supabase_url = os.getenv("SUPABASE_URL")  # Added for Supabase Auth
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")  # Added for Supabase Auth

@st.cache_resource
def load_config(logging):
    """
    Loads the configuration from environment variables and returns a Config object.
    Config variables are cached as resources to improve performance.
    
    Returns:
        Config: An instance of the Config class containing the loaded configuration.
    """
    logging.info("Loading configuration from environment variables.")
    config = Config()
    return config

def validate_variables(st, logging, config):
    """
    Validates the presence of essential environment variables required for the app to function.
    Stops the app execution if any critical variables are missing.

    Raises:
        Streamlit error and logs missing variables if validation fails.
    """
    # Validate essential variables
    # Reason: Ensures the app doesn't start without critical configuration, preventing runtime errors later.
    essential_vars = {
        "GOOGLE_API_KEY": config.google_api_key,
        "SUPABASE_CONNECTION_STRING": config.supabase_connection_string, # For mem0 vector store
        "SUPABASE_URL": config.supabase_url, # For Supabase Auth client
        "SUPABASE_ANON_KEY": config.supabase_anon_key, # For Supabase Auth client
        "NEO4J_URI": config.neo4j_url,
        "NEO4J_USERNAME": config.neo4j_username,
        "NEO4J_PASSWORD": config.neo4j_password,
    }
    missing_vars = [name for name, value in essential_vars.items() if not value]
    if missing_vars:
        st.error(f"Missing essential environment variables in .env file: {', '.join(missing_vars)}")
        logging.error(f"App: Missing essential environment variables: {', '.join(missing_vars)}")
        st.stop() # Stop the app if config is missing

def initialize_session_state_with_token(st):
    """
    Initialize session state for token counts
    """
    if "prompt_tokens" not in st.session_state:
        st.session_state.prompt_tokens = 0

    if "response_tokens" not in st.session_state:
        st.session_state.response_tokens = 0

    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0

    if "cumulative_prompt_tokens" not in st.session_state:
        st.session_state.cumulative_prompt_tokens = 0

    if "cumulative_response_tokens" not in st.session_state:
        st.session_state.cumulative_response_tokens = 0

    if "cumulative_total_tokens" not in st.session_state:
        st.session_state.cumulative_total_tokens = 0

def reset_conversation_state(st):
    """
    Resets the session state variables related to user session and messages.
    """
     # Reset chat history
    st.session_state.messages = []
    # Reset token counts
    st.session_state.prompt_tokens = 0
    st.session_state.response_tokens = 0
    st.session_state.total_tokens = 0
    st.session_state.cumulative_prompt_tokens = 0
    st.session_state.cumulative_response_tokens = 0
    st.session_state.cumulative_total_tokens = 0

def refresh_tokens_panel(st, tokens_panel):
    """
    Refreshes the token usage display in the sidebar.
    """
    with tokens_panel.container():
        with st.expander("Tokens", expanded=True):
            total_col1, total_col2, total_col3 = st.columns(3)
            with total_col2:
                st.metric(label="**Total**", value = st.session_state.cumulative_total_tokens, delta= st.session_state.total_tokens)
            details_col1, details_col2 = st.columns(2)
            with details_col1:
                st.metric(label="Prompt", value = st.session_state.cumulative_prompt_tokens, delta= st.session_state.prompt_tokens, border = True)
            with details_col2:
                st.metric(label="Response", value = st.session_state.cumulative_response_tokens, delta= st.session_state.response_tokens, border = True)

def update_tokens(st, response):
    """
    Updates the token counts in the session state.
    """
    # Extract token counts from the response
    prompt_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
    response_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0
    total_tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0

    # Update token counts
    st.session_state.prompt_tokens = prompt_tokens
    st.session_state.response_tokens = response_tokens
    st.session_state.total_tokens = total_tokens

    # Update cumulative token counts
    st.session_state.cumulative_prompt_tokens += prompt_tokens
    st.session_state.cumulative_response_tokens += response_tokens
    st.session_state.cumulative_total_tokens += total_tokens