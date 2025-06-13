# Prashna Rachna – AI Question Generation Platform

A full-stack, production-ready platform for document upload, semantic chunking, and AI-powered question generation. Built with Next.js (frontend), FastAPI (backend), PostgreSQL, ChromaDB, Clerk authentication, and hybrid file/cloud storage.

---

## 🏗️ Monorepo Structure

```
.
├── backend/    # FastAPI backend (API, parsing, LLM, storage)
├── client/     # Next.js frontend (UI, auth, upload, question gen)
├── docs/       # Project documentation
├── docker-compose.yml  # Multi-service orchestration
└── README.md   # (this file)
```

---

## 🚀 Features

- **User Authentication**: Clerk (SSO, JWT, session)
- **Document Upload**: PDF, DOCX, PPTX (validated)
- **Cloud Storage Ready**: Local for dev, S3/GCS/Azure for prod
- **Semantic Parsing**: LangChain chunking, ChromaDB vector search
- **AI Question Generation**: LLM-powered, MCQ, Fill-in-the-Blank, True/False, Bloom's Taxonomy
- **Feedback & History**: Store and retrieve user feedback and question history
- **Production-Ready**: Scalable, secure, cloud-native

---

## ⚡ Quickstart (Dev)

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd <repo-root>
```

### 2. Backend (API)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env  # Edit .env for DB, Clerk, storage
python init_db.py    # Or: alembic upgrade head
uvicorn main:app --reload
```
- Docs: [backend/README.md](backend/README.md)

### 3. Frontend (Web UI)

```bash
cd client
npm install
npm run dev
```
- Docs: [client/README.md](client/README.md)

### 4. Open in Browser
- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)

---

## ☁️ Cloud & Production

- **Cloud Storage**: Set `FILE_STORAGE_TYPE` in backend `.env` to `aws_s3`, `gcp`, or `azure` and provide credentials
- **Docker Compose**: Use `docker-compose.yml` for full-stack orchestration
- **Deployment Guide**: See [backend/docs/deployment_guide.md](backend/docs/deployment_guide.md)

---

## 🧩 Architecture

- **Frontend**: Next.js (React, Clerk, Zod, modern UI/UX)
- **Backend**: FastAPI (async, Pydantic, LangChain, ChromaDB, PostgreSQL)
- **Storage**: Hybrid (local for dev, S3/GCS/Azure for prod)
- **Auth**: Clerk (JWT, session, SSO)
- **Vector Search**: ChromaDB
- **LLM**: Ollama/DeepSeek/other (configurable)

---

## 📝 Contributing

1. Fork the repo
2. Create a feature branch
3. Commit your changes
4. Open a PR!

---

## 📄 License

MIT License

---

**Questions?**  
See [backend/docs/deployment_guide.md](backend/docs/deployment_guide.md) or open an issue! 

##TODO 
- Check if the document already exists if yes dont parse it again 
- Add a chat interface after question generation to modify the generated questions and personalize them 
- Add curriculum feature where users can select from curriculum like cbse etc or upload their own curriculum for better alignment 
- CrewAI Agents for question generation 
- Fix ai hallucination its not generating the specified number of questions everytime 