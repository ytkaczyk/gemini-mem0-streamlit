import streamlit as st
from mem0 import Memory
import logging
from utils import Config
from supabase import create_client, Client
from google.generativeai.client import configure as genai_configure
from google.generativeai.generative_models import GenerativeModel as genai_GenerativeModel



def build_mem0_config(config: Config) -> dict:
    # Define the mem0 configuration dictionary
    # Reason: Centralizes the configuration for mem0, making it easy to manage connections.
    # Note: History manager config removed as it wasn't essential for the initial test and adds complexity.
    mem0_config = {
        "vector_store": { # Configuration for the vector database (Supabase)
            "provider": "supabase",
            "config": {
                "connection_string": config.supabase_connection_string,
                "collection_name": config.supabase_table_name,
                "embedding_model_dims": config.embedding_model_dims, # Must match the dimensions of the chosen embedding model
            }
        },
        "graph_store": { # Configuration for the graph database (Neo4j)
            "provider": "neo4j",
            "config": {
                "url": config.neo4j_url, # Connection URI for Neo4j instance
                "username": config.neo4j_username,
                "password": config.neo4j_password, # Password for Neo4j user
            }
        },
        "llm": { # Configuration for the Language Model (Gemini) used by mem0 internally
            "provider": "gemini",
            "config": {
                "model": config.llm_model, # Specific Gemini model to use
                "api_key": config.google_api_key, # API key for Gemini
            }
        },
        "embedder": { # Configuration for the embedding model (Gemini)
            "provider": "gemini",
            "config": {
                "model": config.embedding_model, # Specific Gemini embedding model
                "embedding_dims": config.embedding_model_dims, # Dimensions required by the model
                "api_key": config.google_api_key,
            }
        },
        # History manager config omitted for simplicity in app v1
    }
    
    return mem0_config


# --- Client Initialization ---
# Cache the clients using st.cache_resource to avoid re-initializing on every script rerun (e.g., user interaction).
# Reason: Improves performance and avoids unnecessary setup/connection overhead.
@st.cache_resource
def get_ai_clients(_config):
    """
    Initializes and returns the mem0, Gemini clients based on the configuration.
    Uses st.cache_resource to ensure clients are created only once per session.

    Returns:
        tuple: A tuple containing the initialized mem0, Gemini clients,
               or (None, None, None) if initialization fails for any.
    """
    mem_client = None
    gemini_client = None

    mem0_config = build_mem0_config(_config)

    # Initialize mem0 client
    logging.info("App: Initializing mem0 client...")
    try:
        # Reason: Creates the core mem0 memory object using the defined configuration.
        mem_client = Memory.from_config(mem0_config)
        logging.info("App: mem0 client initialized successfully.")
    except Exception as e:
        logging.error(f"App: Failed to initialize mem0 client: {e}", exc_info=True)
        st.error(f"Failed to initialize mem0 client: {e}") # Display error in Streamlit UI

    # Initialize Gemini client (used for direct LLM calls in this app)
    logging.info("App: Initializing Gemini client...")
    try:
        if _config.embedding_model and _config.google_api_key:
            # Reason: Configures the global genai library with the API key.
            genai_configure(api_key=_config.google_api_key)
            # Reason: Creates a client instance for the specified Gemini model.
            gemini_client = genai_GenerativeModel(_config.llm_model)
            logging.info("App: Gemini client initialized successfully.")
        else:
             # Reason: Gemini client cannot function without an API key.
             logging.error("App: GOOGLE_API_KEY not found for Gemini client initialization.")
             st.error("GOOGLE_API_KEY not found. Cannot initialize Gemini client.")
        if gemini_client:
             logging.info(f"App: Using Gemini model: {_config.llm_model}") # Log the model name
    except Exception as e:
        logging.error(f"App: Failed to initialize Gemini client: {e}", exc_info=True)
        st.error(f"Failed to initialize Gemini client: {e}")

    return mem_client, gemini_client

# --- Client Initialization ---
# Cache the clients using st.cache_resource to avoid re-initializing on every script rerun (e.g., user interaction).
# Reason: Improves performance and avoids unnecessary setup/connection overhead.
@st.cache_resource
def get_supabase_client(_config) -> Client:
    """
    Initializes and returns the Supabase client based on the configuration.
    Uses st.cache_resource to ensure clients are created only once per session.

    Returns:
        tuple: The initialized mem0, Gemini, and Supabase clients,
               or None if initialization fails.
    """
    # Initialize Supabase client (for Auth)
    logging.info("App: Initializing Supabase client...")
    if _config.supabase_url and _config.supabase_anon_key:
        # Reason: Creates the Supabase client instance needed for authentication operations.
        supabase_client: Client = create_client(_config.supabase_url, _config.supabase_anon_key)
        logging.info("App: Supabase client initialized successfully.")
        return supabase_client
    else:
        # Reason: Supabase Auth requires both URL and Anon Key.
        logging.error("App: SUPABASE_URL or SUPABASE_ANON_KEY not found for Supabase client initialization.")
        st.error("SUPABASE_URL or SUPABASE_ANON_KEY not found. Cannot initialize Supabase client.")
        raise Exception("SUPABASE_URL or SUPABASE_ANON_KEY not found. Cannot initialize Supabase client")

    return supabase_client
