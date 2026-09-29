---
title: InForge AI Backend
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# 🚀 INFORGE-AI

> **Autonomous Multi-Agent AI Analytics Platform** — Transform raw datasets into actionable business intelligence with zero manual intervention.

---

## ✨ What It Does

Upload a CSV or Excel file. INFORGE-AI handles everything else:

- **Data ingestion** — schema detection, metadata extraction
- **Data cleaning** — nulls, duplicates, outliers
- **Exploratory Data Analysis** — statistics, correlations, distributions
- **Visualization** — auto-generated, context-aware charts
- **ML Benchmarking** — auto-detected task, multiple models trained and compared
- **Business Insights** — synthesized from your data, in plain language
- **Code Generation** — reproducible Python scripts for every step
- **Conversational Q&A** — ask follow-up questions in natural language
- **Resilient fallback mode** — returns computed summaries, charts, reports, and chat answers even when external LLM APIs are unavailable

---

## 🧠 Autonomous Agent Pipeline

| # | Agent | Role |
|---|-------|------|
| 1 | **Ingestion Agent** | Dataset schema & metadata analysis |
| 2 | **Cleaning Agent** | Handle nulls, duplicates, outliers |
| 3 | **EDA Agent** | Statistical analysis & correlations |
| 4 | **Visualization Agent** | Generate optimized charts |
| 5 | **ML Agent** | Train & benchmark ML models |
| 6 | **Insights Agent** | Business intelligence synthesis |
| 7 | **Code Agent** | Generate reproducible Python scripts |
| 8 | **Chat Agent** | Interactive contextual Q&A |

---

## 🏗️ Architecture

```
Frontend (React + Vite)
        ↓
WebSocket + REST API
        ↓
FastAPI Backend
        ↓
Multi-Agent Orchestrator
        ↓
LLMs + Local Fallbacks + ML Models + Analytics Engine
```

The backend computes the core analytics locally with pandas, scikit-learn, XGBoost, Matplotlib, and Seaborn. LLMs are used to enrich explanations, chart strategy, generated code, and conversational answers. If an LLM provider fails because of an invalid key, unavailable model, rate limit, or network issue, INFORGE-AI falls back to deterministic local summaries so the user still gets a completed analysis.

---

## ⚙️ Tech Stack

### Backend
`FastAPI` · `Uvicorn` · `AsyncIO` · `WebSockets` · `Pandas` · `NumPy` · `Scikit-learn` · `XGBoost` · `Matplotlib` · `Seaborn` · `ReportLab`

### AI Models

| Model | Purpose |
|-------|---------|
| Gemini 2.0 Flash Lite | Visualization reasoning |
| Groq Llama-3.3-70B | Insights & synthesis |
| OpenRouter-compatible LLMs | Schema & data analysis |
| Local fallback heuristics | Offline/resilient summaries and chat answers |

### Frontend
`React 19` · `Vite` · `Tailwind CSS 4` · `Framer Motion` · `Recharts` · `Lucide React`

---

## 📂 Project Structure

```
INFORGE-AI/
├── backend/
│   ├── agents/
│   ├── pipeline/
│   ├── utils/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   └── hooks/
│   ├── public/
│   └── package.json
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 📡 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | `POST` | Upload CSV/Excel dataset |
| `/ws/{session_id}` | `WebSocket` | Real-time progress stream |
| `/results/{session_id}` | `GET` | Retrieve complete analysis |
| `/chat/{session_id}` | `POST` | Ask questions about analysis |
| `/export/pdf/{session_id}` | `GET` | Download PDF report |
| `/export/code/{session_id}` | `GET` | Download generated Python script |
| `/docs` | `GET` | Swagger UI |

---

## 📊 Machine Learning Capabilities

Auto-detects task type from dataset structure.

**Classification** — Logistic Regression, Random Forest, XGBoost, KNN

**Regression** — Linear Regression, Ridge Regression, Random Forest Regressor, XGBoost Regressor

**Clustering** — KMeans, DBSCAN

---

## 🔄 Real-Time Streaming

Live pipeline updates over WebSocket:

```
ws://localhost:8000/ws/{session_id}
```

- Live progress updates per agent step
- Real-time UI synchronization
- Progress replay support

---

## 🚀 Local Setup

### 1. Clone

```bash
git clone https://github.com/vinayak533/InForge-AI.git
cd InForge-AI
```

### 2. Backend

```bash
cd backend
python -m venv ../venv

# Windows
..\venv\Scripts\activate

# Linux / Mac
source ../venv/bin/activate

pip install -r requirements.txt
python main.py
```

Backend runs at `http://localhost:8000`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### 4. Single-port local preview

To serve the production React build from FastAPI:

```bash
cd frontend
npm install
npm run build

cd ../backend
../venv/Scripts/python.exe main.py
```

Open `http://localhost:8000/index.html`.

---

## 🔐 Environment Variables

Create `backend/.env`:

```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
OPENROUTER_API_KEY=your_key
```

These keys are optional for the core pipeline. Without valid keys, the platform still runs local schema detection, cleaning, EDA, visualization, ML benchmarking, report/code fallback generation, and chat answers grounded in computed results.

---

## 🌐 Deployment

| Service | Platform |
|---------|----------|
| Frontend | Vercel |
| Backend | Hugging Face Spaces (Docker) · Railway · Render · AWS EC2 |

---

## 📄 Export Features

- PDF business intelligence reports
- Cleaned CSV datasets
- Reproducible Python analysis scripts

---



## 📌 Roadmap

- [ ] Multi-user collaboration
- [ ] Fine-tuned domain-specific models
- [ ] Auto dashboard generation
- [ ] AI-powered forecasting
- [ ] Cloud data warehouse integration
- [ ] Scheduled analytics workflows

---

## 👨‍💻 Author

**Vinayak K V** — Data Science & AI Engineer

Specializations: Machine Learning · Generative AI · LLM Engineering · Multi-Agent Systems · Full-Stack AI

GitHub: [github.com/vinayak533](https://github.com/vinayak533)

---

## 📜 License

MIT License

---

*Built with FastAPI · React · Vite · Tailwind CSS · Groq · Google Gemini · Hugging Face · Scikit-learn · XGBoost*
