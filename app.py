import streamlit as st
from mem0 import Memory
from dotenv import load_dotenv
import logging
import warnings
from utils import Config, load_config, validate_variables, initialize_session_state_with_token, reset_conversation_state, refresh_tokens_panel, update_tokens
import google.generativeai as genai
from supabase import create_client, Client, AuthApiError # Added for Supabase Auth

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
config = load_config(logging)

# Validate required environment variables
validate_variables(st, logging, config)

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

# --- Client Initialization ---
# Cache the clients using st.cache_resource to avoid re-initializing on every script rerun (e.g., user interaction).
# Reason: Improves performance and avoids unnecessary setup/connection overhead.
@st.cache_resource
def initialize_clients():
    """
    Initializes and returns the mem0, Gemini, and Supabase clients based on the configuration.
    Uses st.cache_resource to ensure clients are created only once per session.

    Returns:
        tuple: A tuple containing the initialized mem0, Gemini, and Supabase clients,
               or (None, None, None) if initialization fails for any.
    """
    mem_client = None
    gemini_client = None
    supabase_client: Client | None = None

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
        if config.embedding_model and config.google_api_key:
            # Reason: Configures the global genai library with the API key.
            genai.configure(api_key=config.google_api_key)
            # Reason: Creates a client instance for the specified Gemini model.
            gemini_client = genai.GenerativeModel(config.llm_model)
            logging.info("App: Gemini client initialized successfully.")
        else:
             # Reason: Gemini client cannot function without an API key.
             logging.error("App: GOOGLE_API_KEY not found for Gemini client initialization.")
             st.error("GOOGLE_API_KEY not found. Cannot initialize Gemini client.")
        if gemini_client:
             logging.info(f"App: Using Gemini model: {config.llm_model}") # Log the model name
    except Exception as e:
        logging.error(f"App: Failed to initialize Gemini client: {e}", exc_info=True)
        st.error(f"Failed to initialize Gemini client: {e}")

    # Initialize Supabase client (for Auth)
    logging.info("App: Initializing Supabase client...")
    try:
        if config.supabase_url and config.supabase_anon_key:
            # Reason: Creates the Supabase client instance needed for authentication operations.
            supabase_client = create_client(config.supabase_url, config.supabase_anon_key)
            logging.info("App: Supabase client initialized successfully.")
        else:
            # Reason: Supabase Auth requires both URL and Anon Key.
            logging.error("App: SUPABASE_URL or SUPABASE_ANON_KEY not found for Supabase client initialization.")
            st.error("SUPABASE_URL or SUPABASE_ANON_KEY not found. Cannot initialize Supabase client.")
    except Exception as e:
        logging.error(f"App: Failed to initialize Supabase client: {e}", exc_info=True)
        st.error(f"Failed to initialize Supabase client: {e}")

    return mem_client, gemini_client, supabase_client

memory_client, gemini_llm_client, supabase = initialize_clients() # Added supabase client

if not memory_client or not gemini_llm_client or not supabase:
    st.warning("One or more clients (mem0, Gemini, Supabase) could not be initialized. Please check logs and configuration.")
    st.stop() # Stop execution if clients fail to initialize

# response chunker
def chunk_response(response):
    try:
        for chunk in response:
            if hasattr(chunk, 'text') and chunk.text:
                yield chunk.text
    except ValueError as ve:
        logging.warning(f"App: Error in chunking response: {ve}", exc_info=True)
        yield "" # Handle any errors in chunking gracefully

initialize_session_state_with_token(st)

# --- Authentication Logic ---

# Initialize session state for user session if it doesn't exist
if 'user_session' not in st.session_state:
    st.session_state.user_session = None
    logging.info("App: Initialized user_session in session state.")

def show_login_form():
    """
    Displays the login/signup form and handles authentication logic.
    """
    st.title("Login / Sign Up")
    st.caption("Please log in or sign up to use the chat.")

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
                    session = supabase.auth.sign_in_with_password({"email": email, "password": password})
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
                    session = supabase.auth.sign_up({"email": email, "password": password})
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

# --- Streamlit UI Setup ---

# Sidebar Section
# Reason: Provides users with configuration info and control options without cluttering the main chat area.
show_memory = False # Default to not showing memory info
tokens_panel_placeholder = None # Placeholder for token usage display

with st.sidebar:
    st.title("Gemini & mem0 Demo")

    # --- Authentication Display and Logout ---
    # Reason: Shows user status and provides logout functionality in the sidebar.
    st.subheader("👤 Account")
    if st.session_state.user_session:
        user_email = st.session_state.user_session.user.email
        st.markdown(f"Logged in as:")
        st.code(user_email, language=None)
        if st.button("Logout", use_container_width=True):
            try:
                logging.info(f"App: Logging out user: {user_email}")
                # Reason: Calls Supabase Auth to invalidate the current session.
                supabase.auth.sign_out()
                st.session_state.user_session = None # Clear session state
                reset_conversation_state(st)
                logging.info("App: Logout successful.")
                st.rerun() # Rerun to show the login form
            except AuthApiError as e:
                logging.error(f"App: Logout failed: {e.message}")
                st.sidebar.error(f"Logout failed: {e.message}")
            except Exception as e:
                logging.error(f"App: An unexpected error occurred during logout: {e}", exc_info=True)
                st.sidebar.error("An unexpected error occurred during logout.")
    else:
        st.markdown("Status: Logged Out")

    st.divider() # Visual separator

    # --- Model Information ---
    st.subheader("🤖 Model")
    st.markdown("Gemini model:")
    st.code(config.llm_model, language=None) # Display model name read from config
    st.markdown("Embedding model:")
    st.code(config.embedding_model, language=None) # Display embedding model name read from config

    st.divider()

    st.subheader("💬 Conversation")

    # Add a toggle to show/hide memory info messages
    show_memory = st.checkbox("Show memory information", value=False)

    # Update Token Usage Display
    tokens_panel_placeholder = st.empty()
    refresh_tokens_panel(st, tokens_panel_placeholder)

    # Allows users to easily start a fresh conversation without restarting the app.
    # Only show clear button if logged in
    if st.session_state.user_session:
        if st.button("Clear Conversation", use_container_width=True):
            reset_conversation_state(st)
            logging.info(f"App: Conversation history cleared by user: {st.session_state.user_session.user.email}")
            st.rerun()

# --- Main Application Logic ---

# Gate access based on login status
# Reason: Ensures only authenticated users can access the chat functionality.
if not st.session_state.user_session:
    show_login_form()
    st.stop() # Stop execution if not logged in

# --- Logged-in Chat Interface ---
# This section only runs if the user is logged in.

st.title("🧠 Chat with mem0")
st.caption(f"Logged in as {st.session_state.user_session.user.email}. Using mem0 with Gemini, Supabase, and Neo4j.")

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
    # --- Step 5.7: Use Authenticated User ID ---
    # Reason: Associates memories and searches with the specific logged-in user.
    user_id = st.session_state.user_session.user.id
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

            if memories_str and show_memory:
                with st.chat_message("memory info", avatar="🧠"):
                    st.markdown(f"**Relevant Memories:**\n{memories_str if memories_str else 'None'}")
                
        except IndexError as ie:
            # Reason: Specific handling for IndexError observed during mem0 search, likely due to LLM issues within mem0.
            logging.error(f"App: IndexError during memory search for query '{prompt}': {ie}. Likely an empty/blocked response from LLM during search.", exc_info=True)
            st.warning(f"Could not complete memory search due to an internal error (IndexError). Proceeding without retrieved memories.")
            # relevant_memories remains empty, memories_str remains empty, allowing the process to continue.

        # --- Step 2: Prepare prompt for Gemini ---
        # Reason: Constructs the system prompt, instructing the LLM on how to behave and providing retrieved memories as context.
        system_prompt = (
            "You are a helpful AI assistant. Answer the user's query based on the query and the following potentially relevant past memories. "
            "If the memories are not relevant, answer the query directly. Do not answer with memories that are not relevant to the query.\n\n"
            f"Relevant Memories:\n{memories_str if memories_str else 'None'}"
        )

        # Construct message history for Gemini API
        # Reason: Gemini API expects a specific format. Here, we combine the system instructions and the user's actual prompt.
        # Include previous conversation turns to maintain context.
        gemini_messages = []
        gemini_messages.append({'role': 'user', 'parts': [system_prompt]}) # System prompt goes first
        for msg in st.session_state.messages: # Iterate through existing messages
            gemini_messages.append({'role': msg['role'], 'parts': [msg['content']]}) # Add each message to the history
        gemini_messages.append({'role': 'user', 'parts': [prompt]}) # Finally, add the current user prompt

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
            safety_settings=safety_settings,
            stream=True
        )

        # Initialize an empty string to accumulate the response
        assistant_response = ""

        # Stream the response and accumulate it
        with st.chat_message("assistant"):
            try:
                assistant_response = st.write_stream(chunk_response(gemini_response))

                # Handle potential blocked responses from safety settings
                if gemini_response.candidates and gemini_response.candidates[0].finish_reason != 1:
                    logging.warning(f"App: Gemini response was not finished. Reason: {gemini_response.candidates[0].finish_reason}")
                    assistant_response = "My response was blocked due to safety settings. Please rephrase your query."
                    st.write(assistant_response)
            except ValueError as ve:
                # Log the full response part if text extraction fails for debugging
                logging.error(f"App: Error extracting text from Gemini response part: {ve}. Part: {gemini_response.candidates[0]}")
                assistant_response = "[Error processing LLM response]"
                st.write(assistant_response) # Show error in UI
            except Exception as exc:
                logging.error(f"App: Unexpected error extracting text from Gemini response: {exc}", exc_info=True)
                assistant_response = "[Unexpected error processing LLM response]"
                st.write(assistant_response) # Show error in UI

        logging.info(f"App: Received response from Gemini: {assistant_response}")

        # --- Step 4: Update token counts ---
        update_tokens(st, gemini_response)
        # Update Token Usage Display
        refresh_tokens_panel(st, tokens_panel_placeholder)

        # --- Step 5: Add conversation turn to mem0 ---
        # Reason: Stores the user query and the assistant's response in mem0 for future context retrieval.
        if assistant_response: # Only add if a valid response was generated
            conversation_turn = [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": assistant_response}
            ]
            user_email = st.session_state.user_session.user.email # Get user email from session
            logging.info(f"App: Adding conversation turn to mem0 for user '{user_id}' with email '{user_email}'")
            # Reason: Calls mem0's add method to process and store the conversation turn in vector/graph stores, including email metadata.
            memory_change_results = memory_client.add(
                conversation_turn,
                user_id=user_id,
                metadata={"email": user_email} # Add email as metadata
            )

            memories_changes_str = \
                "\n".join(f"- ✔️ {entry['memory']}" for entry in memory_change_results.get("results", []) if entry.get("event", "") == "ADD") + \
                "\n".join(f"- ❌ {entry['memory']}" for entry in memory_change_results.get("results", []) if entry.get("event", "") == "DELETE") + \
                "\n".join(f"- ♻️ {entry['previous_memory']} ➡️ {entry['memory']}" for entry in memory_change_results.get("results", []) if entry.get("event", "") == "UPDATE")

            if memories_changes_str and show_memory:
                with st.chat_message("memory info", avatar="🧠"):
                    st.markdown(f"**Updated Memories:**\n{memories_changes_str if memories_changes_str else 'None'}")

            logging.info("App: Conversation turn added to mem0.")

            # Add assistant response to Streamlit history and display it
            # Reason: Updates the UI with the assistant's response.
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        else:
            # Reason: Handles cases where no valid response was generated or extracted.
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
