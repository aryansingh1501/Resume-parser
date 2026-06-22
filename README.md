# AI Resume Parser with Skill Gap Analyzer

A portfolio-ready Streamlit app that extracts structured data from PDF/DOCX resumes and compares your skills against a job description.

## Folder Structure

```
resume-parser/
├── app.py                      # Streamlit dashboard (main entry point)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── data/
│   └── skills_glossary.json    # Skill aliases + Hinglish keyword support
└── src/
    ├── __init__.py
    ├── file_reader.py          # PDF (PyMuPDF) and DOCX (python-docx) readers
    ├── resume_parser.py        # spaCy + regex extraction logic
    ├── skills_glossary.py      # Glossary loader and skill matching
    ├── job_matcher.py          # Match score and skill gap analysis
    └── utils.py                # JSON export and UI helpers
```

## How to Run Locally

### 1. Open a terminal in the project folder

```bash
cd "C:\Users\Aryan Singh\resume-parser"
```

### 2. Create a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the spaCy English model

spaCy needs a language model for name detection (NER):

```bash
py -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

If `python -m spacy download en_core_web_sm` fails on Windows, use the pip command above instead.

### 5. Start the app

```bash
streamlit run app.py
```

Your browser should open at `http://localhost:8501`.

## How to Use

1. Upload a **PDF** or **DOCX** resume.
2. Paste a **job description** in the text box.
3. Click **Analyze Resume & Match Skills**.
4. Review the dashboard: contact info, skills, education, experience, match score, and skill gaps.
5. Click **Download Parsed Resume (JSON)** to save results.

## Sample Output Explanation

Suppose you upload a resume with skills: `Python`, `Machine Learning`, `Git`, `SQL`  
and paste a job asking for: `Python`, `SQL`, `Docker`, `AWS`, `Machine Learning`.

| Field | Example Output | Meaning |
|-------|----------------|---------|
| **Match Score** | `60% — Moderate Match` | 3 of 5 required skills found → yellow badge |
| **Matched Skills** | Python, SQL, Machine Learning | Skills you already have for this role |
| **Skill Gaps** | Docker, Aws | Skills mentioned in the JD but missing from resume |
| **Name / Email / Phone** | Extracted via spaCy + regex | Basic contact parsing |
| **Education** | Lines with B.Tech, University, etc. | Keyword-based section detection |
| **JSON Download** | Full structured export | Useful for APIs, portfolios, or further analysis |

### Color-coded match score

| Score | Color | Label |
|-------|-------|-------|
| 0–49% | Red | Low Match |
| 50–74% | Yellow | Moderate Match |
| 75–100% | Green | Strong Match |

## Hinglish Skill Support

The glossary in `data/skills_glossary.json` recognizes:

- Abbreviations: **ML**, **AI**, **DS**, **NLP**, **K8s**
- Mixed phrasing: "data sci", "gen ai", "full stack"
- Common student resume phrases: "b.tech", "cse", "internship experience"

You can extend the glossary by adding more aliases under any canonical skill name.

## Brief Explanation of Complex Parts

### spaCy (NLP)

spaCy reads text and finds entities like **person names**. We use the small English model `en_core_web_sm` because it is fast and good enough for resumes.

### PyMuPDF

Reads PDF files page by page and pulls out plain text. Many resumes are PDFs, so this is the first step before parsing.

### Skill matching (not magic AI)

We match skills using a **glossary of keywords**, not a black-box neural network. This is transparent, fast, and easy to customize — great for a student portfolio project.

### Match score formula

```
match_score = (number of matched skills / number of skills in job description) × 100
```

Simple and explainable in interviews.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `spaCy model not found` | Run `python -m spacy download en_core_web_sm` |
| No skills detected | Add a clear "Skills" section with standard keywords |
| Name not found | Put your name on the first line of the resume |
| `.doc` not supported | Save as `.docx` in Word/Google Docs |

## Tech Stack

- **Python** — core language
- **Streamlit** — web UI
- **spaCy** — NLP / name extraction
- **PyMuPDF** — PDF reading
- **python-docx** — DOCX reading
- **pandas** — tabular skill display

## License

Free to use for learning and portfolio projects.
