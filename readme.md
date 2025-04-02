# mem0 Demo Project - Streamlit Chat

This project demonstrates the capabilities of the `mem0` library for AI memory management, integrating it with Google Gemini, Supabase (vector store), and Neo4j (graph store) within a Streamlit chat application.

## Features

*   Chat interface powered by Streamlit.
*   Conversation processing and memory management using `mem0`.
*   LLM integration with Google Gemini for understanding and response generation.
*   Vector memory storage via Supabase (pgvector).
*   Graph memory storage via Neo4j.
*   Persistence of memories within a single user session.

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
    *   *(Note: If `requirements.txt` is missing or outdated, you might need to install manually: `pip install "mem0ai[supabase,neo4j,gemini]" streamlit python-dotenv google-generativeai vecs langchain-neo4j rank-bm25`)*

4.  **Configure Environment Variables:**
    *   Create a file named `.env` in the project root directory (`u:/source/mem0-demo`).
    *   Add your credentials to the `.env` file. **Do not commit this file to Git.**
        ```dotenv
        # Gemini
        GOOGLE_API_KEY="your_google_ai_api_key"

        # Supabase
        SUPABASE_URL="your_supabase_project_url"
        SUPABASE_SERVICE_KEY="your_supabase_service_role_key"
        SUPABASE_CONNECTION_STRING="postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres" # Replace with your actual connection string
        # SUPABASE_TABLE_NAME="documents" # Optional: Specify if not default (default is 'documents')

        # Neo4j
        NEO4J_URI="your_neo4j_uri" # e.g., neo4j+s://instance.aura.net or bolt://localhost:7687
        NEO4J_USERNAME="your_neo4j_username" # default is often 'neo4j'
        NEO4J_PASSWORD="your_neo4j_password"

        # Optional: Specify embedding/LLM models if overriding mem0 defaults
        # EMBEDDING_MODEL="models/text-embedding-004"
        # EMBEDDING_MODEL_DIMS="768" # Or 1536 depending on Supabase setup
        # LLM_MODEL="gemini-1.5-flash-latest"
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
