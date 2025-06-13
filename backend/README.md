# 📚 Prashna Rachna – Question Generation Platform (Backend)

A scalable, production-ready FastAPI backend for document upload, parsing, semantic chunking, and AI-powered question generation.
Supports Clerk authentication, PostgreSQL, ChromaDB, and **hybrid file storage** (local for dev, cloud for production: AWS S3, GCS, Azure Blob).

---

## 🚀 Features

- **User Authentication**: Clerk integration (JWT, session, profile)
- **Document Upload**: PDF, DOCX, PPTX with validation
- **Cloud Storage Ready**: Seamless switch between local and cloud (S3, GCS, Azure)
- **Document Parsing**: LangChain-based, semantic chunking
- **Vector Storage**: ChromaDB for semantic search
- **AI Question Generation**: LLM-powered, supports MCQ, Fill-in-the-Blank, True/False, Bloom's Taxonomy
- **Feedback & History**: Store and retrieve user feedback and question history
- **Production-Ready**: Environment-based config, scalable, secure

---

## 🛠️ Quickstart

### 1. Clone & Environment Setup

```bash
git clone <your-repo-url>
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp env.example .env
# Edit .env with your DB, Clerk, and storage credentials
```

- For **local dev**: `FILE_STORAGE_TYPE=local`
- For **production**: set to `aws_s3`, `gcp`, or `azure` and provide credentials

### 3. Database Setup

```bash
# Initialize tables (dev)
python init_db.py

# Or use Alembic migrations (recommended)
alembic upgrade head
```

### 4. Run the Server

```bash
uvicorn main:app --reload
# Or for production:
# uvicorn main:app --host 0.0.0.0 --port 8000
```

API available at: [http://localhost:8000](http://localhost:8000)

---

## ☁️ Cloud Storage Configuration

- **AWS S3**: Set `FILE_STORAGE_TYPE=aws_s3` and provide `AWS_S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- **Google Cloud Storage**: Set `FILE_STORAGE_TYPE=gcp` and provide `GCP_STORAGE_BUCKET`, `GOOGLE_APPLICATION_CREDENTIALS`
- **Azure Blob**: Set `FILE_STORAGE_TYPE=azure` and provide `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_CONTAINER_NAME`

See [`docs/deployment_guide.md`](docs/deployment_guide.md) for full cloud setup and migration instructions.

---

## 🧪 Testing

```bash
# Run all backend tests
pytest
# Or run individual test files
python test_document_upload.py
python test_question_generation.py
```

---

## 🔒 Authentication

- Uses Clerk for user management and JWT authentication.
- Protected endpoints require:
  ```
  Authorization: Bearer <your_jwt_token>
  ```

---

## 📖 API Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🏗️ Project Structure

```
backend/
├── app/                # Main application code
│   ├── routes/         # API routes
│   ├── services/       # Business logic, storage, parsing, LLM
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   └── ...
├── docs/               # Documentation (deployment, tasks, etc.)
├── tests/              # Test files
├── uploads/            # Local file storage (dev only)
├── requirements.txt    # Python dependencies
├── main.py             # FastAPI entrypoint
└── ...
```

---

## 🌐 Deployment

- **Heroku, Railway, Render, AWS, GCP, Azure**: Supported out of the box
- See [`docs/deployment_guide.md`](docs/deployment_guide.md) for step-by-step deployment and cloud migration

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
See the [deployment guide](docs/deployment_guide.md) or open an issue! 