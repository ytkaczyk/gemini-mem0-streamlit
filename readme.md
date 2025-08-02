# mem0 Demo Project - Streamlit Chat

This project demonstrates the capabilities of the `mem0` library for AI memory management, integrating it with Google Gemini, Supabase (vector store), and Neo4j (graph store) within a Streamlit chat application.

## Features

*   Chat interface powered by Streamlit.
*   Conversation processing and memory management using `mem0`.
*   LLM integration with Google Gemini for understanding and response generation.
*   Vector memory storage via Supabase (pgvector).
*   Graph memory storage via Neo4j.
*   Persistence of memories witfor each user across sessions.
*   User authentication using Supabase Auth.
*   Display prompt, Response and Total tokens count for the current prompt and conversation.
*   Sidebar displaying the LLM model in use and an option to clear the conversation UI.

## Prerequisite
1.  Python 
2.  **Optional: Install `uv` for dependency management**
    `uv` is a fast Python package installer and resolver, written in Rust.
    To check if `uv` is already installed, run:
    ```bash
    uv --version
    ```
    If `uv` is not found, you can install it using pip:
    ```bash
    pip install uv
    ```


## Setup Instructions

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone https://github.com/ytkaczyk/gemini-mem0-streamlit.git
    cd gemini-mem0-streamlit
    ```

2.  **Install Dependencies:**
    *   Install all required packages using `uv sync`:
        ```bash
        uv sync
        ```
    *   *(This installs all necessary libraries including `mem0ai`, `streamlit`, `python-dotenv`, `google-generativeai`, and their dependencies specified in the `uv.lock` file.)*

3.  **Get Google Gemini API Key:**
    *   Obtain a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

4.  **Setup Supabase:**
    *   Sign up for a free Supabase account at [https://supabase.com/](https://supabase.com/).
    *   Create a new project.
    *   Navigate to "Project Settings" -> "API" to find your `SUPABASE_URL` and `SUPABASE_ANON_KEY`.
    *   Go to "Database" -> "Connection String" to get your `SUPABASE_CONNECTION_STRING`. Ensure you use the "URI" format.
    *   Enable the `vector` extension in your Supabase database:
        *   Go to "Database" -> "Extensions" and search for "vector".
        *   Toggle it on.

5.  **Setup Neo4j:**
    *   Sign up for a free Neo4j AuraDB account at [https://neo4j.com/cloud/aura/](https://neo4j.com/cloud/aura/).
    *   Create a new Neo4j instance (a free tier is available).
    *   Once your instance is created, download the connection details (usually a `.txt` file). This file will contain your `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD`.

6.  **Configure Environment Variables:**
    *   Copy `.example.env` to `.env` in the project root directory (where `app.py` is located).
    *   Add the credentials from the previous steps to the `.env` file. **Never commit this file to Git.**
        ```dotenv
        # Gemini config
        # Obtain a key at https://aistudio.google.com/app/apikey
        GOOGLE_API_KEY="<your api key>"
        # llm and embedding model
        # Model list at https://ai.google.dev/gemini-api/docs/models
        LLM_MODEL="gemini-2.0-flash"
        # Embedding model list at https://ai.google.dev/gemini-api/docs/models#gemini-embedding and https://ai.google.dev/gemini-api/docs/models#text-embedding
        EMBEDDING_MODEL="models/gemini-embedding-001"
        EMBEDDING_MODEL_DIMS=1536

        # Neo4j config
        # Sign up for a free account at https://supabase.com/ or self host
        SUPABASE_URL="https://<supabase project ID>.supabase.co"
        SUPABASE_ANON_KEY="<your anon key>"
        SUPABASE_TABLE_NAME="mem0_memories"
        SUPABASE_CONNECTION_STRING="<database connection string>"

        # Neo4j config
        # Sign up for a free Neo4j AuraDB account at https://neo4j.com/product/auradb/ or self host. 
        NEO4J_URI="neo4j+s://<neo4j aura project ID>>.databases.neo4j.io" 
        NEO4J_USERNAME="<usually neo4j>"
        NEO4J_PASSWORD="<your neo4j password>"
        ```
    *   Ensure your Supabase database has the `vector` extension enabled.
    *   Ensure your Neo4j instance is running and accessible.

7.  **Run the Application:**
    *   Execute the following command in your terminal (with the virtual environment activated):
        ```bash
        streamlit run app.py
        ```
    *   The application should open in your default web browser.

## How it Works

*See [PLANNING.md](planning.md) for more architectural details and [TASK.md](task.md) for development status.*
