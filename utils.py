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