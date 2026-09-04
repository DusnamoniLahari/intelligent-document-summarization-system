import io
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:5000"
API_URL = f"{API_BASE}/api/summarize"

st.set_page_config(
    page_title="Intelligent Document Summarization System",
    page_icon="📄",
    layout="wide",
)

st.title("📄 Intelligent Document Summarization System")
st.caption("System Engineering Project • Streamlit • Flask REST API • NLP/Transformer • OCR • Quality Evaluation")

with st.sidebar:
    st.header("⚙️ System Controls")
    target_language = st.selectbox("Output language", ["English", "Hindi", "Telugu", "Japanese"])
    summary_ratio = st.slider("Summary length (%)", 10, 60, 30, 5)
    method = st.selectbox(
        "Summarization method",
        ["Hybrid", "Extractive NLP", "Transformer AI"],
        help="Hybrid is recommended for academic/technical PDFs because it preserves source wording."
    )
    st.divider()
    st.caption("Backend status")
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3)
        if health.ok:
            st.success("Flask API: Online")
        else:
            st.error("Flask API: Error")
    except requests.RequestException:
        st.error("Flask API: Offline")

uploaded_file = st.file_uploader("📤 Upload a PDF document", type=["pdf"], key="pdf_uploader")
reference = st.text_area(
    "Optional reference summary (for research-grade ROUGE evaluation)",
    height=100,
    help="Paste a human-written/reference summary. ROUGE is shown only when this is supplied."
)

if uploaded_file:
    st.info(f"Selected file: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

if uploaded_file and st.button("🚀 Process Document", type="primary", key="process_document_button"):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    data = {
        "summary_ratio": str(summary_ratio),
        "target_language": target_language,
        "method": method,
        "reference_summary": reference,
    }

    with st.spinner("Extracting, summarizing, evaluating and preparing results..."):
        try:
            response = requests.post(API_URL, files=files, data=data, timeout=600)
        except requests.RequestException as exc:
            st.error("Could not connect to Flask backend. Run: python -m backend.app")
            st.exception(exc)
            st.stop()

    try:
        result = response.json()
    except ValueError:
        st.error(f"Backend returned an invalid response (HTTP {response.status_code}).")
        st.text(response.text)
        st.stop()

    if response.status_code != 200:
        st.error(result.get("error", "Backend processing failed"))
        st.stop()

    st.success("Document processed successfully.")

    quality = result["document_quality"]
    stats = result["statistics"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Extracted words", quality["word_count"])
    c2.metric("Summary words", stats["summary_words"])
    c3.metric("Compression", f"{stats['compression_percent']}%")
    c4.metric("Processing time", f"{result.get('processing_time_seconds', 0)} s")

    st.subheader("🔎 Processing Diagnostics")
    d1, d2, d3 = st.columns(3)
    d1.metric("Extraction method", result.get("extraction_method", "Unknown"))
    d2.metric("OCR used", "Yes" if result.get("ocr_used") else "No")
    d3.metric("Text quality", f"{quality['readability_score']}%")
    if result.get("ocr_used"):
        st.warning("This document appears to be scanned/image-based. Tesseract OCR was used as a fallback.")
    elif result.get("extraction_method") == "None":
        st.warning("No extraction method was available.")

    if quality["status"] == "Good":
        st.success(f"PDF text quality: {quality['status']} ({quality['readability_score']}%)")
    elif quality["status"] == "Fair":
        st.warning(f"PDF text quality: {quality['status']} ({quality['readability_score']}%). {quality['warning']}")
    else:
        st.error(f"PDF text quality: {quality['status']} ({quality['readability_score']}%). {quality['warning']}")

    st.subheader("📊 Summary Dashboard")
    chart_data = {
        "Original document": quality["word_count"],
        "Generated summary": stats["summary_words"],
    }
    st.bar_chart(chart_data, height=280)
    st.caption("Word-count comparison: the summary is shorter than the original document.")

    with st.expander("📖 View extracted PDF text", expanded=False):
        st.text_area("Extracted text", result["extracted_text"], height=300, label_visibility="collapsed")

    st.subheader("🤖 AI-Generated Summary")
    st.write(result["summary"])

    summary_download = (
        f"Document: {result['filename']}\n"
        f"Method: {result['method']}\n"
        f"Extraction method: {result.get('extraction_method', 'Unknown')}\n"
        f"OCR used: {'Yes' if result.get('ocr_used') else 'No'}\n"
        f"Summary length: {summary_ratio}%\n\n"
        f"{result['summary']}\n"
    )
    st.download_button(
        "⬇️ Download Summary (.txt)",
        data=summary_download,
        file_name="summary.txt",
        mime="text/plain",
    )

    # PDF report download is generated entirely from the processed result.
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import inch
        from xml.sax.saxutils import escape

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
        styles = getSampleStyleSheet()
        styles["Title"].alignment = TA_CENTER
        story = [
            Paragraph("Intelligent Document Summarization Report", styles["Title"]),
            Spacer(1, 0.2 * inch),
            Paragraph(f"Document: {escape(result['filename'])}", styles["BodyText"]),
            Paragraph(f"Method: {escape(result['method'])}", styles["BodyText"]),
            Paragraph(f"Extraction: {escape(result.get('extraction_method', 'Unknown'))}", styles["BodyText"]),
            Paragraph(f"OCR used: {'Yes' if result.get('ocr_used') else 'No'}", styles["BodyText"]),
            Paragraph(f"Original words: {quality['word_count']} | Summary words: {stats['summary_words']} | Compression: {stats['compression_percent']}%", styles["BodyText"]),
            Spacer(1, 0.2 * inch),
            Paragraph("AI-Generated Summary", styles["Heading2"]),
        ]
        for paragraph in result["summary"].split("\n"):
            if paragraph.strip():
                story.append(Paragraph(escape(paragraph.strip()), styles["BodyText"]))
                story.append(Spacer(1, 0.08 * inch))
        if target_language != "English":
            story.extend([Paragraph(f"Translated Summary — {escape(target_language)}", styles["Heading2"])])
            story.append(Paragraph(escape(result["translated_summary"]), styles["BodyText"]))
        doc.build(story)
        st.download_button(
            "📄 Download Report (.pdf)",
            data=buffer.getvalue(),
            file_name="summarization_report.pdf",
            mime="application/pdf",
        )
    except Exception as exc:
        st.warning(f"PDF report download is unavailable: {exc}")

    if target_language != "English":
        st.subheader(f"🌐 Translated Summary — {target_language}")
        st.write(result["translated_summary"])

    st.subheader("📊 Quality Evaluation")
    if result["evaluation"]:
        scores = result["evaluation"]
        c1, c2, c3 = st.columns(3)
        c1.metric("ROUGE-1", f"{scores['rouge1']:.3f}")
        c2.metric("ROUGE-2", f"{scores['rouge2']:.3f}")
        c3.metric("ROUGE-L", f"{scores['rougeL']:.3f}")
        st.caption("Computed against the reference summary supplied by the user.")
        st.bar_chart({"ROUGE-1": scores["rouge1"], "ROUGE-2": scores["rouge2"], "ROUGE-L": scores["rougeL"]})
    else:
        st.info("No reference summary supplied. ROUGE is intentionally not shown because a meaningful ROUGE evaluation requires a reference.")

st.divider()
st.subheader("🏗️ System Architecture")
st.markdown("""
**User → Streamlit UI → Flask REST API → PDF Extraction → Quality Gate → OCR Fallback → NLP/Transformer → Translation → Evaluation → Report/Response**

| Layer | Component |
|---|---|
| Presentation | Streamlit dashboard |
| API | Flask REST API |
| Document Processing | pypdf + PyMuPDF + text cleaning |
| OCR Fallback | Tesseract OCR + PyMuPDF rendering |
| Quality Gate | PDF text readability diagnostics |
| NLP | Extractive NLP / Transformer AI |
| Translation | Deep Translator |
| Evaluation | ROUGE-1 / ROUGE-2 / ROUGE-L |
| Reporting | TXT + PDF report download |
| Engineering | Modular design, validation, testing, observability |
""")

st.subheader("✨ V4 Engineering Features")
features = [
    "Dual PDF text extraction with automatic quality selection",
    "OCR fallback for scanned/image-only PDFs",
    "Interactive word-count and ROUGE charts",
    "Downloadable TXT summary and formatted PDF report",
    "Processing diagnostics and extraction-method observability",
]
for feature in features:
    st.write(f"• {feature}")
