# Format Conversion

Raw source files must be in markdown before ingestion. This document covers how to detect format, convert, and verify each type.

---

## Supported Formats

| Format | Extension(s) | Primary tool | Fallback |
|--------|-------------|-------------|---------|
| Markdown | `.md` | No conversion needed | — |
| MHTML / MHT | `.mhtml`, `.mht` | `scripts/mhtml_to_md.py` | pandoc, BeautifulSoup+html2text |
| HTML | `.html`, `.htm` | `scripts/html_to_md.py` | pandoc |
| PDF (text-based) | `.pdf` | pymupdf / fitz | pdftotext |
| SRT (subtitles) | `.srt` | pandoc | Python strip script |
| EPUB | `.epub` | pandoc | unzip + pandoc on extracted HTML |

**Not in the table = unknown format.** If you encounter an extension not listed here, jump to the "Unknown Format Handling" section at the bottom of this file. Do NOT invent a conversion.

---

## Check for Existing Scripts First

Before using any conversion tool, check whether conversion scripts already exist in the repo's `scripts/` directory. Real-world wikis maintain their own scripts tailored to their source formats.

```
<repo-root>/scripts/mhtml_to_md.py   — MHTML conversion (Substack, Obsidian Web Clipper)
<repo-root>/scripts/html_to_md.py    — HTML conversion (book readers, web pages)
```

If these scripts exist, prefer them over generic tools. They strip site-specific chrome (navigation bars, footers, Substack boilerplate) that generic tools leave behind.

---

## Where Do Converted Files Go?

The immutability rule ("never modify raw/") conflicts with the practical need to write converted `.md` files somewhere. Resolution:

**Converted `.md` files ARE allowed in `raw/`, alongside their source.** They are conversion artifacts, not modifications of existing raw files. The rule prohibits EDITING existing raw files, not CREATING new ones derived from them.

### Placement rules

| Source location | Converted file location |
|---|---|
| `raw/newsletters/article.mhtml` | `raw/newsletters/article.md` (same directory) |
| `raw/book-chapters/05-rate-limiter.html` | `raw/book-chapters/05-rate-limiter.md` (same directory) |
| `raw/books/design-patterns.pdf` | `raw/books/design-patterns.md` (same directory) OR `raw/books/design-patterns/chapter-*.md` for chapter-split books |
| `raw/notion-export/.../Research.md` (already markdown) | No conversion needed |

### Rules for converted files

1. **Keep the original.** Never delete the source (`.mhtml`, `.html`, `.pdf`, etc.) — the raw immutability rule means the original stays forever.
2. **Mirror the filename.** `article.mhtml` → `article.md` (same base name, different extension). This makes it obvious which conversion produced which file.
3. **Place in the same directory** as the source. Do not create a separate `converted/` subdirectory — it fragments the source location.
4. **The `.md` file is the one you cite in wiki frontmatter.** The `sources` field in wiki pages should reference the `.md` file (`raw/newsletters/article.md`), not the original source file. The original stays as a provenance backup.
5. **If re-running conversion** (e.g., script was improved), the `.md` file may be overwritten. This is the ONE case where a file in `raw/` may be replaced — and only by re-running the same conversion on the unchanged source.

### Anti-patterns

- **Do NOT** write converted `.md` files to `wiki/source-summaries/` directly. Those are wiki pages that cite raw sources, not raw sources themselves.
- **Do NOT** delete the original after conversion. Immutability means the original stays even if ignored.
- **Do NOT** create a parallel directory structure like `raw-converted/` that mirrors `raw/`. Keep everything in one place.
- **Do NOT** rename converted files to obscure the relationship to the source (e.g., `article-converted.md`). The base name should match.

---

## MHTML / MHT

### Detection

File extension `.mhtml` or `.mht`. Common sources:
- Substack articles saved via Obsidian Web Clipper
- Any web page saved as "Web Archive, Single File" in a browser

### Conversion with existing script

```bash
# Single file
python scripts/mhtml_to_md.py --input raw/newsletters/article.mhtml --output raw/newsletters/article.md

# Entire directory (recursive, mirrors structure)
python scripts/mhtml_to_md.py --input raw/newsletters/2024/ --output raw/newsletters/2024/

# Dry run to see what would be converted
python scripts/mhtml_to_md.py --input raw/newsletters/2024/ --output raw/newsletters/2024/ --dry-run

# Overwrite existing .md files
python scripts/mhtml_to_md.py --input raw/newsletters/2024/ --output raw/newsletters/2024/ --force
```

The script strips embedded data: URI images (which produce unusable output), strips Substack chrome, and collapses excess blank lines.

### Fallback (no script available)

```bash
pandoc input.mhtml -f html -t markdown -o output.md
```

### Post-conversion checks (CRITICAL)

After converting MHTML files, ALWAYS spot-check at least 3 converted files before ingesting. Auth-wall stubs are the biggest risk.

**Auth-wall stub signatures** (skip these, flag for re-download):
- File is under ~1,000 characters
- Content contains: "Update your profile", "Check your email", "Sign in to continue", "This post is for paid subscribers"
- Body is only navigation links and a sign-in prompt
- No substantive paragraphs in the first 50 lines

**Legitimate content signatures**:
- Multiple content sections with prose
- Technical vocabulary present
- Usually 3,000+ characters

```bash
# Quick size check to find likely stubs
wc -c raw/newsletters/2024/*.md | sort -n | head -20
```

Any file under ~1,000 bytes after conversion is a likely stub. Read it before ingesting.

---

## HTML

### Detection

File extension `.html` or `.htm`. Common sources:
- Alex Xu book reader exports (chapter HTML files)
- Web pages saved as HTML

### Conversion with existing script

```bash
# Single file
python scripts/html_to_md.py --input raw/book-chapters/05-rate-limiter.html --output raw/book-chapters/05-rate-limiter.md

# Directory (top-level only by default)
python scripts/html_to_md.py --input raw/book-chapters/ --output raw/book-chapters/

# Directory recursive
python scripts/html_to_md.py --input raw/book-chapters/ --output raw/book-chapters/ --recursive

# Force overwrite
python scripts/html_to_md.py --input raw/book-chapters/ --output raw/book-chapters/ --force
```

The script detects charset from `<meta>` tags, strips book reader chrome, and preserves image URLs (unlike the MHTML script which strips data: URIs).

### Fallback (no script available)

```bash
pandoc input.html -f html -t markdown -o output.md
```

For sites with heavy JavaScript rendering, pandoc may produce thin output. In that case, try:
1. Saving the rendered page from the browser (File → Save As → Web Page, HTML Only)
2. Then running the conversion on the saved HTML

### Post-conversion checks

- Verify that code blocks are preserved (look for triple backtick fences)
- Check that tables converted correctly
- Verify that images are referenced as `![alt](url)` syntax, not broken

---

## PDF

### Detection

File extension `.pdf`. Two types:

| Type | Description | Conversion approach |
|------|-------------|---------------------|
| Text-based | Created from a word processor or typesetting tool (most technical books) | pymupdf text extraction |
| Scanned image | Photographed or scanned pages (older academic papers) | OCR required — out of scope |

### Detecting if text extraction will work

Open the PDF in any viewer and try to select text. If you can select individual characters, text extraction will work. If selection grabs whole blocks or fails, the PDF is likely scanned.

### Conversion with pymupdf / fitz

```python
import fitz  # pymupdf

doc = fitz.open("raw/System Design Archive 2022.pdf")

# Extract all text
full_text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    full_text += page.get_text()

# Or extract specific page ranges
for page_num in range(10, 20):  # pages 11-20
    page = doc[page_num]
    print(page.get_text())
```

Install: `pip install pymupdf`

### Fallback tools

```bash
# pdftotext (poppler-utils)
pdftotext -layout input.pdf output.txt

# pandoc (handles some PDFs)
pandoc input.pdf -o output.md
```

### Post-conversion checks

- Verify that headings are preserved (they often become bold text, not H1/H2 — fix manually if needed)
- Code blocks in technical PDFs often lose formatting — check and restore triple backticks
- Table extraction is unreliable in PDFs — verify tables manually
- For visual archive PDFs (infographics, diagrams): text extraction gives topic context only. Note in the source summary that the primary content is visual and cannot be extracted via text.

### Scanned PDFs

If text extraction returns empty or garbled text, the PDF is scanned. OCR is required and is out of scope for standard ingest. Options:
- Use Adobe Acrobat's OCR feature (if available)
- Use `ocrmypdf` CLI tool
- Skip and note in the log: `[SKIP] PDF appears to be scanned; OCR required`

---

## SRT (Subtitles)

### Detection

File extension `.srt`. Common sources:
- YouTube auto-generated captions downloaded
- Video course subtitles

### SRT format

SRT files contain numbered blocks of: sequence number, timestamp, text. Example:
```
1
00:00:01,000 --> 00:00:04,500
Welcome to this lecture on system design.

2
00:00:04,500 --> 00:00:08,000
Today we will cover rate limiting algorithms.
```

### Conversion with pandoc

```bash
pandoc input.srt -t markdown -o output.md
```

### Python fallback (strip timestamps manually)

```python
import re

def srt_to_text(srt_path: str) -> str:
    with open(srt_path, encoding="utf-8") as f:
        content = f.read()

    # Remove sequence numbers (lines that are just digits)
    # Remove timestamp lines (00:00:01,000 --> 00:00:04,500)
    # Collapse multiple blank lines
    lines = content.splitlines()
    text_lines = []
    for line in lines:
        if re.match(r"^\d+$", line.strip()):
            continue  # sequence number
        if re.match(r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$", line.strip()):
            continue  # timestamp
        text_lines.append(line)

    # Join and collapse blank lines
    text = "\n".join(text_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
```

### Post-conversion checks

- SRT text has no paragraph structure — the conversion produces a wall of short lines
- Manually add paragraph breaks at natural topic transitions before ingesting
- Filler words ("um", "uh", "like") should be removed for readability
- Speaker identification lines (if present) should be removed or converted to bold headers

---

## Markdown (No Conversion Needed)

If the file is already `.md`, skip format conversion entirely and proceed to triage (SKILL.md Step 0).

However, check for these issues that may require cleanup before ingest:

1. **Obsidian-specific syntax** — Files clipped with Obsidian Web Clipper may contain `![[image.png]]` internal image links that will not render on other platforms. This is fine if staying in Obsidian.
2. **Frontmatter from clipping tools** — Obsidian Web Clipper adds its own frontmatter. This does not conflict with the wiki's frontmatter conventions but should be reviewed.
3. **Broken image URLs** — Clipped articles sometimes have images that load from CDNs that may expire. Flag these in the source summary if relevant.

---

## Script Templates for Fresh Repos

If the repo has no conversion scripts yet (no `scripts/` directory), use these templates.

### MHTML conversion (minimal)

```python
"""minimal_mhtml_to_md.py — convert a single MHTML file to markdown"""
import email
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    import html2text
except ImportError:
    print("pip install beautifulsoup4 html2text")
    sys.exit(1)

def convert(src: Path, dst: Path) -> None:
    raw = src.read_bytes()
    msg = email.message_from_bytes(raw)
    html_part = None
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_part = part
            break
    if html_part is None:
        raise ValueError(f"No HTML part in {src}")

    payload = html_part.get_payload(decode=True)
    charset = html_part.get_param("charset") or "utf-8"
    html = payload.decode(charset, errors="replace")

    soup = BeautifulSoup(html, "html.parser")
    # Remove common boilerplate
    for tag in soup.select("nav, footer, header, script, style, [role=navigation]"):
        tag.decompose()

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True  # strip data: URI images
    h.body_width = 0  # no line wrapping
    md = h.handle(str(soup))
    dst.write_text(md, encoding="utf-8")
    print(f"Converted: {src} -> {dst}")

if __name__ == "__main__":
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
```

### HTML conversion (minimal)

```python
"""minimal_html_to_md.py — convert a single HTML file to markdown"""
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    import html2text
except ImportError:
    print("pip install beautifulsoup4 html2text")
    sys.exit(1)

def convert(src: Path, dst: Path) -> None:
    raw = src.read_bytes()
    # Sniff charset from meta tags
    head = raw[:4096].decode("ascii", errors="replace")
    import re
    m = re.search(r'charset=["\']?([a-zA-Z0-9_-]+)', head, re.I)
    charset = m.group(1) if m else "utf-8"
    html = raw.decode(charset, errors="replace")

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.select("nav, footer, header, script, style"):
        tag.decompose()

    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False  # preserve real image URLs
    h.body_width = 0
    md = h.handle(str(soup))
    dst.write_text(md, encoding="utf-8")
    print(f"Converted: {src} -> {dst}")

if __name__ == "__main__":
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
```

---

## EPUB

### Detection

File extension `.epub`. Common sources:
- Ebook exports from Calibre, Apple Books, O'Reilly, Leanpub
- Technical books distributed in DRM-free EPUB format

### Conversion with pandoc

```bash
pandoc input.epub -t markdown -o output.md
```

Pandoc handles EPUB natively. It preserves chapter structure (mapped to `#` headings), images (referenced as `![alt](media/image.png)` — may need separate extraction), and code blocks.

### Chapter splitting for book-sized EPUBs

A 500-page technical book EPUB should not become one giant wiki page. Extract the table of contents and split into chapter files:

```bash
# Extract the EPUB (it's a zip archive)
mkdir extracted && unzip input.epub -d extracted/

# The OPF file at extracted/OEBPS/content.opf (or similar) lists the spine in reading order.
# Each spine item is an HTML file representing a chapter.
# Convert each chapter file individually:
for chapter in extracted/OEBPS/*.html; do
  name=$(basename "$chapter" .html)
  pandoc "$chapter" -f html -t markdown -o "raw/book-title/chapter-${name}.md"
done
```

This produces one markdown file per chapter, which then flows naturally into the batch ingest pipeline.

### Image extraction

EPUB images are usually in `OEBPS/images/` or `OEBPS/media/` inside the zip. Copy them to a known location and update the markdown references:

```bash
cp -r extracted/OEBPS/images raw/book-title/assets/
```

### Post-conversion checks

- Verify chapter count matches the book's TOC
- Check that code blocks in technical books preserved their fences (pandoc usually handles this well)
- Verify that tables converted — EPUB tables sometimes use `<table>` and sometimes CSS grids; the latter may produce broken markdown
- For scanned EPUBs (image-only pages), OCR is required — handle the same way as scanned PDFs

### When pandoc fails on EPUB

Some EPUBs use non-standard or encrypted packaging. If `pandoc` errors or produces empty output:
1. Try `unzip -l input.epub` to verify the archive is valid
2. Extract manually and convert chapter HTML files individually
3. If the EPUB is DRM-protected, the user must unlock it first (out of scope)

---

## Unknown Format Handling

**This section is the mandatory fallback when an extension is not in the Supported Formats table above.**

When the pre-flight assessment (SKILL.md Step -1) finds a file with an unrecognized extension, do NOT silently skip or invent a conversion. Follow this procedure:

### Step 1: Identify the file type

```bash
# Linux/Mac: use the file(1) command to inspect magic bytes
file path/to/mystery-file.xyz

# Windows (Git Bash): also has file(1) via MSYS
file path/to/mystery-file.xyz

# Python fallback if `file` is unavailable
python -c "
with open('path/to/mystery-file.xyz', 'rb') as f:
    header = f.read(16)
print('Magic bytes:', header.hex())
print('ASCII:', header.decode('latin-1', errors='replace'))
"
```

Common magic byte signatures:

| Header (hex) | Format |
|---|---|
| `504b 0304` | ZIP archive (DOCX, XLSX, PPTX, EPUB, JAR are all ZIP-based) |
| `2550 4446` | PDF (`%PDF`) |
| `d0cf 11e0` | Legacy MS Office (DOC, XLS, PPT) |
| `1f8b 0800` | GZIP |
| `7b22` (`{"`) | JSON (likely text) |
| `3c21 444f 4354 5950 45` | HTML (`<!DOCTYPE`) |
| `3c3f 786d 6c` | XML (`<?xml`) |

### Step 2: Check pandoc's supported input formats

```bash
pandoc --list-input-formats
```

If the identified format is in pandoc's list (common ones: `docx`, `odt`, `epub`, `rst`, `org`, `textile`, `mediawiki`, `latex`, `opml`), pandoc can likely convert it:

```bash
pandoc input.docx -t markdown -o output.md
```

### Step 3: Ask the user before proceeding

Produce a report like:

```markdown
## Unknown Format Decision Needed

File: raw/mystery-file.xyz
- Magic bytes: 504b0304 (ZIP archive)
- Likely format: DOCX / EPUB / ZIP container (need to inspect contents)
- Pandoc support: yes (if DOCX or EPUB)

File: raw/sample-book.epub
- Magic bytes: 7b2274 (starts with `{"t`)
- Likely format: JSON (not a real EPUB — renamed or stub)
- Pandoc support: N/A

Options:
1. SKIP both files — log as "unsupported format"
2. For mystery-file.xyz: try `pandoc -f docx`. For sample-book.epub: inspect JSON content, treat as text
3. Tell me what these files are supposed to be and I'll add handling to the skill

What would you like me to do?
```

### Step 4: If the user says "add to skill"

Do not make up a format section. Ask the user:
1. What is the canonical format name?
2. Is there a preferred tool (pandoc? a custom script? a Python library?)?
3. What are the known edge cases or gotchas?

Then add a new section to format-conversion.md following the same structure as the existing format sections (Detection, Conversion, Post-conversion checks, Edge cases).

### Step 5: If the user says "try generic conversion"

1. Run `pandoc -f <format> input.xxx -o output.md` with a reasonable guess at the format
2. Spot-check the output for length and readability
3. If the output looks good, proceed with ingest BUT flag in the log: "Converted via unverified pandoc fallback — spot-check before trusting"
4. If the output is garbled or empty, stop and report back to the user

### Step 6: Never silently skip

Unknown format files must ALWAYS be reported to the user. A silent skip means the user later discovers that files they added were never ingested, which erodes trust in the skill. Prefer stopping with a question over silently dropping files.

---

## Conversion Script Failure Detection

**Learned from real testing:** Existing conversion scripts (like a custom `mhtml_to_md.py`) can silently produce broken output. The garen-wiki Substack MHTML conversion produced 32-byte stub files because the CSS selectors didn't match Substack's current HTML structure.

### Always spot-check after running a conversion script

After ANY conversion, before ingesting the result:

```bash
# Quick size sanity check — anything under 500 bytes is suspect
wc -c raw/converted-file.md

# Quick content check — should see prose paragraphs, not just boilerplate
head -20 raw/converted-file.md
```

### Signals that a conversion script failed

- Output file under 500 bytes
- Output contains only navigation/footer/boilerplate text
- Output contains "Sign in", "Subscribe", "Update your profile" (auth-wall leaked through)
- Output is missing the article title or body content
- Output has HTML tags visible in the markdown (conversion didn't process them)

### Fallback when the script fails

1. Inspect the raw source file manually to confirm it has content
2. Try the minimal BeautifulSoup+html2text template in this file (see Script Templates section below)
3. If that also fails, try pandoc directly
4. Report the failure to the user so they know to update or replace the script

---

## Edge Cases

**Mixed-format directories:** A `raw/newsletters/2024/` directory may contain both `.mhtml` and `.md` files (articles already converted manually). Run the conversion script with `--dry-run` first to see what would be processed. Existing `.md` files are skipped by default (no `--force`).

**Encoding issues:** If a conversion produces garbled text (e.g., `Ã©` instead of `é`), the source charset declaration was wrong or missing. Try re-decoding with `latin-1`:
```bash
iconv -f latin-1 -t utf-8 input.html -o input-utf8.html
```

**Very large files:** PDFs over 50 MB may be slow to process with pymupdf. For archive PDFs (visual reference only), consider processing in page-range batches rather than all at once.

**Password-protected PDFs:** If `fitz.open()` raises an error about encryption, the PDF is password-protected. Ask the user for the password or skip the file.
