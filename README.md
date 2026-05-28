---

title: InForge AI Backend
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
-------------

# 🚀 INFORGE-AI

> Autonomous Multi-Agent AI Analytics Platform

INFORGE-AI is an enterprise-grade autonomous AI analytics system that transforms raw datasets into actionable business intelligence using a coordinated multi-agent pipeline powered by Large Language Models (LLMs), machine learning, and real-time analytics.

Users simply upload a CSV or Excel dataset, and the platform automatically performs:

* Data ingestion
* Data cleaning
* Exploratory Data Analysis (EDA)
* Visualization generation
* Machine learning benchmarking
* Business insight synthesis
* Python code generation
* Conversational Q&A

All with zero manual intervention.

---

# ✨ Features

* 🤖 8-Agent Autonomous AI Pipeline
* 📊 Automated EDA & Visualization
* 🧠 Multi-LLM Architecture (Gemini, Groq, Nemotron)
* ⚡ Real-Time WebSocket Streaming
* 📈 Auto ML Task Detection
* 📄 PDF Report Export
* 🐍 Python Code Generation
* 💬 Interactive AI Chat Assistant
* 🎨 Premium Glassmorphism UI
* 🚀 FastAPI + React + Vite Architecture
* 🔄 End-to-End Automated Analytics

---

# 🧠 Autonomous Agent Pipeline

| Step | Agent               | Purpose                              |
| ---- | ------------------- | ------------------------------------ |
| 1    | Ingestion Agent     | Dataset schema & metadata analysis   |
| 2    | Cleaning Agent      | Handle nulls, duplicates, outliers   |
| 3    | EDA Agent           | Statistical analysis & correlations  |
| 4    | Visualization Agent | Generate optimized charts            |
| 5    | ML Agent            | Train & benchmark ML models          |
| 6    | Insights Agent      | Business intelligence synthesis      |
| 7    | Code Agent          | Generate reproducible Python scripts |
| 8    | Chat Agent          | Interactive contextual Q&A           |

---

# 🏗️ System Architecture

```text
Frontend (React + Vite)
        ↓
WebSocket + REST API
        ↓
FastAPI Backend
        ↓
Multi-Agent Orchestrator
        ↓
LLMs + ML Models + Analytics Engine
```

---

# ⚙️ Tech Stack

## Backend

* FastAPI
* Uvicorn
* AsyncIO
* WebSockets
* Pandas
* NumPy
* Scikit-learn
* XGBoost
* Matplotlib
* Seaborn
* ReportLab

## AI Models

| Model                 | Purpose                 |
| --------------------- | ----------------------- |
| Gemini 2.0 Flash Lite | Visualization reasoning |
| Groq Llama-3.3-70B    | Insights & synthesis    |
| Nemotron Models       | Schema & data analysis  |

## Frontend

* React 19
* Vite
* Tailwind CSS 4
* Framer Motion
* Recharts
* Lucide React

---

# 📂 Project Structure

```bash
INFORGE-AI/
│
├── backend/
│   ├── agents/
│   ├── services/
│   ├── routes/
│   ├── websocket/
│   ├── exports/
│   ├── app.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   └── hooks/
│   ├── public/
│   └── package.json
│
├── Dockerfile
├── README.md
└── docker-compose.yml
```

---

# 📡 API Endpoints

| Endpoint                    | Method    | Description                      |
| --------------------------- | --------- | -------------------------------- |
| `/upload`                   | POST      | Upload CSV/Excel dataset         |
| `/ws/{session_id}`          | WebSocket | Real-time progress updates       |
| `/results/{session_id}`     | GET       | Retrieve complete analysis       |
| `/chat/{session_id}`        | POST      | Ask questions about analysis     |
| `/export/pdf/{session_id}`  | GET       | Download PDF report              |
| `/export/code/{session_id}` | GET       | Download generated Python script |
| `/docs`                     | GET       | Swagger API documentation        |

---

# 📊 Machine Learning Capabilities

INFORGE-AI automatically detects the appropriate ML task.

## Classification Models

* Logistic Regression
* Random Forest
* XGBoost
* KNN

## Regression Models

* Linear Regression
* Ridge Regression
* Random Forest Regressor
* XGBoost Regressor

## Clustering Models

* KMeans
* DBSCAN

---

# 🔄 Real-Time Streaming

The platform uses WebSockets for live agent updates.

```text
ws://localhost:8000/ws/{session_id}
```

Features include:

* Live progress updates
* Step-by-step pipeline tracking
* Real-time UI synchronization
* Progress replay support

---

# 🚀 Local Development Setup

## 1. Clone Repository

```bash
git clone https://github.com/vinayak533/InForge-AI.git
cd InForge-AI
```

---

## 2. Backend Setup

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate

pip install -r requirements.txt

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at:

```text
http://localhost:8000
```

---

## 3. Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

# 🌐 Deployment

## Frontend Deployment

* Vercel

## Backend Deployment

* Hugging Face Spaces (Docker)
* Railway
* Render
* AWS EC2

---

# 🔐 Environment Variables

Create a `.env` file inside `backend/`

```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
OPENROUTER_API_KEY=your_key
```

---

# 📄 Export Features

* PDF business reports
* Cleaned CSV datasets
* Generated Python analysis scripts

---

# 🎨 UI Highlights

* Dark premium theme
* Glassmorphism interface
* Animated transitions
* Interactive dashboards
* Real-time progress indicators

---

# ⚠️ Production Recommendations

Current implementation uses in-memory session storage suitable for demos and prototypes.

For production deployments:

* PostgreSQL / MongoDB
* JWT Authentication
* API Rate Limiting
* Redis Caching
* Secure Secret Management
* Centralized Logging
* Retry & Recovery Systems
* Kubernetes / Docker Scaling

---

# 📌 Future Improvements

* Multi-user collaboration
* Fine-tuned domain-specific models
* Auto dashboard generation
* AI-powered forecasting
* Cloud warehouse integration
* Scheduled analytics workflows

---

# 👨‍💻 Author

**Vinayak K V**

Data Science & AI Engineer

### Specializations

* Machine Learning
* Generative AI
* LLM Engineering
* Multi-Agent Systems
* Full-Stack AI Applications

GitHub: https://github.com/vinayak533

---

# 📜 License

This project is licensed under the MIT License.

---

# ⭐ Acknowledgements

Built using:

* FastAPI
* React
* Vite
* Tailwind CSS
* Groq
* Google Gemini
* Hugging Face
* Scikit-learn
* XGBoost

---

# 💡 INFORGE-AI

Transforming raw data into autonomous intelligence.
