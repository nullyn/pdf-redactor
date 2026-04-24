# pdf-redactor

A local PDF PII redaction tool. Upload a PDF, review detected sensitive entities with bounding boxes, select what to redact, and download the permanently redacted file.

Built on top of **[OpenAI Privacy Filter](https://pypi.org/project/openai-privacy-filter/)** — OpenAI's local privacy detection model (~1.5B params, ~96% F1). All inference runs on your machine; nothing leaves your network.

---

## What we add on top of OPF

OPF is a CLI that detects PII spans in text. This project wraps it into a full document workflow:

- **PDF extraction** — pulls text per-page via PyMuPDF, feeds it to OPF
- **Coordinate mapping** — translates OPF text spans back to PDF bounding boxes
- **Visual review UI** — HTML/JS frontend with a PDF preview, per-entity checkboxes, and redaction overlays
- **Permanent redaction** — applies black-box redactions to the PDF binary via PyMuPDF (not just text removal)
- **REST API** — FastAPI backend with upload / detect / apply / download endpoints

---

## Stack

| Layer | Tech |
|---|---|
| PII detection | [openai-privacy-filter](https://pypi.org/project/openai-privacy-filter/) |
| PDF processing | PyMuPDF |
| Backend | FastAPI + Uvicorn |
| Frontend | Vanilla HTML/CSS/JS + PDF.js |

---

## Quick start

### 1. Install OPF

```bash
pip install openai-privacy-filter
```

> First run downloads the model checkpoint (~3GB) to `~/.opf/privacy_filter/`.  
> On Apple Silicon, CPU inference is used automatically (`--device cpu`).

### 2. Install backend deps

```bash
cd pdf_redaction_project/backend
pip install -r requirements.txt
```

### 3. Configure `.env`

```bash
# pdf_redaction_project/backend/.env
ALLOWED_ORIGINS=["*"]
```

### 4. Start the backend

```bash
cd pdf_redaction_project/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Open the frontend

```bash
open pdf_redaction_project/frontend/index.html
```

---

## API

```
POST /api/upload          →  { file_id, page_count, filename }
POST /api/detect?file_id= →  { matches: [{page, text, type, rect, confidence}], summary }
POST /api/apply           →  { file_id, redaction_count, download_url }
GET  /api/download/{id}   →  redacted PDF binary
GET  /api/health          →  { status: "ok" }
```

---

## Attribution

PII detection is powered by **OpenAI Privacy Filter**, developed by OpenAI.  
PyPI: [openai-privacy-filter](https://pypi.org/project/openai-privacy-filter/)

PDF rendering in the browser via [PDF.js](https://github.com/mozilla/pdf.js) by Mozilla.
