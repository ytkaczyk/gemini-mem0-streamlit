# TASK LIST - mem0 Demo Project

**Last Updated:** April 2, 2025 (PM)

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

## Phase 3: Streamlit Frontend Development - COMPLETED

*   [x] **3.1: Create Streamlit App File:**
    *   [x] Create `app.py`.
    *   [x] Import `streamlit as st`, `os`, `Memory` from `mem0`, `load_dotenv`.
*   [x] **3.2: Initialize `mem0` in App:**
    *   [x] Load environment variables.
    *   [x] Define/load the `mem0` configuration dictionary.
    *   [x] Initialize the `mem0` client: `memory = Memory.from_config(config)`. Handle potential initialization errors.
*   [x] **3.3: Basic Chat UI:**
    *   [x] Set page title: `st.set_page_config(page_title="mem0 Demo Chat")`.
    *   [x] Add a title: `st.title("Chat with mem0")`.
    *   [x] Initialize chat history in `st.session_state` if it doesn't exist (e.g., `st.session_state.messages = []`).
    *   [x] Display existing messages from `st.session_state.messages` using `st.chat_message`.
*   [x] **3.4: Chat Input Handling:**
    *   [x] Add chat input widget: `prompt = st.chat_input("What's up?")`.
    *   [x] If `prompt` is received:
        *   [x] Add user message to `st.session_state.messages`.
        *   [x] Display user message using `st.chat_message("user")`.
*   [x] **3.5: Integrate `mem0` Processing:**
    *   [x] Inside the `if prompt:` block:
        *   [x] Assign a consistent `user_id` for the session (e.g., `user_id="streamlit_session_user"`).
        *   [x] Use `mem0.chat()` to handle processing and response generation. (Note: Direct LLM call used instead as per implementation)
        *   [x] Use `mem0.search()` to retrieve relevant context.
        *   [x] Construct a prompt for the LLM (Gemini) using the context.
        *   [x] Call the LLM API directly to generate the response.
        *   [x] Use `mem0.add()` to store the user message and assistant response.
        *   [x] Display assistant's response using `st.chat_message("assistant")`.
        *   [x] Add assistant response to `st.session_state.messages`.

## Phase 4: Refinement & Testing

*   [x] **4.1: Basic Error Handling:**
    *   [x] Add `try...except` blocks around `mem0` calls and external service interactions. Log basic errors to the console or Streamlit interface. (Improved in recent update)
*   [x] **4.2: End-to-End Testing:**
    *   [x] Run the Streamlit app: `streamlit run app.py`.
    *   [x] Engage in a short conversation, testing if the AI remembers previously mentioned information (e.g., "My name is Bob", later ask "What is my name?").
    *   [x] Check Supabase and Neo4j (if possible via their respective UIs/dashboards) to see if data is being stored. (Manual check - assumed done by user)
*   [x] **4.3: Code Cleanup & Readme:** - COMPLETED
    *   [x] Add comments to `app.py`.
    *   [x] Update `README.md` with setup instructions (install deps, set up `.env`, run app) and a brief description.

## Discovered During Work (April 2, 2025)

*   [x] **Fix `IndexError` in `app.py`:** Added specific `try...except IndexError` around `memory_client.search()` call (line ~158) to handle cases where the Gemini API might return an empty/blocked response during the search process, preventing the app from crashing.
*   [x] **Add Console Log for Model:** Added `logging.info` call in `app.py` to display the used Gemini model name on startup.
*   [x] **Add Streamlit Sidebar:** Implemented `st.sidebar` in `app.py`.
*   [x] **Display Model in Sidebar:** Added model name display (`st.sidebar.markdown`, `st.sidebar.code`) to the sidebar.
*   [x] **Add Clear Conversation Button:** Added a button (`st.sidebar.button`) to the sidebar to clear the session state message history (`st.session_state.messages`).
*   [x] **Organize Sidebar:** Added section header (`st.sidebar.subheader`) and divider (`st.sidebar.divider`) for the clear button.
*   [x] **Expand Clear Button:** Made the "Clear Conversation" button full width (`use_container_width=True`).

## Phase 5: User Authentication (April 2, 2025)

*   [ ] **5.1: Update Planning & Task Docs:**
    *   [x] Update `PLANNING.md` scope, tech stack, considerations.
    *   [x] Add Phase 5 tasks to `TASK.md`.
*   [ ] **5.2: Install Supabase Client:**
    *   [ ] Add `supabase-py` to `requirements.txt`.
    *   [ ] Run `pip install -r requirements.txt`.
*   [ ] **5.3: Add Supabase Auth Credentials:**
    *   [ ] Ensure `SUPABASE_URL` and `SUPABASE_ANON_KEY` are in `.env` (Anon key is typically used for client-side auth).
*   [ ] **5.4: Implement Login UI:**
    *   [ ] Create a function `show_login_form()` in `app.py`.
    *   [ ] Use `st.text_input` for email and password.
    *   [ ] Add "Login" and "Sign Up" buttons.
*   [ ] **5.5: Implement Auth Logic:**
    *   [ ] Initialize Supabase client (`create_client` from `supabase`).
    *   [ ] Handle Login button click: Call `supabase.auth.sign_in_with_password()`. Store session in `st.session_state`.
    *   [ ] Handle Sign Up button click: Call `supabase.auth.sign_up()`. Provide feedback to user (e.g., check email).
    *   [ ] Add a "Logout" button (e.g., in sidebar) if a user session exists: Call `supabase.auth.sign_out()`. Clear session state.
*   [ ] **5.6: Gate App Access:**
    *   [ ] In `app.py`, check if `st.session_state.user_session` exists.
    *   [ ] If not logged in, call `show_login_form()` and use `st.stop()` to prevent the main chat app from rendering.
    *   [ ] If logged in, display the main chat interface.
*   [ ] **5.7: Use Authenticated User ID for `mem0`:**
    *   [ ] When logged in, extract the user ID from `st.session_state.user_session.user.id`.
    *   [ ] Pass this user ID to `mem0.add()` and `mem0.search()` instead of the static ID.
*   [ ] **5.8: Testing:**
    *   [ ] Test Sign Up flow.
    *   [ ] Test Login flow.
    *   [ ] Test Logout flow.
    *   [ ] Verify chat history is associated with the logged-in user (requires checking `mem0` storage or observing behavior across logins).

## (Optional) Further Enhancements

*   [ ] Explore more advanced `mem0` search/query options.
*   [ ] Improve Streamlit UI (e.g., loading spinners).
*   [ ] Add a button to clear memory/session state.
*   [ ] Implement more robust error display to the user.
