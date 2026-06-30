# 🧠 RepoMind — AI-Powered GitHub Repo Explorer

**Live Demo:** [Click here to view the app](https://github-explorer-bl8d.vercel.app/)

RepoMind is a sleek, intelligent repository explorer that allows developers to paste any public GitHub repository URL and instantly analyze its architecture, file structures, and code logic using AI. Built with a pristine, high-contrast light workspace for ultimate code readability.

<p align="center">
  <img src="./assets/Screenshot 2026-06-23 120719.png" alt="RepoMind Dashboard Preview" width="100%">
</p>


---

## 🎯 System Architecture & Data Flow

RepoMind seamlessly ingests, embeds, searches, and reasons over remote codebases. Here is the underlying architecture map showing how user queries are processed through embeddings, vector stores, and LLM orchestration layers:

<p align="center">
  <img src="./assets/Screenshot 2026-06-23 121117.png" alt="RepoMind System Flow Diagram" width="85%">
</p>

---

## ✨ Features

* **Instant Repository Indexing:** Input a public GitHub URL to quickly map and parse project files.
* **AI-Driven Code Analytics:** Ask deep contextual questions ("How does data flow?", "What are the core design patterns?").
* **Dynamic Structural Overview:** Compiles directory trees and provides structural file role breakdowns cleanly.
* **Trace-Enabled Observability:** Backed by LangSmith telemetry for reliable, optimized vector chunk retrievals.

---

## 📸 Core Walkthrough

### 1. Welcome & Entry Point
When launching RepoMind, you are presented with a clean, distraction-free empty state prompting you to input a public GitHub repository path.

<p align="center">
  <img src="./assets/Screenshot 2026-06-23 121249.png" alt="Empty Landing State" width="90%">
</p>

### 2. Live Vector Indexing
Once you hit analyze, RepoMind chunk-parses up to 150 project files, passes them through embedding models, and caches them to a local vector space.

<p align="center">
  <img src="./assets/Screenshot 2026-06-23 120623.png" alt="Indexing Modal State" width="50%">
</p>

### 3. Smart Code Mapping & Question Answering
Once indexed, the assistant gives a high-level review of what the repository does and opens a conversational chat panel where file architectures are dynamically visualized.

<p align="center">
  <img src="./assets/Screenshot 2026-06-23 120738.png" alt="Structural Analysis Interaction" width="90%">
</p>

---

## 🛠️ Tech Stack

* **Frontend:** React (v18+) & Vite
* **Styling:** Custom Light CSS Variables & Tailwind CSS
* **Core Agent Logic:** Python (LangChain / Custom RAG Orchestrator)
* **Embeddings:** Gemini `embedding-001`
* **Vector Index:** FAISS Vector Store (Cosine Similarity Tracking)
* **Inference LLM:** Groq API Cloud (`Llama-3.3-70b-versatile`)
* **Telemetry:** LangSmith Tracing Cloud

---

## 📦 Local Installation & Setup

Follow these precise sequential steps to configure and run both the AI engine backend and your user interface dashboard side-by-side.

### 1. Global Project Initialization

Clone the parent workspace repository and establish your target system configuration parameters file:

```bash
git clone https://github.com/himanshi20084/Todo-list-website.git GITHUBEXPLORER
cd GITHUBEXPLORER
touch .env
```

Open the `.env` file and supply your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key_here
```

### 2. Backend Engine Server Setup

Navigate to the backend, create a virtual environment, and start the server:

```bash
cd backend
python -m venv venv

# For Windows Shell:
.\venv\Scripts\activate

# For Linux / MacOS Environments:
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

---

## 📂 Project Structure

```
GITHUBEXPLORER/
├── assets/                 # Storage framework for system interface walkthrough images
├── backend/
│   ├── agent.py            # Natural language processing orchestration module
│   ├── app.py              # Server network endpoints initialization routing controller
│   ├── embedder.py         # Code structural context token vectorization engine via Gemini
│   ├── fetcher.py          # GitHub raw file extraction engine framework mechanics
│   ├── vector_store.py     # Clean FAISS index storage matrix data manager system
│   └── requirements.txt    # Mandatory operational Python dependency tracking map
├── frontend/
│   ├── index.html          # Main application skeleton template structure shell
│   ├── tailwind.config.js  # Framework styling configuration parameters script rules
│   ├── package.json        # Node component tracking registry and build operational commands
│   └── src/
│       ├── main.jsx        # Structural React DOM portal engine mounting initializer
│       ├── App.jsx         # Component container rendering block template
│       └── style.css       # Deep customized ergonomic light scheme structural variables
├── .env                    # System global infrastructure key vector token configuration file
└── README.md               # Product installation manuals and platform operational maps
```
