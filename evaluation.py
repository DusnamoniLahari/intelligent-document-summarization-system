"""Command-line evaluation helper for the summarization system."""

import sys
from src.modules.document_processor import extract_text_from_pdf
from src.modules.summarizer import summarize_text
from src.modules.evaluator import evaluate_summary

# Evaluation is primarily available through the Streamlit application.
print("Use: streamlit run app.py")
