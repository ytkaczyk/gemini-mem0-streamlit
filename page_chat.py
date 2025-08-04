from client_utils import get_ai_clients
from dotenv import load_dotenv
from google.generativeai import types as genai_types
import logging
import warnings
from utils import (
    get_config,
    initialize_session_state_with_token,
    refresh_tokens_panel,
    reset_conversation_state,
    update_tokens,
)
import streamlit as st

# Suppress specific DeprecationWarning from pydantic v1 typing
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.v1.typing")

# Configure logging (optional, could inherit from app.py if run together, but good practice for standalone page logic)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Chat Page UI Setup ---

st.title("🤖💬 Chat")
st.caption(f"Using mem0 with Gemini, Supabase, and Neo4j.")

def store_value(key):
    st.session_state[key] = st.session_state["_"+key]

def load_value(key, default=None):
    if key not in st.session_state:
        st.session_state[key] = default
    st.session_state["_"+key] = st.session_state[key]

# --- Configuration Loading ---
# Load environment variables from .env file
load_dotenv()
logging.info("Chat Page: Loaded environment variables.")
config = get_config(logging)

# Load the clients (cached resources)
memory_client, gemini_llm_client = get_ai_clients(config)

if not memory_client or not gemini_llm_client:
    st.warning("One or more clients (mem0, Gemini) could not be initialized. Please check logs and configuration.")
    st.stop() # Stop execution if clients fail to initialize

# --- Authentication Check ---
# Ensure user is logged in before proceeding. Session state is shared across pages.
if 'user_session' not in st.session_state or st.session_state.user_session is None:
    st.warning("Please log in first.")
    st.link_button("Go to Login", "/") # Link back to the main app page (which handles login)
    st.stop()

# Stop if clients failed to initialize
if not memory_client or not gemini_llm_client:
    st.warning("One or more clients (mem0, Gemini, Supabase) could not be initialized for the chat page. Please check logs and configuration.")
    st.stop()

# Initialize session state for chat-specific things if they don't exist
initialize_session_state_with_token(st) # Ensures token counts are initialized

# Sidebar Section (Chat Page Specific)
show_memory = False # Default to not showing memory info
tokens_panel_placeholder = None # Placeholder for token usage display

with st.sidebar:
    # Placeholder for sidebar content managed by app.py (like logout, global info)
    # Add chat-specific controls here if needed

    with st.expander("💬 Conversation", expanded=True):
        if st.button("Clear Conversation", use_container_width=True):
            reset_conversation_state(st)
            # Rerun the current page after clearing state
            st.rerun()

        # Add a toggle to show/hide memory info messages
        load_value("show_memory", default=False)
        show_memory = st.toggle("Show memory information", key="_show_memory", on_change=store_value, args=("show_memory",))

        # Token display placeholder - content will be updated by refresh_tokens_panel
        tokens_panel_placeholder = st.empty()
        # Initial display of token counts
        refresh_tokens_panel(st, tokens_panel_placeholder)

# --- Main Chat Interface Logic ---

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    logging.info("Chat Page: Initialized messages in session state.")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# response chunker
def chunk_response(response):
    try:
        for chunk in response:
            if hasattr(chunk, 'text') and chunk.text:
                yield chunk.text
    except ValueError as ve:
        logging.warning(f"Chat Page: Error in chunking response: {ve}", exc_info=True)
        yield "" # Handle any errors in chunking gracefully
    except Exception as e: # Catch other potential errors during iteration
        logging.error(f"Chat Page: Unexpected error during response chunking: {e}", exc_info=True)
        yield f"[Error processing response chunk: {e}]"

# --- Chat Input and Processing ---
if prompt := st.chat_input("Ask me anything..."):
    logging.info(f"Chat Page: Received prompt: {prompt}")

    # Add user message to Streamlit chat history and display it immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process the prompt using mem0 and Gemini
    user_id = st.session_state.user_session.user.id
    assistant_response = None

    try:
        # --- Step 1: Search for relevant memories using mem0 ---
        logging.info(f"Chat Page: Searching memories for user '{user_id}' with query: {prompt}")
        relevant_memories = {}
        memories_str = ""
        try:
            relevant_memories = memory_client.search(query=prompt, user_id=user_id, limit=5)
            memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories.get("results", []))
            logging.info(f"Chat Page: Found relevant memories:\n{memories_str if memories_str else 'None'}")

            if memories_str and show_memory:
                 # Display memory info if checkbox is ticked
                 with st.chat_message("memory info", avatar="🧠"):
                    st.markdown(f"**Relevant Memories:**\n{memories_str if memories_str else 'None'}")

        except IndexError as ie:
            logging.error(f"Chat Page: IndexError during memory search for query '{prompt}': {ie}. Likely an empty/blocked response from LLM during search.", exc_info=True)
            st.warning(f"Could not complete memory search due to an internal error (IndexError). Proceeding without retrieved memories.")

        # --- Step 2: Prepare prompt for Gemini ---
        system_prompt = (
            "You are a helpful AI assistant. Answer the user's query based on the query and the following potentially relevant past memories. "
            "If the memories are not relevant, answer the query directly. Do not answer with memories that are not relevant to the query.\n\n"
            f"Relevant User Memories:\n{memories_str if memories_str else 'None'}"
        )
        gemini_messages = []
        gemini_messages.append({'role': 'user', 'parts': [system_prompt]})
        # Include previous conversation turns (ensure roles are 'user'/'model' for Gemini)
        for msg in st.session_state.messages:
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_messages.append({'role': role, 'parts': [msg['content']]})

        # --- Step 3: Call Gemini LLM ---
        logging.info("Chat Page: Calling Gemini API...")
        generation_config = genai_types.GenerationConfig(temperature=0.7)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        gemini_response = gemini_llm_client.generate_content(
            gemini_messages,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True
        )

        assistant_response = ""
        with st.chat_message("assistant"):
            try:
                # Use the chunk_response helper function to stream the response
                assistant_response = st.write_stream(chunk_response(gemini_response))

            except Exception as exc:
                logging.error(f"Chat Page: Unexpected error during response streaming or processing: {exc}", exc_info=True)
                assistant_response = "[Unexpected error processing LLM response]"
                st.write(assistant_response) # Show error in UI

        logging.info(f"Chat Page: Received response from Gemini: {assistant_response}")

        # --- Step 4: Update token counts ---
        try:
            # Attempt to update tokens - may fail if metadata isn't available post-stream
            update_tokens(st, gemini_response)
            # Update Token Usage Display in the sidebar
            refresh_tokens_panel(st, tokens_panel_placeholder)

        except Exception as token_exc:
             logging.warning(f"Chat Page: Could not update token counts after streaming: {token_exc}", exc_info=True)
             # Optionally display a message in the panel if update fails
             tokens_panel_placeholder.warning("Token counts may be inaccurate for the last message.")

        # --- Step 5: Add conversation turn to mem0 ---
        if assistant_response and type(assistant_response) is str and assistant_response.strip() and not assistant_response.startswith("[Error"):
            conversation_turn = [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": assistant_response}
            ]
            user_email = st.session_state.user_session.user.email
            logging.info(f"Chat Page: Adding conversation turn to mem0 for user '{user_id}' with email '{user_email}'")
            try:
                memory_change_results = memory_client.add(
                    conversation_turn,
                    user_id=user_id,
                    metadata={"email": user_email}
                )

                memories_changes_str = \
                    "\n".join(f"- ✔️ {entry['memory']}" for entry in memory_change_results.get("results", []) if entry.get("event", "") == "ADD") + \
                    "\n".join(f"- ❌ {entry['memory']}" for entry in memory_change_results.get("results", []) if entry.get("event", "") == "DELETE") + \
                    "\n".join(f"- ♻️ {entry['previous_memory']} ➡️ {entry['memory']}" for entry in memory_change_results.get("results", []) if entry.get("event", "") == "UPDATE")

                if memories_changes_str and show_memory:
                    with st.chat_message("memory info", avatar="🧠"):
                        st.markdown(f"**Updated Memories:**\n{memories_changes_str if memories_changes_str else 'None'}")

                logging.info("Chat Page: Conversation turn added to mem0.")
            except Exception as mem_add_err:
                logging.error(f"Chat Page: Failed to add conversation turn to mem0: {mem_add_err}", exc_info=True)
                st.error(f"Failed to save conversation memory: {mem_add_err}")

            # Add assistant response to Streamlit history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        else:
            logging.warning("Chat Page: No valid assistant response generated or extracted to add to history/memory.")

    except Exception as e:
        error_message = f"An error occurred during chat processing: {e}"
        logging.error(f"Chat Page: {error_message}", exc_info=True)
        st.error(error_message)
        # Add error message to chat display for user visibility
        st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
        with st.chat_message("assistant"):
            st.error(f"Error: {e}")

    logging.info("Chat Page: Finished processing prompt.")


