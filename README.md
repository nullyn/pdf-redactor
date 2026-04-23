# PDF Redaction Tool

Complete PDF redaction service.

## Quick Start (Docker)

```bash
docker-compose up --build
```

Then open: **http://localhost:3000**

## Manual Start

1. **Backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_lg
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend:**
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```
