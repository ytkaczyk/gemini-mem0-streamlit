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

*   [x] **5.1: Update Planning & Task Docs:**
    *   [x] Update `PLANNING.md` scope, tech stack, considerations.
    *   [x] Add Phase 5 tasks to `TASK.md`.
*   [x] **5.2: Install Supabase Client:** (Completed April 3, 2025)
    *   [x] Add `supabase` to `requirements.txt` (Corrected package name).
    *   [x] Run `pip install -r requirements.txt`.
*   [x] **5.3: Add Supabase Auth Credentials:** (Completed April 3, 2025 - Code checks added)
    *   [x] Ensure `SUPABASE_URL` and `SUPABASE_ANON_KEY` are in `.env` (User responsibility, but code now requires them).
*   [x] **5.4: Implement Login UI:** (Completed April 3, 2025)
    *   [x] Create a function `show_login_form()` in `app.py`.
    *   [x] Use `st.text_input` for email and password.
    *   [x] Add "Login" and "Sign Up" buttons.
*   [x] **5.5: Implement Auth Logic:** (Completed April 3, 2025)
    *   [x] Initialize Supabase client (`create_client` from `supabase`).
    *   [x] Handle Login button click: Call `supabase.auth.sign_in_with_password()`. Store session in `st.session_state`.
    *   [x] Handle Sign Up button click: Call `supabase.auth.sign_up()`. Provide feedback to user (e.g., check email).
    *   [x] Add a "Logout" button (e.g., in sidebar) if a user session exists: Call `supabase.auth.sign_out()`. Clear session state.
*   [x] **5.6: Gate App Access:** (Completed April 3, 2025)
    *   [x] In `app.py`, check if `st.session_state.user_session` exists.
    *   [x] If not logged in, call `show_login_form()` and use `st.stop()` to prevent the main chat app from rendering.
    *   [x] If logged in, display the main chat interface.
*   [x] **5.7: Use Authenticated User ID for `mem0`:** (Completed April 3, 2025)
    *   [x] When logged in, extract the user ID from `st.session_state.user_session.user.id`.
    *   [x] Pass this user ID to `mem0.add()` and `mem0.search()` instead of the static ID.
*   [x] **5.8: Testing:** (User Action Required)
    *   [x] Test Sign Up flow.
    *   [x] Test Login flow.
    *   [x] Test Logout flow.
    *   [x] Verify chat history is associated with the logged-in user (requires checking `mem0` storage or observing behavior across logins).

## Phase 6: Streaming Response (April 7, 2025)

*   [x] **6.1: Implement Streaming Response:**
    *   [x] Modify the LLM (Gemini) call to stream the response.
    *   [x] Use `st.write_stream` to display the streaming response in the chat interface.

## Phase 7: Display token count (April 10, 2025)
    
*   [x] **7.1: Implement token count display:**     
    *   [x] Display 'Prompt token count', 'Response token count' and 'Total token count' ('Prompt token count' + 'Response token count') in the conversation section in the side panel for the current prompt.
    *   [x] Display cumulative values for 'Prompt token count', 'Response token count' and 'Total token count' for the entire conversation.
    *   [x] These values should be reset when the user clicks on 'Clear Conversation'.

## Further Enhancements
*   [x] Add a button to clear memory/session state.

## (Optional) Further Enhancements

*   [ ] Explore more advanced `mem0` search/query options.
*   [ ] Improve Streamlit UI (e.g., loading spinners).
*   [ ] Implement more robust error display to the user.


## Phase 8: Display Memories (April 11, 2025)

*   [x] **8.1: Update Planning & Task Docs:**
    *   [x] Update `PLANNING.md` scope, architecture. (Completed)
    *   [x] Add Phase 8 tasks to `TASK.md`. (Completed)
*   [x] **8.2: Create `pages` Directory:** (Completed April 11, 2025)
    *   [x] Create a directory named `pages` in the project root.
*   [x] **8.3: Create `pages/1_Chat.py`:** (Completed April 11, 2025)
    *   [x] Create the file `pages/1_Chat.py`.
    *   [x] Move the core chat interface logic (UI elements, message handling, `mem0` interaction, token display) from `app.py` to this file.
    *   [x] Adapt imports and ensure necessary initializations (e.g., `mem0` client, potentially Supabase client if needed locally) are present or correctly accessed from session state/global scope.
    *   [x] Verify that session state variables (`messages`, `user_session`, token counts) are accessed correctly within the page context.
    *   [x] Ensure the authentication check (is user logged in?) is performed at the beginning of this page's logic.
*   [x] **8.4: Create `pages/2_Memory.py`:** (Completed April 11, 2025)
    *   [x] Create the file `pages/2_Memory.py`.
    *   [x] Add necessary imports (`streamlit`, `mem0`, `os`, `load_dotenv`, `supabase`).
    *   [x] Add logic to initialize the `mem0` client (consider sharing via a utility function or session state if feasible).
    *   [x] Implement the authentication check (is user logged in?). If not, display a message and stop.
    *   [x] If logged in, retrieve the `user_id` from `st.session_state.user_session`.
    *   [x] Use `memory_client.get_all(user_id=user_id)` to fetch all memories for the user. (Note: Check `mem0` documentation for the exact method, especially if using async).
    *   [x] Add a title like "Your Memories".
*   [x] **8.5: Refactor `app.py` (Main Entry Point):** (Completed April 11, 2025)
    *   [x] Remove the chat-specific UI and logic.
    *   [x] Keep essential global setup: `st.set_page_config`, `load_dotenv`.
    *   [x] Keep/Refine the Supabase client initialization and the login/logout form logic (`show_login_form`, auth handling). This should likely remain in `app.py` to gate access before page navigation.
    *   [x] Ensure the login check (`if 'user_session' not in st.session_state...`) happens *before* attempting to render any page content or navigation.
    *   [x] Define the pages using `st.Page`:
        ```python
        # Example structure in app.py after auth check
        if st.session_state.user_session:
            pg = st.navigation(
                [
                    st.Page("pages/1_Chat.py", title="Chat", icon=":speech_balloon:"),
                    st.Page("pages/2_Memory.py", title="Memory", icon=":brain:"),
                ]
            )
            # Add logout button logic here (e.g., in sidebar)
            # ... sidebar logout button ...
            pg.run() # Render the selected page
        else:
            show_login_form() # Show login if not authenticated
        ```
    *   [x] Move the sidebar elements (logout button, potentially token counts if they become global/summary) to be defined within the `if st.session_state.user_session:` block in `app.py` so they appear consistently across pages.
*   [ ] **8.6: Display tabular memories
    *   [ ] Display the retrieved memories using `st.write`, `st.dataframe`, or `st.json`. Handle the case where no memories are found.
*   [ ] **8.7: Display graph memories
    *   [ ] Add 'graph' tabs
    *   [ ] Display graph 
*   [ ] **8.8: Testing:** (User Action Required)
    *   [ ] Run `streamlit run app.py`.
    *   [ ] Test logging in and out.
    *   [ ] Test navigating between the "Chat" and "Memory" pages using the sidebar.
    *   [ ] Verify chat functionality works as before on the "Chat" page.
    *   [ ] Verify memories are displayed correctly on the "Memory" page for the logged-in user.
    *   [ ] Test adding new memories in chat and seeing them appear on the "Memory" page after refresh/navigation.
    *   [ ] Ensure session state (chat history, token counts) persists correctly when switching pages.
    *   [ ] Confirm logout works from any page and returns to the login screen.
