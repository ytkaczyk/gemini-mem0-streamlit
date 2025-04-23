import logging
import pandas as pd
import streamlit as st
import warnings
from client_utils import get_clients
from dotenv import load_dotenv
from streamlit_agraph import agraph
from streamlit_graph.config import Config as GraphConfig
from streamlit_graph.triple_store import TripleStore, Node, Edge
from utils import get_config

# --- Initial Setup ---
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.v1.typing")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration Loading ---
load_dotenv()
logging.info("Memory Page: Loaded environment variables.")
config = get_config(logging)

memory_client, gemini_llm_client, supabase_client = get_clients(config)

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
st.caption("Displaying all stored memories for your account.")

user_id = st.session_state.user_session.user.id
logging.info(f"Memory Page: Fetching memories for user_id: {user_id}")

try:
    # Fetch all memories for the logged-in user
    # Note: mem0's get_all might return an iterator or list depending on version.
    # Adjust processing accordingly. Assuming it returns a list of dictionaries.
    all_memories = memory_client.get_all(user_id=user_id)

    if all_memories:
        vector_page, graphs_page = st.tabs(["Vector Memories", "Graphs Memories"])
        with vector_page:
            # Display as a table
            df = pd.DataFrame(all_memories["results"])
            df.set_index("id", inplace=True)  # Set 'id' as index for better readability
            st.dataframe( \
                df, 
                use_container_width=True,
                hide_index=True, 
                column_order=["memory", "created_at", "updated_at"],
                column_config={
                    "memory": st.column_config.TextColumn("Memory", width="large"),
                    "created_at": st.column_config.DatetimeColumn("Created At", format="MM-DD-YYYY HH:mm:ss", width="small"),
                    "updated_at": st.column_config.DatetimeColumn("Updated At", format="MM-DD-YYYY HH:mm:ss", width="small"),
                }
            )

        with graphs_page:
            def personalize_node(node: Node) -> Node:
                if(node.id == user_id):
                    node.color = "green"
                    node.title = "You"
                node.label = node.title
                return node


            # Display neo4j data as a graph
            store = TripleStore()

            for memory in all_memories["relations"]:
                source = personalize_node(Node(id=memory["source"]))
                target = personalize_node(Node(id=memory["target"]))
                relationship = Edge(source=source.id, target=target.id, title=memory["relationship"], label=memory["relationship"])
                store.add_triple_base(source, relationship, target)

            nodes = list(store.getNodes())
            edges = list(store.getEdges())

            graph_config = GraphConfig(height="800px", width="100%", solver="repulsion")

            agraph(nodes, edges, graph_config)

    else:
        logging.info(f"Memory Page: No memories found for user_id: {user_id}")
        st.info("No memories found for your account yet. Start chatting to create some!")

except Exception as e:
    error_message = f"An error occurred while fetching memories: {e}"
    logging.error(f"Memory Page: {error_message}", exc_info=True)
    st.error(error_message)
