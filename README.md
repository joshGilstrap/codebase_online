# Cloud Codebase Teacher: RAG Agent

Cloud Codebase Teacher is a serverless RAG (Retrieval-Augmented Generation) application designed to analyze codebases in the cloud.

Unlike local-only tools, this version is architected for Streamlit Community Cloud. It replaces local GPU inference with the Groq API (Llama 3 70B) and replaces local file paths with Zip File Ingestion, allowing it to run entirely in a browser environment without accessing the user's local file system.

## Demo

<img width="1848" height="724" alt="Screenshot 2025-11-28 101608" src="https://github.com/user-attachments/assets/592048cc-92b8-4626-9706-e0e4cec009b6" />

## Key Features

Cloud Native: Runs entirely on Streamlit Community Cloud (no local GPU required).

Fast Inference: Uses Groq to serve Llama 3-8B/70B at lightning speeds (~300 tokens/sec).

Zip Ingestion: Users upload a ```.zip``` of their project; the app extracts, filters, and processes code in a temporary cloud directory.

Language-Aware Chunking: Uses ```RecursiveCharacterTextSplitter``` optimized for Python to preserve class/function structure.

Ephemeral Vector Store: Uses FAISS in memory to index code on the fly without requiring a persistent vector database.

## Tech Stack

App Framework: Streamlit

LLM Orchestration: LangChain

Inference Engine: Groq API (Llama 3)

Vector Store: FAISS (CPU)

Embeddings: HuggingFace (```all-MiniLM-L6-v2```)

Data Processing: ```zipfile``` + ```tempfile``` for secure file handling.

## Architecture
```
graph LR
    A[User Uploads .zip] -->|Extract| B(Temp Directory)
    B -->|Filter venv/git| C(TextLoader)
    C -->|Split| D(HuggingFace Embeddings)
    D -->|Vectors| E[(FAISS RAM Index)]
    F[User Question] -->|Retrieve| E
    E -->|Context| G[Groq API (Llama 3)]
    G -->|Answer| H[Streamlit UI]
```


## Installation & Local Setup

1. Prerequisites

Python 3.10+ installed.

Groq API Key (Get one for free at console.groq.com).

2. Clone & Install
```
git clone [https://github.com/joshgilstrap/codebase-online.git](https://github.com/joshgilstrap/codebase-online.git)
cd codebase-online

# Create Virtual Environment
python -m venv venv

# Activate Environment
# Windows:
venv\Scripts\activate 
# Mac/Linux:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

3. Configure Secrets

Create a folder named .streamlit and a file inside named secrets.toml:
```
# .streamlit/secrets.toml
GROQ_API_KEY = "gsk_..."
```

(Alternatively, you can enter the key manually in the App Sidebar).

4. Run the App
```
streamlit run app.py
```

## How It Works

Ingestion: The user uploads a compressed ```.zip``` file of their codebase. The app uses Python's ```tempfile``` library to create a secure, temporary directory and extracts the files there.

Filtering: The crawler walks through the temporary folder, ignoring system directories like ```node_modules```, ```venv```, and ```.git``` to ensure only relevant source code (```.py```, ```.js```, ```.md```) is processed.

Embedding: Code is split into chunks using ```RecursiveCharacterTextSplitter``` (Python-optimized). These chunks are embedded using ```all-MiniLM-L6-v2``` running on the cloud CPU.

Retrieval: When a user asks a question, FAISS performs a similarity search to find the relevant code blocks.

Generation: The retrieved context is sent to Groq (Llama 3) via API. Because Groq is optimized for speed, the "Think" time is almost instantaneous compared to local inference.

## Deployment Guide

This app is ready for Streamlit Community Cloud:

Push this code to a GitHub repository.

Log in to share.streamlit.io.

Connect your repo and click Deploy.

In the Streamlit Dashboard, go to Settings -> Secrets and add your API key:
```
GROQ_API_KEY = "gsk_your_key_here"
```

## Troubleshooting

"No module named..." errors:
Ensure your ```requirements.txt``` contains ```langchain-groq``` and ```faiss-cpu```. The cloud environment uses Linux, so do not use ```faiss-gpu``` or windows-specific binaries.

Zip File Issues:
Ensure your zip file is a standard archive. If the app says "0 files found," check that your code isn't nested inside a folder inside the zip (e.g., ```my-project/my-project/main.py```).

API Limits:
Groq free tier limits if you hit a rate limit, wait a minute and try again.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
