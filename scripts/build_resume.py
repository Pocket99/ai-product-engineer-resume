"""Generate the HTML and PDF resume from README.md.

Install the pinned packages from scripts/requirements-resume.txt, then run:
    python scripts/build_resume.py
Optional project-local dependencies are loaded from .resume-tools/.
"""

from __future__ import annotations

import html
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".resume-tools"))

import markdown
from markdown.extensions.toc import slugify_unicode
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
)


CSS = """
:root { color-scheme: light; --ink: #172337; --muted: #536477; --accent: #166a82; }
* { box-sizing: border-box; }
body { margin: 0; color: var(--ink); background: #edf1f5;
  font: 15px/1.8 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC', sans-serif; }
main { max-width: 930px; margin: 28px auto; padding: 46px 58px;
  background: white; box-shadow: 0 8px 32px #1723370d; }
h1 { font-size: 30px; line-height: 1.3; margin: 0 0 12px; letter-spacing: .5px; }
h1 + p { color: var(--accent); font-size: 19px; line-height: 1.4; }
h2 { color: var(--accent); font-size: 19px; border-bottom: 1px solid #d5e0e7;
  margin: 28px 0 14px; padding-bottom: 7px; }
h3 { font-size: 17px; line-height: 1.6; margin: 22px 0 7px; break-after: avoid; }
h3 + p { font-size: 13px; color: var(--muted); margin-top: 0; }
p { margin: 9px 0; }
ul { padding-left: 21px; margin: 9px 0 14px; }
li { padding-left: 2px; margin-bottom: 7px; }
a { color: #12647b; text-decoration: none; overflow-wrap: anywhere; }
a:hover { text-decoration: underline; }
strong { font-weight: 700; }
details { margin: 16px 0 20px; color: var(--muted); }
summary { width: fit-content; color: var(--accent); cursor: pointer; }
.toc { padding: 0 12px; border-left: 2px solid #d5e0e7; }
.toc li { margin: 1px 0; }
@media (max-width: 680px) { main { margin: 0; padding: 26px 22px; } }
@page { size: A4; margin: 16mm 17mm; }
@media print {
  details { display: none; }
  body { font-size: 10pt; line-height: 1.65; background: white; }
  main { max-width: none; margin: 0; padding: 0; box-shadow: none; }
  h1 { font-size: 23pt; } h1 + p, h2 { font-size: 13pt; } h3 { font-size: 11pt; }
  h3 + p { font-size: 9pt; } li { break-inside: avoid; }
}
"""


def source_text() -> str:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    return text.split("<!-- resume:end -->", 1)[0].strip()


def inline(text: str) -> str:
    """Convert the small inline Markdown subset used in this resume."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    def link(match: re.Match[str]) -> str:
        label, href = match.groups()
        if not href.startswith(("https://", "http://")):
            return label
        return f'<a href="{html.escape(html.unescape(href), quote=True)}" color="#12647b">{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)


def register_fonts() -> None:
    if sys.platform == "darwin":
        font_dir = Path("/System/Library/Fonts")
        regular, bold, index = "STHeiti Light.ttc", "STHeiti Medium.ttc", 1
    else:
        font_dir = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        regular, bold, index = "msyh.ttc", "msyhbd.ttc", 0
    for name, env_var, filename in [
        ("Resume", "RESUME_FONT_REGULAR", regular),
        ("ResumeBold", "RESUME_FONT_BOLD", bold),
    ]:
        override = os.environ.get(env_var)
        path = Path(override) if override else font_dir / filename
        if not path.exists():
            raise SystemExit(f"Missing font: {path}. Set {env_var} to a Chinese TrueType font.")
        pdfmetrics.registerFont(TTFont(name, str(path), subfontIndex=0 if override else index))
    pdfmetrics.registerFontFamily(
        "Resume", normal="Resume", bold="ResumeBold", italic="Resume", boldItalic="ResumeBold"
    )


def styles() -> dict[str, ParagraphStyle]:
    base = dict(fontName="Resume", fontSize=9.9, leading=15.4,
                textColor=colors.HexColor("#172337"), wordWrap="CJK",
                alignment=TA_LEFT, splitLongWords=True, allowWidows=0, allowOrphans=0)
    body = ParagraphStyle("body", **base, spaceAfter=6)
    return {
        "body": body,
        "title": ParagraphStyle("title", parent=body, fontName="ResumeBold", fontSize=23,
                                leading=30, spaceAfter=8, keepWithNext=True),
        "role": ParagraphStyle("role", parent=body, fontName="ResumeBold", fontSize=13,
                               leading=18, textColor=colors.HexColor("#166a82"),
                               keepWithNext=True),
        "section": ParagraphStyle("section", parent=body, fontName="ResumeBold", fontSize=13,
                                  leading=20, spaceBefore=14, spaceAfter=6,
                                  textColor=colors.HexColor("#166a82"), keepWithNext=True),
        "project": ParagraphStyle("project", parent=body, fontName="ResumeBold", fontSize=11.2,
                                  leading=18, spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "meta": ParagraphStyle("meta", parent=body, fontSize=8.8, leading=13.5,
                               textColor=colors.HexColor("#536477"), keepWithNext=True),
        "bullet": ParagraphStyle("bullet", parent=body, leftIndent=10, firstLineIndent=0,
                                 bulletIndent=0, bulletFontName="Resume", bulletFontSize=7,
                                 spaceAfter=5),
    }


def make_flowables(text: str) -> list:
    st = styles()
    flow = []
    next_meta = False
    next_role = False

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"\s*·\s*\[[^\]]+\]\((?:\./)?resume\.pdf\)", "", line)
        if line.startswith("### "):
            flow.append(Paragraph(inline(line[4:]), st["project"]))
            next_meta = True
            continue
        if line.startswith("## "):
            flow.append(Paragraph(inline(line[3:]), st["section"]))
            rule = HRFlowable(width="100%", thickness=.5,
                              color=colors.HexColor("#d5e0e7"), spaceAfter=4)
            rule.keepWithNext = True
            flow.append(rule)
            next_meta = False
            continue
        if line.startswith("# "):
            flow.append(Paragraph(inline(line[2:]), st["title"]))
            next_role = True
            continue
        if next_role:
            flow.append(Paragraph(inline(line), st["role"]))
            next_role = False
            continue
        if line.startswith("- "):
            flow.append(Paragraph(inline(line[2:]), st["bullet"], bulletText="•"))
        else:
            flow.append(Paragraph(inline(line), st["meta"] if next_meta else st["body"]))
        next_meta = False
    return flow


class ResumeDocument(BaseDocTemplate):
    """Give the long resume a navigable outline in PDF readers."""

    def beforeDocument(self) -> None:
        self.heading_count = 0

    def afterFlowable(self, flowable) -> None:
        if not isinstance(flowable, Paragraph):
            return
        levels = {"section": 0, "project": 1}
        level = levels.get(flowable.style.name)
        if level is None:
            return
        self.heading_count += 1
        key = f"heading-{self.heading_count}"
        self.canv.bookmarkHorizontalAbsolute(key, self.frame._y + flowable.height)
        self.canv.addOutlineEntry(flowable.getPlainText(), key, level=level, closed=True)


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d5e0e7"))
    canvas.setLineWidth(.4)
    canvas.line(17 * mm, 13 * mm, A4[0] - 17 * mm, 13 * mm)
    canvas.setFont("Resume", 8)
    canvas.setFillColor(colors.HexColor("#607386"))
    canvas.drawString(17 * mm, 8.7 * mm, doc.title)
    canvas.drawRightString(A4[0] - 17 * mm, 8.7 * mm, str(doc.page))
    canvas.restoreState()


def main() -> None:
    text = source_text()
    name_line, role_line, *_ = (line for line in text.splitlines() if line.strip())
    name = name_line.removeprefix("# ").split("·", 1)[0].strip()
    role = role_line.strip("*").removeprefix("求职方向｜")
    title = f"{name} · {role}"
    converter = markdown.Markdown(
        extensions=["extra", "toc"],
        extension_configs={"toc": {"toc_depth": "2-3", "slugify": slugify_unicode}},
    )
    markup = converter.convert(text)
    index = (
        '<details><summary>按项目浏览完整简历</summary>'
        f'<nav aria-label="简历目录">{converter.toc}</nav></details>'
    )
    markup = markup.replace("<h2 ", index + "<h2 ", 1)
    (ROOT / "resume.html").write_text(
        '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{html.escape(title)}</title>'
        f'<style>{CSS}</style></head><body><main>{markup}</main></body></html>\n',
        encoding="utf-8",
    )
    register_fonts()
    target = ROOT / "resume.pdf"
    doc = ResumeDocument(
        str(target), pagesize=A4, leftMargin=17 * mm, rightMargin=17 * mm,
        topMargin=15 * mm, bottomMargin=19 * mm,
        title=title, author="Zirui Qiu", subject="求职简历", pageCompression=1,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="resume")
    doc.addPageTemplates(PageTemplate(id="resume", frames=[frame], onPageEnd=footer))
    doc.build(make_flowables(text))
    print(f"Generated {target.name} ({target.stat().st_size:,} bytes) and resume.html")


if __name__ == "__main__":
    main()
