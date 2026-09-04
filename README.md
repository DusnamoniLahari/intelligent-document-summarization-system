# Intelligent Document Summarization System — V4

A modular AI-based document summarization system for extracting text from PDFs, checking extraction quality, generating concise summaries, translating results, evaluating summaries with ROUGE, and producing downloadable reports.

## V4 additions

- PDF report download
- Interactive dashboard improvements
- Word-count and ROUGE charts
- Optional Tesseract OCR fallback for scanned PDFs
- Extraction method and OCR observability

## Run on Windows

### Terminal 1 — Flask backend

```text
python -m backend.app
```

### Terminal 2 — Streamlit frontend

```text
python -m streamlit run app.py
```

Open the Streamlit URL shown in the terminal, normally `http://localhost:8501`.

## OCR note

Normal text PDFs do not require OCR. For scanned PDFs, install the Tesseract OCR application on Windows in addition to the Python dependencies. If Tesseract is unavailable, the application still supports normal text-based PDFs.

## Recommended test

1. Upload a normal text PDF.
2. Confirm extraction quality and extraction method.
3. Generate a summary.
4. Download TXT and PDF reports.
5. Paste a reference summary and confirm ROUGE charts appear.
6. Optionally test a scanned PDF after installing Tesseract.
