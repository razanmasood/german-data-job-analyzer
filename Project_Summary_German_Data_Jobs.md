# German Data Jobs Analyzer

## Project Overview

### What This Is
An end-to-end NLP pipeline that analyzes 1,240 real German data science job postings to extract in-demand skills and visualize market trends. The project demonstrates modern ML engineering practices by combining LLM-assisted annotation with fine-tuned multilingual transformers for Named Entity Recognition.

### Why This Matters

**For the German job market:**
- Provides data-driven insights into what skills employers actually want
- Identifies skill combinations that appear together (e.g., "Python + AWS + Docker")
- Reveals seniority expectations through existing LinkedIn data
- Helps job seekers prioritize which skills to develop

**For portfolio demonstration:**
- Shows end-to-end ML engineering: data collection → annotation → model training → deployment
- Demonstrates practical use of transformers (not just API calls)
- Highlights multilingual NLP capability (German + English)
- Shows modern workflow: LLM pre-annotation + human review (hybrid approach)
- Proves ability to work with messy real-world data
- Makes smart scope decisions (using existing data vs. building unnecessary models)

### How It Works

**Input:** Raw job posting text
```
"Wir suchen einen Data Scientist mit Python, SQL und Machine Learning Erfahrung..."
```

**Processing Pipeline:**
1. **LLM Pre-annotation**: Llama 3.1 8B extracts candidate skills/tools
2. **Human Review**: Manual correction in Label Studio
3. **NER Training**: Fine-tune xlm-roberta-large on corrected annotations
4. **Seniority Data**: Use existing LinkedIn experienceLevel field (no classifier needed)
5. **Analysis**: Extract skills from all 1,240 postings

**Output:** Interactive Streamlit dashboard showing:
- Top 20 most requested skills and tools
- Skill co-occurrence patterns (what skills appear together)
- Seniority distribution across roles (from existing data)
- Trends in the German DS/ML job market

### Tech Highlights
- **Multilingual**: Handles both German and English postings (reflects real market)
- **Hybrid annotation**: LLM does 80% of work, human ensures quality
- **Production-grade**: Containerized, version-controlled, reproducible
- **Local-first**: Fine-tuning runs on MacBook (no cloud costs)
- **Smart scoping**: Uses existing data when available instead of building unnecessary models

## 🎯 Current Step

**Next action:** Continue with Day 5 - LLM Pre-annotation

---

## ✅ Progress Tracker

### Phase 0: Setup (2 days) — ✓ COMPLETE
- [x] Create GitHub repo
- [x] Set up Dev Container (reuse pattern from Project 1)
- [x] Create project structure
- [x] Verify environment works

### Phase 1: Data Collection (3 days) — ✓ COMPLETE
- [x] Research job posting sources (StepStone, Indeed.de, LinkedIn)
- [x] Build scraper OR find existing dataset
- [x] Collect 500+ German DS/ML job postings (1,240 collected via Octoparse)
- [x] Store raw data in structured format
- [x] Verify: have enough data to proceed
- [x] Analyze experienceLevel field (decision: use existing data, no classifier needed)

### Phase 2: Annotation + NER Fine-tuning (6 days)
- [x] Define entity types (SKILL, TOOL)
- [x] Install Ollama + Llama 3.1 8B locally
- [x] Sample 150 job postings for annotation
- [x] Create annotation prompt for LLM
- [x] Run LLM pre-annotation on 150 postings ← **CURRENT STEP**
- [x] Set up Label Studio for review/correction
- [x] Review and correct LLM annotations (150 postings)
- [x] Prepare data in NER format (IOB tagging)
- [ ] Fine-tune xlm-roberta-large for NER
- [ ] Evaluate: F1 score on held-out test set

### Phase 3: Data Processing (2 days)
- [ ] Build inference pipeline for NER
- [ ] Process all 1,240 job postings with NER model
- [ ] Extract experienceLevel data and standardize categories
- [ ] Analyze skill co-occurrence patterns
- [ ] Save processed results

**Note:** Using existing experienceLevel field from dataset — no seniority classifier training needed

### Phase 4: Analysis + Dashboard (3 days)
- [ ] Build Streamlit dashboard
- [ ] Show: top skills, skill co-occurrence, seniority distribution
- [ ] Add interactive features (filters, text input)
- [ ] Verify: dashboard tells a story

### Phase 5: Finish (2 days)
- [ ] Write README (German + English)
- [ ] Clean up code
- [ ] Push to GitHub
- [ ] Add to CV/portfolio

**When all boxes are checked, the project is DONE.**

---

## One-Sentence Summary

Fine-tune a multilingual NER model to extract skills from 1,240 German/English data science job postings and visualize market trends with an interactive dashboard.

---

## What You're Building (Input → Output)

### Input
Raw German or English job posting text, e.g.:
```
Wir suchen einen erfahrenen Data Scientist (m/w/d) mit 
3+ Jahren Erfahrung in Python und Machine Learning. 
Kenntnisse in AWS und Docker sind von Vorteil.
```

### What Happens Inside
1. Fine-tuned NER extracts: [Python: TOOL], [Machine Learning: SKILL], [AWS: TOOL], [Docker: TOOL]
2. Experience level read from existing data: "Mid-Senior level"
3. Results aggregated across all 1,240 postings

### Output
Dashboard showing:
- Most requested skills/tools (bar chart)
- Skill co-occurrence (what's requested together)
- Seniority distribution (from existing data)
- Interactive filtering by experience level
- Text input to analyze custom job postings

---

## Why This Project

**Portfolio value:**
- Fine-tuning a transformer model (not just using APIs)
- German + English NLP (differentiator in German job market)
- Custom NER (real NLP engineering, not just sentiment analysis)
- End-to-end: data collection → model training → visualization
- Smart scope management (knowing when NOT to build something)

**Practical value:**
- You'll actually learn what skills to emphasize
- Good talking point in interviews: "I analyzed 1,240 job postings and found..."
- Market insights you can use in applications

---

## Tech Stack

### Models
| Component | Choice | Reason |
|-----------|--------|--------|
| Base model | `xlm-roberta-large` | Multilingual BERT, handles both German & English |
| NER framework | Hugging Face Transformers | Industry standard, you know it |
| Seniority data | Use existing `experienceLevel` field | 100% filled, clean data - no classifier needed |

### Infrastructure
| Component | Choice | Reason |
|-----------|--------|--------|
| LLM annotation | Llama 3.1 8B (via Ollama) | Local, free, good for pre-annotation |
| Annotation review | Label Studio (local Docker) | Free, good NER support |
| Dashboard | Streamlit | Fast to build, looks professional |
| Data storage | JSON files | Simple, no infrastructure needed |
| Development | Docker + Dev Containers | Same as Project 1 |

### Compute
- Fine-tuning: Your M4 MacBook (32GB RAM is plenty for BERT)
- No cloud needed for training

---

## Data Description

### Dataset Overview
- **Source**: LinkedIn job postings collected via Octoparse web scraping tool
- **Collection period**: January 2026
- **Total unique jobs**: 1,240 (after deduplication by job ID)
- **Original sources**:
  - ds_jobs.csv: 400 Data Scientist positions
  - ml_jobs.csv: 1,000 Machine Learning positions
  - Combined with significant overlap removed

### Language Distribution
- **English descriptions**: 690 jobs (55.6%)
- **German descriptions**: 550 jobs (44.4%)
- **Note**: High percentage of English reflects international tech job market in Germany

### Data Fields
Each job posting contains:
- `title`: Job title
- `description`: Full job description text (primary field for NER)
- `descriptionHtml`: HTML version of description
- `experienceLevel`: Entry level, Associate, Mid-Senior level, Director, Executive, Internship, Not Applicable
- `location`: Job location
- `companyName`, `companyUrl`: Company information
- `salary`, `benefits`, `contractType`: Compensation details (often sparse)
- `publishedAt`: Posting date
- `jobUrl`, `applyUrl`: Application links
- `sector`, `jobCategory`: Job classification
- Other metadata fields

### Experience Level Distribution (From Actual Data)
```
Mid-Senior level: 708 (50.9%)
Entry level: 293 (21.0%)
Associate: 169 (12.1%)
Internship: 109 (7.8%)
Not Applicable: 81 (5.8%)
Director: 25 (1.8%)
Executive: 7 (0.5%)
```

**Key insight:** This field is 100% filled and uses LinkedIn's standardized taxonomy. No classifier needed - we'll use this data directly.

### Data Quality
- **Description field**: 100% filled (1,240/1,240)
- **Experience level**: 100% filled (1,240/1,240) with clean, consistent values
- **Company information**: Nearly complete
- **Salary information**: Sparse (typical for German market)

### Privacy & Ethics
- Data is publicly posted job listings
- No personal candidate information collected
- Data stored locally, not shared publicly
- Only aggregated insights (skills, trends) will be shared in final output
- Complies with LinkedIn's publicly accessible data policy

---

## Entity Types for NER

| Entity | Example | Notes |
|--------|---------|-------|
| SKILL | Machine Learning, NLP, Statistik | Technical abilities |
| TOOL | Python, AWS, Docker, TensorFlow | Specific technologies |

**Scope decision:** Starting with SKILL and TOOL only. These are the most valuable for job seekers and clearly distinguishable. Other entities (EXPERIENCE, EDUCATION, etc.) can be added in future iterations if needed.

---

## Scope Boundaries

### In scope
- Multilingual job postings (German & English)
- Data Scientist / ML Engineer / AI roles
- NER for skill/tool extraction
- Use existing experienceLevel data (no classification)
- Simple Streamlit dashboard
- 1,240 job postings

### Out of scope (do NOT add)
- ❌ Seniority level classifier (using existing experienceLevel field instead - SCOPE CHANGE Feb 4)
- ❌ Salary prediction model (too complex)
- ❌ Job recommendation system
- ❌ Real-time scraping
- ❌ Company analysis
- ❌ Geographic analysis
- ❌ Additional entity types beyond SKILL and TOOL

---

## Scope Change Log

### February 4, 2026 — Removed Seniority Classifier
**Decision:** Use existing `experienceLevel` field from dataset instead of training a classifier.

**Rationale:**
- LinkedIn's experienceLevel field is 100% filled (0% missing)
- Uses standardized categories (7 distinct values, no variants)
- Clean distribution matches expected job market
- Saves ~1 day of work (annotation + training + evaluation)

**Impact:**
- Removes classifier training from schedule (old Day 11)
- Frees up time for NER polish and earlier job applications
- Still demonstrates NLP skills through NER (the core value)
- Shows good engineering judgment (don't build what you don't need)

**Updated timeline:** Project still finishes in 3 weeks, with more buffer time.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Annotation takes too long | Start with 150 postings, increase only if time permits |
| NER performance is poor | 60-70% F1 is acceptable for portfolio - document challenges |
| Fine-tuning too slow on laptop | Use smaller model (`xlm-roberta-base`), reduce batch size |
| LLM annotation quality varies | Human review step catches and corrects errors |

---

## Timeline

**Target: 3 weeks** (with buffer built in)

| Week | Focus |
|------|-------|
| Week 1 | Setup + Data collection + Annotation (Days 1-7) |
| Week 2 | NER training + Data processing (Days 8-12) |
| Week 3 | Dashboard + Documentation + Ship (Days 13-15) |

Detailed daily schedule in `German_Data_Jobs_Schedule.md`.

---

## Definition of Done (MVP)

The project is **complete** when:

1. ✓ 150+ job postings annotated for NER
2. ✓ Fine-tuned German NER model with documented F1 score
3. ✓ Experience level distribution analyzed and documented
4. ✓ All 1,240 postings processed with NER pipeline
5. ✓ Streamlit dashboard shows skill analysis and seniority trends
6. ✓ README explains methodology and results (English + German)
7. ✓ Code is clean and on GitHub
8. ✓ Can demo in under 5 minutes

**Everything beyond this is a separate project.**

---

## Project Structure

```
german-data-job-analyzer/
├── data/
│   ├── raw/                        # Original scraped data
│   │   ├── ds_jobs.csv             # 400 Data Scientist postings (Octoparse)
│   │   ├── ml_jobs.csv             # 1,000 ML Engineer postings (Octoparse)
│   │   └── jobs_combined.json      # Deduplicated combined dataset (1,240 jobs)
│   ├── annotation/                 # LLM pre-annotation data
│   │   ├── sample_150.json         # 150 sampled postings for annotation
│   │   └── test_prompt_results.json# Prompt testing output
│   └── processed/                  # Analysis outputs
│       └── experience_level_analysis.json  # experienceLevel field analysis
├── scripts/                        # Numbered pipeline scripts
│   ├── 01_combine_data.py          # Combine & deduplicate raw CSVs
│   ├── 02_analyze_experience_level.py  # experienceLevel analysis & recommendation
│   ├── 03_check_languages.py       # Detect language of job descriptions
│   ├── 03_sample_data.py           # Sample 150 postings for annotation
│   ├── 04_test_prompt.py           # Test LLM annotation prompt
│   └── test_ollama.py              # Verify Ollama/Llama setup
├── src/
│   ├── ner/                        # NER model code (planned)
│   └── classifier/                 # Reserved (unused — seniority classifier removed from scope)
├── prompts/
│   └── annotation.txt              # LLM prompt for SKILL/TOOL extraction
├── models/                         # Trained model artifacts (planned)
├── app/                            # Streamlit dashboard (planned)
├── docs/
│   └── annotation_guidelines.md    # Entity annotation rules for SKILL and TOOL
├── Project_Summary_German_Data_Jobs.md   # This file — project overview & progress
├── German_Data_Jobs_Schedule.md          # Detailed daily schedule
├── requirements.txt                # Python dependencies
├── mylearning.md                   # Personal learning notes
├── README.md                       # Public-facing README
└── LICENSE
```

---

## Notes

- Annotation is the bottleneck — don't skip it, don't over-engineer it
- A working model with 70% F1 is better than no model
- The dashboard doesn't need to be beautiful, just functional
- Document what you learn about the job market — that's interview material
- Using existing data when available is smart engineering, not cheating
