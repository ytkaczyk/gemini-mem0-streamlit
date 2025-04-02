# mem0 Demo Project - Streamlit Chat

This project demonstrates the capabilities of the `mem0` library for AI memory management, integrating it with Google Gemini, Supabase (vector store), and Neo4j (graph store) within a Streamlit chat application.

## Features

*   Chat interface powered by Streamlit.
*   Conversation processing and memory management using `mem0`.
*   LLM integration with Google Gemini for understanding and response generation.
*   Vector memory storage via Supabase (pgvector).
*   Graph memory storage via Neo4j.
*   Persistence of memories within a single user session.
*   Sidebar displaying the LLM model in use and an option to clear the conversation UI.

## Setup Instructions

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd mem0-demo
    ```

2.  **Create and Activate Virtual Environment:**
    *   Ensure you have Python 3.x installed.
    *   Create a virtual environment:
        ```bash
        python -m venv venv
        ```
    *   Activate the environment:
        *   **Windows (cmd.exe):** `venv\Scripts\activate`
        *   **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
        *   **macOS/Linux:** `source venv/bin/activate`

3.  **Install Dependencies:**
    *   Install all required packages from `requirements.txt`:
        ```bash
        pip install -r requirements.txt
        ```
    *   *(This installs all necessary libraries including `mem0ai`, `streamlit`, `python-dotenv`, `google-generativeai`, and their dependencies specified in the file.)*

4.  **Configure Environment Variables:**
    *   Create a file named `.env` in the project root directory (where `app.py` is located).
    *   Add your credentials to the `.env` file. **Do not commit this file to Git.**
        ```dotenv
        # --- Gemini ---
        GOOGLE_API_KEY="your_google_ai_api_key"

        # --- Supabase ---
        SUPABASE_URL="your_supabase_project_url"
        SUPABASE_SERVICE_KEY="your_supabase_service_role_key"
        # Replace with your actual Supabase database connection string
        SUPABASE_CONNECTION_STRING="postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres"
        # Optional: Specify if not using the default table name 'documents'
        # SUPABASE_TABLE_NAME="your_custom_table_name"

        # --- Neo4j ---
        # e.g., neo4j+s://instance.aura.net or bolt://localhost:7687
        NEO4J_URI="your_neo4j_uri"
        # Default username is often 'neo4j'
        NEO4J_USERNAME="your_neo4j_username"
        NEO4J_PASSWORD="your_neo4j_password"

        # --- LLM / Embeddings ---
        LLM_MODEL="gemini-2.0-flash-001"
        EMBEDDING_MODEL="models/gemini-embedding-exp-03-07"
        # Ensure this matches the dimensions expected by your Supabase setup (e.g., 768 for text-embedding-004)
        EMBEDDING_MODEL_DIMS="1536"
        ```
    *   Ensure your Supabase database has the `vector` extension enabled.
    *   Ensure your Neo4j instance is running and accessible.

5.  **Run the Application:**
    *   Execute the following command in your terminal (with the virtual environment activated):
        ```bash
        streamlit run app.py
        ```
    *   The application should open in your default web browser.

## How it Works

1.  The Streamlit UI captures user input.
2.  The input is sent to the `mem0` client initialized in `app.py`.
3.  `mem0` uses its configured LLM (Gemini) and Embedder to process the input.
4.  Relevant information is stored as vectors in Supabase and as graph data in Neo4j.
5.  `mem0` searches these stores for relevant context based on the current input.
6.  The retrieved context and the user input are used by the LLM to generate a response.
7.  The response is displayed in the Streamlit UI.

*(This is an initial version. See `PLANNING.md` for more architectural details and `TASK.md` for development status.)*
