# LangGraph Support Agent

**Overview**
A full-stack AI-powered customer support application designed to automate ticket resolution and feedback analysis. It leverages **LangGraph** to orchestrate intelligent agent workflows, enabling the system to handle complex user queries with stateful interactions and memory.

**Key Features**
*   **AI Support Agent**: Capable of understanding and resolving customer tickets using large language models (via OpenRouter).
*   **Ticket Lifecycle Management**: automated workflows for creating, tracking, and processing support tickets.
*   **Feedback System**: Integrated feedback collection to continuously improve agent performance.
*   **Real-time Interaction**: A responsive React frontend for seamless user communication with the agent.

**Tech Stack**
*   **Frontend**: React (Vite), CSS Modules, Lucide React
*   **Backend**: FastAPI, LangChain, LangGraph, PostgreSQL, SQLAlchemy
*   **Infrastructure**: Docker & Docker Compose for easy deployment

## Getting Started

### Prerequisites
- Node.js & npm
- Python 3.10+
- Docker & Docker Compose (optional but recommended)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/neshmo/Langgraph-Support-Agent.git
    cd Langgraph-Support-Agent
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    # Create .env file with your API keys (OPENROUTER_API_KEY, etc.)
    cp .env.example .env
    
    # Run with Docker
    docker-compose up --build
    
    # OR Run Locally
    python -m venv env
    .\env\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```

3.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

The frontend will start at `http://localhost:5173` and the backend at `http://localhost:8000`.
