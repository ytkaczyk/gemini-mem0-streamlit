import streamlit as st
import os
from mem0 import Memory
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Streamlit Page Config (MUST be the first Streamlit command) ---
st.set_page_config(page_title="mem0 Demo Chat", layout="wide")

# --- Configuration Loading ---
# Load environment variables from .env file
load_dotenv()
logging.info("App: Loaded environment variables.")

# Retrieve credentials and config from environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")
supabase_connection_string = os.getenv("SUPABASE_CONNECTION_STRING")
supabase_table_name = os.getenv("SUPABASE_TABLE_NAME", "documents")
neo4j_url = os.getenv("NEO4J_URI")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
embedding_model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
embedding_model_dims = int(os.getenv("EMBEDDING_MODEL_DIMS", "768")) # Match test script default
llm_model = os.getenv("LLM_MODEL", "gemini-1.5-flash-latest")

# Validate essential variables
essential_vars = {
    "GOOGLE_API_KEY": google_api_key,
    "SUPABASE_CONNECTION_STRING": supabase_connection_string,
    "NEO4J_URI": neo4j_url,
    "NEO4J_USERNAME": neo4j_username,
    "NEO4J_PASSWORD": neo4j_password,
}
missing_vars = [name for name, value in essential_vars.items() if not value]
if missing_vars:
    st.error(f"Missing essential environment variables in .env file: {', '.join(missing_vars)}")
    logging.error(f"App: Missing essential environment variables: {', '.join(missing_vars)}")
    st.stop() # Stop the app if config is missing

# Define the mem0 configuration (matching the successful test script)
# Note: History manager config removed as it wasn't essential for the test and might need Supabase URL/Key which we didn't validate
mem0_config = {
    "vector_store": {
        "provider": "supabase",
        "config": {
            "connection_string": supabase_connection_string,
            "collection_name": supabase_table_name,
            "embedding_model_dims": embedding_model_dims,
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": neo4j_url,
            "username": neo4j_username,
            "password": neo4j_password,
        }
    },
    "llm": {
        "provider": "gemini",
        "config": {
            "model": llm_model,
            "api_key": google_api_key,
        }
    },
    "embedder": {
        "provider": "gemini",
        "config": {
            "model": embedding_model,
            "embedding_dims": embedding_model_dims, # Use the validated dimension
            "api_key": google_api_key,
        }
    },
    # History manager config omitted for simplicity in app v1
}

# --- mem0 Initialization ---
# Cache the mem0 client to avoid re-initializing on each interaction
@st.cache_resource
def get_mem0_client():
    """Initializes and returns the mem0 client."""
    logging.info("App: Initializing mem0 client...")
    try:
        memory = Memory.from_config(mem0_config)
        logging.info("App: mem0 client initialized successfully.")
        return memory
    except Exception as e:
        logging.error(f"App: Failed to initialize mem0 client: {e}", exc_info=True)
        st.error(f"Failed to initialize mem0 client: {e}")
        return None

memory_client = get_mem0_client()

if not memory_client:
    st.warning("Mem0 client could not be initialized. Please check logs and configuration.")
    st.stop()

# --- Streamlit UI Setup ---
# Page config moved to the top
st.title("🧠 Chat with mem0")
st.caption("A simple chat interface demonstrating mem0 with Gemini, Supabase, and Neo4j.")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    logging.info("App: Initialized messages in session state.")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Processing ---
if prompt := st.chat_input("Ask me anything..."):
    logging.info(f"App: Received prompt: {prompt}")
    # Add user message to history and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process with mem0 and get response
    try:
        logging.info("App: Calling mem0.chat()...")
        # Use the mem0 chat method which should handle context retrieval and generation
        # We need a consistent user_id for the session
        user_id = "streamlit_session_user" # Simple ID for this demo

        # Prepare message history for mem0.chat() if needed, or just send the prompt
        # Based on quickstart, mem0.chat() might take the prompt directly
        # Let's try sending just the prompt first. If context is poor, we might need to send history.
        response = memory_client.chat(prompt, user_id=user_id)

        if response:
            logging.info(f"App: Received response from mem0: {response}")
            # Add assistant response to history and display
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
        else:
            logging.warning("App: Received empty response from mem0.chat()")
            st.warning("Received no response from the memory agent.")
            # Optionally add a placeholder message
            # st.session_state.messages.append({"role": "assistant", "content": "[No response generated]"})
            # with st.chat_message("assistant"):
            #     st.markdown("[No response generated]")

    except Exception as e:
        error_message = f"An error occurred while processing your message: {e}"
        logging.error(f"App: Error during mem0 processing: {error_message}", exc_info=True)
        st.error(error_message)
        # Add error message to chat display
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
        with st.chat_message("assistant"):
            st.error(f"Error: {e}")

    # No explicit st.rerun() needed here, Streamlit handles it after input processing.
    logging.info("App: Finished processing prompt.")
