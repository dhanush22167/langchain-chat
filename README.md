# 💬 LangChain PDF Chat

Upload any PDF or text file and ask questions about it. Powered by **LangChain + Groq (free) + FAISS**.

---

## What This Does

1. You upload a PDF or TXT file
2. LangChain splits it into chunks and creates embeddings (HuggingFace, free)
3. Embeddings stored in FAISS (in-memory vector store, no database needed)
4. You ask a question → it finds relevant chunks → Groq LLM answers

---

## Deploy in 3 Steps

### Step 1 — Get your free Groq API key
1. Go to **console.groq.com** → Sign up free
2. Click **API Keys** → Create key
3. Copy it (starts with `gsk_...`)

### Step 2 — Deploy Backend to Render.com (free)
1. Push this repo to GitHub (see below)
2. Go to **render.com** → New → Web Service
3. Connect your GitHub repo
4. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: **Free**
5. Environment Variables → Add: `GROQ_API_KEY` = your key
6. Deploy → copy your URL e.g. `https://langchain-chat.onrender.com`

### Step 3 — Deploy Frontend to Netlify (free, no config needed)
1. Open `frontend/index.html`
2. Find this line near the top of the script:
   ```
   : (window.ENV_API_URL || 'https://YOUR_RENDER_URL.onrender.com/api');
   ```
3. Replace `YOUR_RENDER_URL` with your actual Render URL
4. Go to **netlify.com** → "Deploy manually"
5. Drag and drop the `frontend` folder → Done!

---

## Push to GitHub

```bash
git init
git add .
git commit -m "feat: LangChain PDF chat app"
git remote add origin https://github.com/YOUR_USERNAME/langchain-chat.git
git push -u origin main
```

---

## Run Locally

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
# Create .env file with: GROQ_API_KEY=your_key
uvicorn main:app --reload --port 8000

# Frontend — just open frontend/index.html in your browser!
```

---

## Tech Stack

| Part | Technology | Cost |
|---|---|---|
| Backend | FastAPI + LangChain | Free |
| LLM | Groq (llama-3.1-8b) | Free |
| Embeddings | HuggingFace MiniLM | Free |
| Vector Store | FAISS (in-memory) | Free |
| Backend Hosting | Render.com | Free |
| Frontend Hosting | Netlify | Free |
