# 💬 Collaborative Fact-Checking Chatbot

This project is a full-stack chatbot application designed to support collaborative fact-checking. Users can submit questions and upload documents, and the system extracts factual claims, ranks them, and allows users to vote on which claim to explore further.

---

## 🧠 Project Overview

The chatbot consists of:

- **Frontend**: A React-based interface where users interact with the chatbot, submit questions, upload files, and vote on claims.
- **Backend**: A FastAPI service that handles file processing, claim extraction, caching, and claim weight updates.

---

## 🔍 Claim Extraction & Voting Mechanism

### 1. **Question Submission**
Users submit a question and optionally attach documents (e.g. PDFs, DOCs).

### 2. **Claim Generation**
The backend uses a mock LLM (`LLMGenerator`) to generate multiple claims from the input. Each claim has:
- `id`: Unique identifier
- `text`: The statement extracted
- `weight`: A numerical score representing relevance

### 3. **Claim Ranking**
Claims are ranked by weight. If multiple claims share the highest weight, the frontend prompts the user to choose one.

### 4. **Voting & Weight Update**
When a user selects a claim:
- The backend updates the weight of the selected claim (`+1`)
- The updated claim set is cached for future reference

---

## 📡 API Endpoints

### `POST /ask`
- Accepts: `question`, `files`
- Returns: `claims`, `answer`, `referenced_documents`

### `POST /claim`
- Accepts: `question`, `files`, `claim_id`
- Action: Increments the weight of the selected claim and updates the cache

---

## 🧱 Project Structure

```bash
chatbot/ 
├── backend/ 
│ ├── src/ 
│ │ ├── api/ # FastAPI route definitions 
│ │ ├── helpers/ # Claim and question handling 
│ │ ├── utils/ # LLM mock, cache, config 
│ │ ├── config.yaml # App configuration 
│ │ ├── main.py # FastAPI entry point 
│ │ └── requirements.txt # Python dependencies 
│ ├── test/ # Backend tests 
│ └── Dockerfile # Backend container 
├── frontend/ 
│ ├── src/ 
│ │ ├── components/ # React components 
│ │ ├── api.ts # Axios API calls 
│ │ ├── App.tsx # Main app component 
│ │ └── main.tsx # Entry point 
│ ├── index.html # HTML template 
│ ├── nginx.conf # NGINX config 
│ ├── package.json # Node dependencies 
│ ├── vite.config.ts # Vite build config 
│ └── Dockerfile # Frontend container 
├── .gitignore # Git ignore rules
├── docker-compose.yml # Docker orchestration 
└── README.md # Project documentation
```

---

## 🐳 Running with Docker

Make sure Docker is installed, then run:

```bash
docker-compose up --build
```
This will:

- Start the FastAPI backend on http://localhost:7373
- Start the React frontend on http://localhost:3000

---

## 🛠 Development Setup (Manual)

### Backend
```bash
cd backend
python -m venv env
source env/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 7373
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```