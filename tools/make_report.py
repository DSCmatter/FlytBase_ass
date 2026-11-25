"""Render REPORT.md into report.pdf using reportlab.

Run with: uv run --with reportlab python tools/make_report.py
"""

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "REPORT.md"
OUTPUT = ROOT / "docs" / "report.pdf"


def inline(text: str) -> str:
    text = escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def build_story(lines: list[str]):
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], fontSize=20, spaceAfter=10, leading=24
    )
    h1 = ParagraphStyle(
        "H1Custom", parent=styles["Heading1"], fontSize=14, spaceBefore=12, spaceAfter=6
    )
    body = ParagraphStyle(
        "BodyCustom", parent=styles["BodyText"], fontSize=10, leading=14, spaceAfter=6
    )
    quote = ParagraphStyle(
        "QuoteCustom", parent=body, leftIndent=10, textColor="#444444"
    )

    story = []
    paragraph = []
    bullets = []
    in_code = False
    code_lines = []

    def flush_paragraph():
        if paragraph:
            story.append(Paragraph(inline(" ".join(paragraph)), body))
            paragraph.clear()

    def flush_bullets():
        if bullets:
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(inline(b), body)) for b in bullets],
                    bulletType="bullet",
                    start="•",
                    leftIndent=12,
                )
            )
            bullets.clear()

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                story.append(Preformatted("\n".join(code_lines), body))
                story.append(Spacer(1, 4))
                code_lines = []
                in_code = False
            else:
                flush_paragraph()
                flush_bullets()
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            flush_bullets()
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(inline(stripped[2:]), title))
        elif stripped.startswith("## "):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(inline(stripped[3:]), h1))
        elif stripped.startswith("### "):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(inline(stripped[4:]), styles["Heading2"]))
        elif stripped.startswith("- "):
            flush_paragraph()
            bullets.append(stripped[2:])
        elif stripped.startswith("> "):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(inline(stripped[2:]), quote))
        else:
            flush_bullets()
            paragraph.append(stripped)

    flush_paragraph()
    flush_bullets()
    return story


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(20 * mm, 12 * mm, "Drone Security Analyst Agent - FlytBase Assignment")
    canvas.drawRightString(A4[0] - 20 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    lines = SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
        title="Drone Security Analyst Agent Report",
        author="AI Engineer Assignment Candidate",
    )
    doc.build(build_story(lines), onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
