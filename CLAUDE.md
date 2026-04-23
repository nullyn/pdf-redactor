# pdf-redactor

A local PDF PII redaction tool with a FastAPI backend and a plain HTML/JS frontend.
Users upload a PDF, review detected PII entities with bounding boxes, select which to redact, and download the permanently redacted PDF.

---

## Branches

| Branch | Detection engine | Status |
|---|---|---|
| `master` | spaCy NER + regex | Original — requires `en_core_web_lg` model |
| `opf-backend` | OpenAI Privacy Filter (OPF) | Active — 96% F1, fully local, no spaCy |

**Work on `opf-backend` for new development.** The OPF backend is the better detector and has been tested end-to-end.

---

## Project Structure

```
pdf_redaction_project/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # upload.py, detect.py, apply.py, health.py
│   │   ├── api/models/     # schemas.py (Pydantic request/response models)
│   │   ├── services/
│   │   │   ├── opf_detector.py   # OPF subprocess wrapper (opf-backend branch)
│   │   │   ├── ner_detector.py   # spaCy detector (master branch only)
│   │   │   ├── redactor.py       # coordinates detection + PDF redaction
│   │   │   ├── pdf_handler.py    # PyMuPDF text extraction + redaction
│   │   │   └── storage.py        # temp file management (/tmp/pdf_redaction/)
│   │   ├── utils/constants.py    # EntityType enum + OPF_LABEL_MAPPING
│   │   ├── config.py             # pydantic-settings (reads .env)
│   │   └── main.py               # FastAPI app entry point
│   ├── .env                      # local config (not committed)
│   └── requirements.txt
└── frontend/
    └── index.html        # self-contained UI, calls http://localhost:8000/api
```

---

## Running Locally

### 1. Install OPF (opf-backend branch only)

```bash
pip install openai-privacy-filter
```

OPF downloads a ~1.5B parameter model on first run (~3GB). Checkpoint stored at `~/.opf/privacy_filter/`.

**Mac (Apple Silicon / no CUDA):** OPF must run with `--device cpu`. This is handled automatically via the `OPF_DEVICE=cpu` default in `opf_detector.py`. MPS fails due to missing `triton` module.

### 2. Install backend dependencies

```bash
cd pdf_redaction_project/backend
pip install -r requirements.txt
```

### 3. Fix `.env` if needed

The `ALLOWED_ORIGINS` field must be valid JSON (pydantic-settings parses it as a list):

```
ALLOWED_ORIGINS=["*"]
```

Not `ALLOWED_ORIGINS=*` (will crash on startup).

### 4. Start the backend

```bash
cd pdf_redaction_project/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verify: `curl http://localhost:8000/api/health`

### 5. Open the frontend

```bash
open -a "Google Chrome" pdf_redaction_project/frontend/index.html
```

The frontend calls `http://localhost:8000/api` directly — no separate frontend server needed.

---

## API Flow

```
POST /api/upload          → { file_id, page_count, filename, size_bytes }
POST /api/detect?file_id= → { file_id, page_count, matches: [{page, text, type, rect, confidence}], summary }
POST /api/apply           → { file_id, redaction_count, download_url }
GET  /api/download/{id}   → redacted PDF binary
GET  /api/health          → { status: "ok" }
```

Uploaded files are stored in `/tmp/pdf_redaction/`. They are not auto-cleaned up; delete manually if needed.

---

## OPF Detector Notes (`opf_detector.py`)

- OPF processes stdin **line by line** and emits one JSON object per line. The detector parses multiple JSON objects from stdout using `JSONDecoder.raw_decode()` in a loop.
- Coordinates are found via `page.search_for(entity_text)` in PyMuPDF — character offsets from OPF are not used.
- Entity dedup is by `(type, text)` to avoid redundant bounding boxes for repeated text.
- Override device: `OPF_DEVICE=mps python -m uvicorn ...` (only if triton is installed).

---

## Known Limitations

- **Scanned/image-only PDFs:** Return 0 entities silently — no error surfaced to the UI. Text must be embedded in the PDF.
- **Long PDFs:** OPF runs per page sequentially; large documents are slow on CPU.
- **No auth / rate limiting:** Not production-ready as-is.
