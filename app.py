import streamlit as st
import os
from mem0 import Memory
from dotenv import load_dotenv
import logging
import warnings
import google.generativeai as genai

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
# Reason: Securely loads API keys and connection strings without hardcoding them.
load_dotenv()
logging.info("App: Loaded environment variables.")

# Retrieve credentials and config from environment variables
# Reason: Makes configuration flexible and avoids exposing secrets in code.
google_api_key = os.getenv("GOOGLE_API_KEY")
supabase_connection_string = os.getenv("SUPABASE_CONNECTION_STRING")
supabase_table_name = os.getenv("SUPABASE_TABLE_NAME", "documents") # Default table name if not specified
neo4j_url = os.getenv("NEO4J_URI")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
embedding_model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004") # Default embedding model
embedding_model_dims = int(os.getenv("EMBEDDING_MODEL_DIMS", "768")) # Default dimensions, ensure integer type
llm_model = os.getenv("LLM_MODEL", "gemini-1.5-flash-latest") # Default LLM model

# Validate essential variables
# Reason: Ensures the app doesn't start without critical configuration, preventing runtime errors later.
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

# Define the mem0 configuration dictionary
# Reason: Centralizes the configuration for mem0, making it easy to manage connections.
# Note: History manager config removed as it wasn't essential for the initial test and adds complexity.
mem0_config = {
    "vector_store": { # Configuration for the vector database (Supabase)
        "provider": "supabase",
        "config": {
            "connection_string": supabase_connection_string,
            "collection_name": supabase_table_name,
            "embedding_model_dims": embedding_model_dims, # Must match the dimensions of the chosen embedding model
        }
    },
    "graph_store": { # Configuration for the graph database (Neo4j)
        "provider": "neo4j",
        "config": {
            "url": neo4j_url, # Connection URI for Neo4j instance
            "username": neo4j_username,
            "password": neo4j_password, # Password for Neo4j user
        }
    },
    "llm": { # Configuration for the Language Model (Gemini) used by mem0 internally
        "provider": "gemini",
        "config": {
            "model": llm_model, # Specific Gemini model to use
            "api_key": google_api_key, # API key for Gemini
        }
    },
    "embedder": { # Configuration for the embedding model (Gemini)
        "provider": "gemini",
        "config": {
            "model": embedding_model, # Specific Gemini embedding model
            "embedding_dims": embedding_model_dims, # Dimensions required by the model
            "api_key": google_api_key,
        }
    },
    # History manager config omitted for simplicity in app v1
}

# --- Client Initialization ---
# Cache the clients using st.cache_resource to avoid re-initializing on every script rerun (e.g., user interaction).
# Reason: Improves performance and avoids unnecessary setup/connection overhead.
@st.cache_resource
def initialize_clients():
    """
    Initializes and returns the mem0 and Gemini clients based on the configuration.
    Uses st.cache_resource to ensure clients are created only once per session.

    Returns:
        tuple: A tuple containing the initialized mem0 client and Gemini client,
               or (None, None) if initialization fails for either.
    """
    mem_client = None
    gemini_client = None

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
        if google_api_key:
            # Reason: Configures the global genai library with the API key.
            genai.configure(api_key=google_api_key)
            # Reason: Creates a client instance for the specified Gemini model.
            gemini_client = genai.GenerativeModel(llm_model)
            logging.info("App: Gemini client initialized successfully.")
        else:
             # Reason: Gemini client cannot function without an API key.
             logging.error("App: GOOGLE_API_KEY not found for Gemini client initialization.")
             st.error("GOOGLE_API_KEY not found. Cannot initialize Gemini client.")
        if gemini_client:
             logging.info(f"App: Using Gemini model: {llm_model}") # Log the model name
    except Exception as e:
        logging.error(f"App: Failed to initialize Gemini client: {e}", exc_info=True)
        st.error(f"Failed to initialize Gemini client: {e}")

    return mem_client, gemini_client

memory_client, gemini_llm_client = initialize_clients()

if not memory_client or not gemini_llm_client:
    st.warning("One or more clients could not be initialized. Please check logs and configuration.")
    st.stop() # Stop execution if clients fail to initialize

# --- Streamlit UI Setup ---

# Sidebar Section
# Reason: Provides users with configuration info and control options without cluttering the main chat area.
st.sidebar.title("Gemini & mem0 Demo")
st.sidebar.subheader("⚙️ Settings")
st.sidebar.markdown("Gemini model:")
st.sidebar.code(llm_model, language=None) # Display model name read from env

st.sidebar.divider() # Visual separator
st.sidebar.subheader("💬 Conversation")
# Reason: Allows users to easily start a fresh conversation without restarting the app.
if st.sidebar.button("Clear Conversation", use_container_width=True):
    # Reason: Resets the chat message list stored in Streamlit's session state.
    st.session_state.messages = []
    logging.info("App: Conversation history cleared by user.")
    # Optional: Could also add logic here to clear mem0 history for the user_id if needed.
    # Reason: Immediately refreshes the page to show the empty chat history.
    st.rerun()

# Main Page Section
st.title("🧠 Chat with mem0")
st.caption("A simple chat interface demonstrating mem0 with Gemini, Supabase, and Neo4j.")

# Initialize chat history in session state if it doesn't exist
# Reason: Persists messages across reruns within the same user session.
if "messages" not in st.session_state:
    st.session_state.messages = []
    logging.info("App: Initialized messages in session state.")

# Display chat messages from history on app rerun
# Reason: Shows the conversation history to the user.
for message in st.session_state.messages:
    # Reason: Uses Streamlit's chat message container for styling.
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Processing ---
# This block executes when the user enters text in the chat input field.
# Reason: `st.chat_input` returns the user's input string or None if nothing was entered.
# The `:=` (walrus operator) assigns the input to `prompt` and checks if it's truthy (not None/empty) in one step.
if prompt := st.chat_input("Ask me anything..."):
    logging.info(f"App: Received prompt: {prompt}")

    # Add user message to Streamlit chat history and display it immediately
    # Reason: Provides immediate feedback to the user that their message was received.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process the prompt using mem0 and Gemini
    user_id = "streamlit_session_user" # Simple static user ID for this single-user demo
    assistant_response = None # Initialize assistant response variable

    # Main processing block with general error handling
    try:
        # --- Step 1: Search for relevant memories using mem0 ---
        logging.info(f"App: Searching memories for user '{user_id}' with query: {prompt}")
        relevant_memories = {} # Initialize as empty dict in case search fails
        memories_str = ""      # Initialize empty string for prompt formatting
        try:
            # Reason: Calls mem0's search function to find memories related to the current prompt.
            relevant_memories = memory_client.search(query=prompt, user_id=user_id, limit=5) # Limit results for context window
            # Reason: Formats the retrieved memories into a simple string for the LLM prompt.
            memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories.get("results", []))
            logging.info(f"App: Found relevant memories:\n{memories_str if memories_str else 'None'}") # Log found memories or None
        except IndexError as ie:
            # Reason: Specific handling for IndexError observed during mem0 search, likely due to LLM issues within mem0.
            logging.error(f"App: IndexError during memory search for query '{prompt}': {ie}. Likely an empty/blocked response from LLM during search.", exc_info=True)
            st.warning(f"Could not complete memory search due to an internal error (IndexError). Proceeding without retrieved memories.")
            # relevant_memories remains empty, memories_str remains empty, allowing the process to continue.

        # --- Step 2: Prepare prompt for Gemini ---
        # Reason: Constructs the system prompt, instructing the LLM on how to behave and providing retrieved memories as context.
        system_prompt = f"You are a helpful AI assistant. Answer the user's query based on the query and the following potentially relevant past memories. If the memories are not relevant, answer the query directly. Do not answer with memories that are not relevant to the query.\n\nRelevant Memories:\n{memories_str if memories_str else 'None'}"

        # Construct message history for Gemini API
        # Reason: Gemini API expects a specific format. Here, we combine the system instructions and the user's actual prompt.
        # Note: For more complex conversations, you might include more turns from st.session_state.messages.
        gemini_messages = [
            {'role': 'user', 'parts': [system_prompt, prompt]} # Gemini API structure requires 'user'/'model' roles and 'parts' list
        ]

        # --- Step 3: Call Gemini LLM ---
        logging.info("App: Calling Gemini API...")
        # Optional: Configure generation parameters like temperature for creativity.
        generation_config = genai.types.GenerationConfig(temperature=0.7)

        # Safety settings - adjust as needed
        # Reason: Configure content safety thresholds for the Gemini API response generation.
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        # Reason: Makes the actual call to the Gemini API to generate the response.
        gemini_response = gemini_llm_client.generate_content(
            gemini_messages,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        # Handle potential blocked responses from safety settings
        # Reason: Checks if the response was blocked by safety filters before trying to access content.
        if not gemini_response.candidates:
             assistant_response = "My response was blocked due to safety settings. Please rephrase your query."
             logging.warning("App: Gemini response blocked by safety settings.")
        else:
            # Extract text, handling potential errors if response structure is unexpected
            # Reason: Safely extracts the text content from the Gemini response, guarding against API changes or errors.
            try:
                 assistant_response = gemini_response.text
            except ValueError as ve:
                 # Log the full response part if text extraction fails for debugging
                 logging.error(f"App: Error extracting text from Gemini response part: {ve}. Part: {gemini_response.candidates[0]}")
                 assistant_response = "[Error processing LLM response]"
            except Exception as exc:
                 logging.error(f"App: Unexpected error extracting text from Gemini response: {exc}", exc_info=True)
                 assistant_response = "[Unexpected error processing LLM response]"

        logging.info(f"App: Received response from Gemini: {assistant_response}")

        # --- Step 4: Add conversation turn to mem0 ---
        # Reason: Stores the user query and the assistant's response in mem0 for future context retrieval.
        if assistant_response: # Only add if a valid response was generated
            conversation_turn = [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": assistant_response}
            ]
            logging.info(f"App: Adding conversation turn to mem0 for user '{user_id}'")
            # Reason: Calls mem0's add method to process and store the conversation turn in vector/graph stores.
            memory_client.add(conversation_turn, user_id=user_id)
            logging.info("App: Conversation turn added to mem0.")

            # Add assistant response to Streamlit history and display it
            # Reason: Updates the UI with the assistant's response.
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
        else:
            # Reason: Handles cases where no valid response was generated (e.g., blocked or error).
            logging.warning("App: No valid assistant response generated or extracted.")
            st.warning("Could not get a response from the assistant.") # Inform user in UI

    except Exception as e:
        # General error handling for the entire processing block
        # Reason: Catches any unexpected errors during the search, LLM call, or mem0 add process.
        error_message = f"An error occurred: {e}"
        logging.error(f"App: Error during chat processing: {error_message}", exc_info=True) # Log detailed error
        st.error(error_message) # Show error in Streamlit UI
        # Add error message to chat display for user visibility
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
        with st.chat_message("assistant"):
            st.error(f"Error: {e}")

    logging.info("App: Finished processing prompt.")

# --- Footer or other UI elements ---
# Example: st.sidebar.info("...")
