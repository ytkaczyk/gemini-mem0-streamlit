# TASK LIST - mem0 Demo Project

**Last Updated:** March 31, 2025

This document outlines the initial tasks required to get the Minimum Viable Product (MVP) of the `mem0` demo project running.

## Phase 1: Setup & Configuration (Prerequisites) - COMPLETED

*   [x] **1.1: Project Setup:**
    *   [x] Use current directory (U:\source\mem0-demo).
    *   [x] Initialize a Git repository (`git init`).
    *   [x] Create a `.gitignore` file (include `venv/`, `__pycache__/`, `.env`, etc.).
    *   [x] Create a basic `README.md`.
*   [x] **1.2: Python Environment:**
    *   [x] Set up a virtual environment (e.g., `python -m venv venv`).
    *   [x] Activate the virtual environment (`source venv/bin/activate` or `venv\Scripts\activate`).
*   [x] **1.3: Install Dependencies:**
    *   [x] Install core libraries: `pip install "mem0ai[supabase,neo4j,gemini]"` (plus `vecs`, `langchain-neo4j`, `rank-bm25`)
    *   [x] Install Streamlit: `pip install streamlit`
    *   [x] Install environment variable handler: `pip install python-dotenv`
    *   [x] Install Gemini client (optional, if direct calls needed): `pip install google-generativeai`
    *   [x] Create `requirements.txt`: `pip freeze > requirements.txt`.
*   [x] **1.4: Environment Configuration:**
    *   [x] Create a `.env` file in the project root.
    *   [x] Add credentials to `.env`:
        ```dotenv
        # Gemini
        GOOGLE_API_KEY="your_google_ai_api_key"

        # Supabase
        SUPABASE_URL="your_supabase_project_url"
        SUPABASE_SERVICE_KEY="your_supabase_service_role_key"
        SUPABASE_CONNECTION_STRING="your_supabase_connection_string" # Added during setup
        # SUPABASE_TABLE_NAME="documents" # Optional: Specify if not default

        # Neo4j
        NEO4J_URI="your_neo4j_uri" # e.g., neo4j+s://instance.aura.net or bolt://localhost:7687
        NEO4J_USERNAME="your_neo4j_username" # default is often 'neo4j'
        NEO4J_PASSWORD="your_neo4j_password"

        # Optional: Specify embedding/LLM models if overriding mem0 defaults
        # EMBEDDING_MODEL="models/text-embedding-004"
        # EMBEDDING_MODEL_DIMS="768" # Or 1536 depending on Supabase setup
        # LLM_MODEL="gemini-1.5-flash-latest"
        ```
    *   [x] **Ensure `.env` is listed in `.gitignore`**.

## Phase 2: Core `mem0` Integration - COMPLETED

*   [x] **2.1: Basic `mem0` Initialization Script:**
    *   [x] Create a test script (e.g., `test_mem0.py`).
    *   [x] Import `os`, `Memory` from `mem0`, and `load_dotenv`.
    *   [x] Load environment variables using `load_dotenv()`.
    *   [x] Create the `mem0` configuration dictionary, pulling values from `os.environ`. Ensure providers ('supabase', 'neo4j', 'gemini') and nested configs are correctly structured per `mem0` docs.
    *   [x] Initialize `mem0`: `memory = Memory.from_config(config)`.
    *   [x] Test basic `memory.add()` with a simple message and `user_id`.
    *   [x] Test basic `memory.search()`.
    *   [x] Print results to verify connections work. Debug connection/config issues.

## Phase 3: Streamlit Frontend Development

*   [ ] **3.1: Create Streamlit App File:**
    *   [ ] Create `app.py`.
    *   [ ] Import `streamlit as st`, `os`, `Memory` from `mem0`, `load_dotenv`.
*   [ ] **3.2: Initialize `mem0` in App:**
    *   [ ] Load environment variables.
    *   [ ] Define/load the `mem0` configuration dictionary.
    *   [ ] Initialize the `mem0` client: `memory = Memory.from_config(config)`. Handle potential initialization errors.
*   [ ] **3.3: Basic Chat UI:**
    *   [ ] Set page title: `st.set_page_config(page_title="mem0 Demo Chat")`.
    *   [ ] Add a title: `st.title("Chat with mem0")`.
    *   [ ] Initialize chat history in `st.session_state` if it doesn't exist (e.g., `st.session_state.messages = []`).
    *   [ ] Display existing messages from `st.session_state.messages` using `st.chat_message`.
*   [ ] **3.4: Chat Input Handling:**
    *   [ ] Add chat input widget: `prompt = st.chat_input("What's up?")`.
    *   [ ] If `prompt` is received:
        *   [ ] Add user message to `st.session_state.messages`.
        *   [ ] Display user message using `st.chat_message("user")`.
*   [ ] **3.5: Integrate `mem0` Processing:**
    *   [ ] Inside the `if prompt:` block:
        *   [ ] Assign a consistent `user_id` for the session (e.g., `user_id="streamlit_session_user"`).
        *   [ ] Use `mem0.chat()` to handle processing and response generation.
        *   [ ] Display assistant's response using `st.chat_message("assistant")`.
        *   [ ] Add assistant response to `st.session_state.messages`.

## Phase 4: Refinement & Testing

*   [ ] **4.1: Basic Error Handling:**
    *   [ ] Add `try...except` blocks around `mem0` calls and external service interactions. Log basic errors to the console or Streamlit interface. (Included in app.py)
*   [ ] **4.2: End-to-End Testing:**
    *   [ ] Run the Streamlit app: `streamlit run app.py`.
    *   [ ] Engage in a short conversation, testing if the AI remembers previously mentioned information (e.g., "My name is Bob", later ask "What is my name?").
    *   [ ] Check Supabase and Neo4j (if possible via their respective UIs/dashboards) to see if data is being stored. (Manual check - assumed done by user)
*   [x] **4.3: Code Cleanup & Readme:**
    *   [ ] Add comments to `app.py`.
    *   [ ] Update `README.md` with setup instructions (install deps, set up `.env`, run app) and a brief description.

## (Optional) Phase 5: Enhancements

*   [ ] Explore more advanced `mem0` search/query options.
*   [ ] Improve Streamlit UI (e.g., loading spinners).
*   [ ] Add a button to clear memory/session state.
*   [ ] Implement more robust error display to the user.
