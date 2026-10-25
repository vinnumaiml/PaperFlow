# PaperFlow — Production-Ready All-in-One PDF Tools & Document Studio

PaperFlow is a high-performance, responsive, privacy-first online document utility platform. It provides a complete suite of 33 PDF operations covering document organization, optimization, conversion, editing, security, and document intelligence.

Every tool in PaperFlow performs a genuine operation backed by industry-standard document engines. There are no mock implementations, dummy spinners, or fake download buttons.

---

## Architecture Overview

```
PaperFlow/
├── frontend/                  # Next.js 16 App Router, React 19, TypeScript
│   ├── app/                   # Dynamic routes for all 33 tools, privacy, terms
│   ├── components/            # Design system, upload zone, canvas sign/editor, results
│   ├── lib/tools/registry.ts  # Single typed source of truth for tool catalogue
│   ├── lib/api/client.ts      # Typed API client with status polling
│   └── Dockerfile             # Multi-stage optimized production container
├── backend/                   # Python 3.12+ FastAPI backend & processing engine
│   ├── app/
│   │   ├── api/routes/        # REST endpoints: /api/jobs, /api/health, /api/tools
│   │   ├── core/              # Config, security sanitization, safe error handling
│   │   ├── services/pdf/      # Organize, optimize, edit, security, conversions
│   │   ├── services/office/   # LibreOffice & pure Python DOCX/PPTX/XLSX engines
│   │   ├── services/html/     # SSRF-sanitized HTML-to-PDF rendering
│   │   ├── services/ocr/      # Tesseract OCR & PyMuPDF searchable PDF engine
│   │   └── services/intelligence/ # AI summarizer, translator & pymupdf4llm Markdown
│   ├── tests/                 # Full automated test suite (Pytest & AsyncIO)
│   ├── requirements.txt       # Frozen Python dependencies
│   └── Dockerfile             # Full container with Ghostscript, Tesseract, LibreOffice
├── docker-compose.yml         # Production orchestration (Frontend, API, Redis)
├── .env.example               # Configuration template
└── README.md                  # Complete documentation
```

---

## Complete Tool Catalogue & Engine Mapping

| Category | Tool | Slug | Engine / Implementation |
|---|---|---|---|
| **Organize PDF** | Merge PDF | `merge-pdf` | PyMuPDF & pypdf |
| | Split PDF | `split-pdf` | PyMuPDF page range extractor |
| | Remove Pages | `remove-pages` | PyMuPDF page deleter |
| | Extract Pages | `extract-pages` | PyMuPDF page slicer (+ ZIP) |
| | Organize PDF | `organize-pdf` | PyMuPDF reorder, rotate & duplicate |
| | Scan to PDF | `scan-to-pdf` | Pillow & PyMuPDF page compiler |
| **Optimize PDF** | Compress PDF | `compress-pdf` | Real multi-pass search (PyMuPDF, pikepdf, Ghostscript) |
| | Repair PDF | `repair-pdf` | pikepdf xref recovery & qpdf |
| | OCR PDF | `ocr-pdf` | Tesseract OCR & PyMuPDF |
| **Convert to PDF** | JPG to PDF | `jpg-to-pdf` | Pillow & PyMuPDF |
| | Word to PDF | `word-to-pdf` | LibreOffice / python-docx & ReportLab |
| | PowerPoint to PDF | `powerpoint-to-pdf` | LibreOffice / python-pptx & ReportLab |
| | Excel to PDF | `excel-to-pdf` | LibreOffice / openpyxl & ReportLab |
| | HTML to PDF | `html-to-pdf` | SSRF-sanitized ReportLab HTML engine |
| **Convert from PDF** | PDF to JPG | `pdf-to-jpg` | PyMuPDF Pixmap renderer (+ ZIP) |
| | PDF to Word | `pdf-to-word` | python-docx & PyMuPDF |
| | PDF to PowerPoint | `pdf-to-powerpoint`| python-pptx slide layout engine |
| | PDF to Excel | `pdf-to-excel` | pdfplumber & openpyxl table extractor |
| | PDF to PDF/A | `pdf-to-pdfa` | pikepdf archival conformance engine |
| **Edit PDF** | Rotate PDF | `rotate-pdf` | PyMuPDF page rotation |
| | Add Page Numbers | `add-page-numbers` | PyMuPDF typography overlay |
| | Add Watermark | `add-watermark` | PyMuPDF opacity & vector overlay |
| | Crop PDF | `crop-pdf` | PyMuPDF CropBox bounds updater |
| | Edit PDF | `edit-pdf` | Interactive canvas annotations & text insertion |
| | PDF Forms | `fill-form` | PyMuPDF AcroForm reader, filler & flattener |
| **PDF Security** | Unlock PDF | `unlock-pdf` | pikepdf AES credential decryption |
| | Protect PDF | `protect-pdf` | pikepdf AES-256 standard encryption |
| | Sign PDF | `sign-pdf` | Canvas visual signing & raster embedding |
| | Redact PDF | `redact-pdf` | PyMuPDF deep irreversible redaction |
| | Compare PDF | `compare-pdf` | PyMuPDF visual diff heatmap & difflib text |
| **PDF Intelligence**| AI Summarizer | `ai-summarize` | NLP extractive & OpenAI adapter |
| | Translate PDF | `ai-translate` | Neural translation & ReportLab compiler |
| | PDF to Markdown | `pdf-to-markdown` | pymupdf4llm structural markdown extractor |

---

## Real Target-Size Compression Search Algorithm

PaperFlow's **Compress PDF** tool does not guess or artificially report numbers:
1. **Candidate Generation**: The compression engine evaluates multiple downsampling candidates across standard and aggressive profiles (DPIs: 200, 140, 110, 90, 72; JPEG quality: 85, 75, 60, 50, 35).
2. **Stream Compression & Cleaning**: Each candidate undergoes xref compaction, duplicate font elimination, and flate stream deflation.
3. **Byte Verification**: Each generated candidate is saved to an isolated workspace, validated with a real PDF parser, and its exact file size in bytes is measured.
4. **Optimal Selection**:
   - If a **custom target size** in KB was requested, the engine selects the highest-quality candidate whose actual size is $\le$ target.
   - If the target is physically unattainable without corrupting document structure, the engine selects the best safe candidate and honestly reports `target_achieved = False` with the exact reduction achieved.
   - If optimization would result in a file larger than the original, the original document is preserved.

---

## Deep Redaction Guarantee

Unlike tools that merely place black rectangles over text (leaving sensitive text extractable in the underlying PDF stream), PaperFlow's **Redact PDF** tool utilizes PyMuPDF's deep redaction pipeline:
1. Locates text bounding boxes and user coordinates.
2. Applies `page.add_redact_annot()`.
3. Calls `page.apply_redactions()`, which physically deletes underlying text glyphs, vector paths, and raster sections from the document.
4. An automated verification pass asserts that redacted terms are no longer extractable.

---

## Local Development Setup

### Prerequisites
- Node.js 20+ & npm
- Python 3.11+ (Python 3.12 or 3.14 recommended)

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run automated tests
pytest -v

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API docs will be available at `http://localhost:8000/docs` and readiness check at `http://localhost:8000/api/health`.

### 2. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run production build check
npm run build

# Start Next.js development server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## Docker Deployment (Production)

To run the complete stack with Ghostscript, Tesseract OCR, LibreOffice, and Redis in isolated containers:

```bash
# Copy and configure environment variables
cp .env.example .env

# Build and start all services
docker compose up -d --build

# View container logs
docker compose logs -f

# Verify API readiness
curl http://localhost:8000/api/health

# Stop containers
docker compose down
```

---

## Deployment & Cloud Publishing

PaperFlow is configured for instant cloud publishing across multiple hosting environments:

- **Netlify (Frontend)**: Zero-config deployment via root [`netlify.toml`](./netlify.toml) and [`frontend/public/_redirects`](./frontend/public/_redirects).
- **Vercel (Frontend)**: Ready out-of-the-box via root [`vercel.json`](./vercel.json) and [`package.json`](./package.json).
- **Render (Full-Stack Blueprint)**: 1-click deploy for both Python FastAPI backend and Next.js frontend via [`render.yaml`](./render.yaml).
- **GitHub Pages**: Automated static export workflow pre-configured via [`.github/workflows/deploy-pages.yml`](./.github/workflows/deploy-pages.yml).
- **Docker Compose**: Containerized multi-service deployment with Redis and system binaries via [`docker-compose.yml`](./docker-compose.yml).

👉 **For complete step-by-step instructions, see the [Deployment Guide (DEPLOYMENT.md)](./DEPLOYMENT.md).**

---

## Privacy, Security & Data Retention

- **Zero Global Writes**: Every job gets a dedicated temporary folder: `backend/data/temp/<job_id>/inputs` and `outputs`.
- **Automatic 60-Minute Purge**: An asynchronous background cleaner executes every 15 minutes to delete temporary files older than 60 minutes.
- **SSRF & LFI Protection**: HTML-to-PDF blocks local `file://` schemes and private IP ranges (`127.0.0.1`, `169.254.169.254`, `10.0.0.0/8`, `192.168.0.0/16`).
- **AI Privacy**: Document content is only sent to AI providers when an AI tool is explicitly initiated by the user.

---

## Dependency & Licensing Notes

PaperFlow adopts permissive and document-standard libraries:
- **PyMuPDF**: Licensed under GNU AGPL v3 / Commercial. For commercial closed-source SaaS distributions, obtain an Artifex commercial license or utilize pypdf/pikepdf fallback paths.
- **pypdf**: BSD 3-Clause license.
- **pikepdf**: Mozilla Public License 2.0 (MPL-2.0).
- **python-docx & python-pptx**: MIT license.
- **openpyxl**: MIT license.
- **Tesseract OCR**: Apache 2.0 license.
- **Ghostscript**: AGPL v3 / Commercial.
