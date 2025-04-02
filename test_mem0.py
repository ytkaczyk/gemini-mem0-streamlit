import os
from mem0 import Memory
from dotenv import load_dotenv
import logging
import warnings

# Suppress specific DeprecationWarning from pydantic v1 typing
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.v1.typing")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()
logging.info("Loaded environment variables.")

# --- Configuration ---
# Retrieve credentials from environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")
supabase_url = os.getenv("SUPABASE_URL") # Keep for history manager construction
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY") # Keep for history manager construction
supabase_connection_string = os.getenv("SUPABASE_CONNECTION_STRING") # For vector store
supabase_table_name = os.getenv("SUPABASE_TABLE_NAME", "documents") # Default collection name
neo4j_url = os.getenv("NEO4J_URI") # Reads NEO4J_URI, but mem0 config expects 'url'
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
embedding_model = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004") # Default embedding
embedding_model_dims = int(os.getenv("EMBEDDING_MODEL_DIMS", "768")) # Default embedding dims for Gemini - FIXED COMMA
llm_model = os.getenv("LLM_MODEL", "gemini-1.5-flash-latest") # Default LLM

# Validate that essential variables are loaded
essential_vars = {
    "GOOGLE_API_KEY": google_api_key,
    "SUPABASE_CONNECTION_STRING": supabase_connection_string, # Check connection string
    "NEO4J_URI": neo4j_url, # Check Neo4j URL (read from NEO4J_URI env var)
    "NEO4J_USERNAME": neo4j_username,
    "NEO4J_PASSWORD": neo4j_password,
    # Supabase URL/Key are needed for history manager construction, check them too
    "SUPABASE_URL": supabase_url,
    "SUPABASE_SERVICE_KEY": supabase_service_key,
}

missing_vars = [name for name, value in essential_vars.items() if not value]
if missing_vars:
    logging.error(f"Missing essential environment variables: {', '.join(missing_vars)}")
    exit(1)
else:
    logging.info("All essential environment variables found.")

# Define the mem0 configuration dictionary
# Structure based on mem0 documentation examples
config = {
    "vector_store": {
        "provider": "supabase", # Error indicated Supabase uses pgvector provider internally
        "config": {
            # Based on error: "Please input only the following fields: index_method, connection_string, embedding_model_dims, index_measure, collection_name"
            "connection_string": supabase_connection_string,
            "collection_name": supabase_table_name,
            "embedding_model_dims": embedding_model_dims,
            # "index_method": "hnsw", # Optional: Specify index method if needed
            # "index_measure": "cosine" # Optional: Specify distance measure if needed
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            # Based on error: "Please provide 'url', 'username' and 'password'."
            "url": neo4j_url, # Use 'url' instead of 'uri'
            "username": neo4j_username,
            "password": neo4j_password,
        }
    },
    "llm": {
        "provider": "gemini",
        "config": {
            "model": llm_model,
            "api_key": google_api_key,
            # "temperature": 0.7 # Optional: Adjust temperature if needed
        },
        "prompt": { # Optional: Define custom prompts if needed
            # "system": "You are an AI assistant.",
            # "history": "...",
            # "user": "...",
            # "memory": "..."
        }
    },
    "embedder": {
        "provider": "gemini",
        "config": {
            "model": embedding_model,
            "embedding_dims": embedding_model_dims,
            "api_key": google_api_key,
            # "task_type" is not a valid argument here according to the error and docs
        }
    },
    "history_manager": {
        "provider": "postgres", # Assuming history is stored alongside vectors in Supabase/Postgres
        "config": {
            "url": supabase_url.replace("https://", "postgresql://postgres:").replace(".supabase.co", f":{supabase_service_key}@db.{supabase_url.split('.')[0]}.supabase.co:5432/postgres"), # Construct PG connection string
            "table_name": "mem0_history" # Default or specify
        }
    },
    # Optional: Add other configurations like ranking, retrieval, etc. if needed
    # "retriever": { ... }
    # "ranker": { ... }
}

logging.info("mem0 configuration prepared.")
# print("DEBUG: Config structure:", config) # Uncomment for debugging config structure

# --- Initialization & Testing ---
try:
    logging.info("Initializing mem0 Memory...")
    # Initialize mem0 with the configuration
    memory = Memory.from_config(config)
    logging.info("mem0 Memory initialized successfully.")

    # Define a test user ID
    test_user_id = "test_connection_user"

    # Test adding a memory
    logging.info(f"Attempting to add memory for user: {test_user_id}")
    memory.add([{"role": "user", "content": "My favorite color is blue."}], user_id=test_user_id) # Use list of dict format
    logging.info("Memory added successfully.")

    # Test searching memory (This implicitly tests retrieval from stores)
    logging.info(f"Attempting to search memory for user: {test_user_id}")
    search_results = memory.search("What is my favorite color?", user_id=test_user_id)
    logging.info(f"Search results: {search_results}")

    # Test a simple chat interaction (if mem0 handles this directly or via LLM)
    # Note: mem0's primary focus is memory, chat might involve separate LLM calls
    # This part might need adjustment based on how mem0 integrates chat generation
    logging.info(f"Attempting a chat interaction for user: {test_user_id}")
    # Assuming mem0 might have a chat method or similar interaction pattern
    # If not, this demonstrates adding user/assistant turns using the correct format
    memory.add([{"role": "user", "content": "What is the capital of France?"}], user_id=test_user_id) # Use list of dict format
    # In a real app, you'd likely call the LLM here, possibly using mem0.search results
    # For this test, we'll just add a placeholder assistant response
    memory.add([{"role": "assistant", "content": "The capital of France is Paris."}], user_id=test_user_id) # Use list of dict format
    logging.info("Chat interaction simulated (added user/assistant messages).")

    # Removed final history call as it's not relevant for this connection test

    logging.info("--- Test Completed Successfully ---")

except Exception as e:
    logging.error(f"An error occurred during mem0 initialization or testing: {e}", exc_info=True)
    logging.error("--- Test Failed ---")

finally:
    # Optional: Clean up resources if necessary (e.g., close connections if not handled by mem0)
    logging.info("Test script finished.")
