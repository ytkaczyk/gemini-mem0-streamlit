import streamlit as st
from mem0 import Memory
from dotenv import load_dotenv
import logging
import warnings
from utils import get_config
from client_utils import get_clients

# --- Initial Setup ---
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.v1.typing")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration Loading ---
load_dotenv()
logging.info("Memory Page: Loaded environment variables.")
config = get_config(logging)

memory_client, gemini_llm_client, supabase = get_clients(config)

# --- Authentication Check ---
if 'user_session' not in st.session_state or st.session_state.user_session is None:
    st.warning("Please log in first.")
    st.link_button("Go to Login", "/")
    st.stop()

# Stop if mem0 client failed to initialize
if not memory_client:
    st.warning("mem0 client could not be initialized for the memory page. Cannot display memories.")
    st.stop()

# --- Memory Display Logic ---
st.title("🧠 Memories")
st.caption("Displaying all memories stored by mem0 for your account.")

user_id = st.session_state.user_session.user.id
logging.info(f"Memory Page: Fetching memories for user_id: {user_id}")

try:
    # Fetch all memories for the logged-in user
    # Note: mem0's get_all might return an iterator or list depending on version.
    # Adjust processing accordingly. Assuming it returns a list of dictionaries.
    all_memories = memory_client.get_all(user_id=user_id)

    if all_memories:
        logging.info(f"Memory Page: Found {len(all_memories)} memories.")
        # Display memories - st.dataframe might be suitable if structure is consistent
        # st.dataframe(all_memories)
        # Or display as JSON for clarity
        st.json(all_memories, expanded=False) # Show collapsed by default

        # Alternatively, iterate and display nicely
        # st.subheader("Stored Memory Records:")
        # for i, memory in enumerate(all_memories):
        #     with st.expander(f"Memory {i+1} (ID: {memory.get('id', 'N/A')})"):
        #         st.write(memory.get('memory', 'No content'))
        #         st.caption(f"Created: {memory.get('created_at', 'N/A')}")
        #         st.json(memory.get('metadata', {})) # Show metadata

    else:
        logging.info(f"Memory Page: No memories found for user_id: {user_id}")
        st.info("No memories found for your account yet. Start chatting to create some!")

except Exception as e:
    error_message = f"An error occurred while fetching memories: {e}"
    logging.error(f"Memory Page: {error_message}", exc_info=True)
    st.error(error_message)
