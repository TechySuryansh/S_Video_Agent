from fpdf import FPDF


def generate_pdf_report(result: dict) -> bytes:
    """Generate a clean PDF report from the analysis result."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    title = str(result.get("title", "Meeting Report"))
    safe_title = title.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 15, safe_title, ln=True, align="C")
    pdf.ln(5)

    # Divider
    pdf.set_draw_color(124, 58, 237)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)

    # Sentiment section if available
    sentiment = result.get("sentiment", {})
    if sentiment:
        tone = sentiment.get("overall_tone", "neutral").capitalize()
        confidence = sentiment.get("confidence", "N/A")
        explanation = sentiment.get("explanation", "")

        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(124, 58, 237)
        pdf.cell(0, 10, "Meeting Tone", ln=True)

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        tone_text = f"{tone} ({confidence}) - {explanation}"
        safe_tone = tone_text.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_tone)
        pdf.ln(5)

    # Main sections
    sections = [
        ("Summary", result.get("summary", "N/A")),
        ("Action Items", result.get("action_items", "N/A")),
        ("Key Decisions", result.get("key_decisions", "N/A")),
        ("Open Questions", result.get("open_questions", "N/A")),
    ]

    for heading, content in sections:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(124, 58, 237)
        pdf.cell(0, 10, heading, ln=True)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)

        clean = str(content).encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, clean)
        pdf.ln(5)

    # Transcript section on new page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(124, 58, 237)
    pdf.cell(0, 10, "Full Transcript", ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    transcript = str(result.get("transcript", "N/A"))
    clean_transcript = transcript.encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 5, clean_transcript)

    return pdf.output()  # Returns bytes
