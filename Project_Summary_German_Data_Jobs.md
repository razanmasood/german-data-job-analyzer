# German Data Jobs Analyzer

## Project Overview

### What This Is
An end-to-end NLP pipeline that analyzes 1,240 real German data science job postings to extract in-demand skills, classify seniority levels, and visualize market trends. The project demonstrates modern ML engineering practices by combining LLM-assisted annotation with fine-tuned multilingual transformers.

### Why This Matters

**For the German job market:**
- Provides data-driven insights into what skills employers actually want
- Identifies skill combinations that appear together (e.g., "Python + AWS + Docker")
- Reveals seniority expectations and requirements
- Helps job seekers prioritize which skills to develop

**For portfolio demonstration:**
- Shows end-to-end ML engineering: data collection → annotation → model training → deployment
- Demonstrates practical use of transformers (not just API calls)
- Highlights multilingual NLP capability (German + English)
- Shows modern workflow: LLM pre-annotation + human review (hybrid approach)
- Proves ability to work with messy real-world data

### How It Works

**Input:** Raw job posting text
```
"Wir suchen einen Data Scientist mit Python, SQL und Machine Learning Erfahrung..."
```

**Processing Pipeline:**
1. **LLM Pre-annotation**: Llama 3.1 8B extracts candidate skills/tools
2. **Human Review**: Manual correction in Label Studio
3. **NER Training**: Fine-tune xlm-roberta-large on corrected annotations
4. **Seniority Classification**: Use existing experience level data
5. **Analysis**: Extract skills from all 1,240 postings

**Output:** Interactive Streamlit dashboard showing:
- Top 20 most requested skills and tools
- Skill co-occurrence patterns (what skills appear together)
- Seniority distribution across roles
- Trends in the German DS/ML job market

### Tech Highlights
- **Multilingual**: Handles both German and English postings (reflects real market)
- **Hybrid annotation**: LLM does 80% of work, human ensures quality
- **Production-grade**: Containerized, version-controlled, reproducible
- **Local-first**: Fine-tuning runs on MacBook (no cloud costs)

## 🎯 Current Step

**Next action:** Review this scope with Claude, then set up repo

---

## ✅ Progress Tracker

### Phase 0: Setup (2 days)
- [x] Create GitHub repo
- [x] Set up Dev Container (reuse pattern from Project 1)
- [x] Create project structure
- [x] Verify environment works

### Phase 1: Data Collection (3 days)
- [x] Research job posting sources (StepStone, Indeed.de, LinkedIn)
- [x] Build scraper OR find existing dataset
- [x] Collect 500+ German DS/ML job postings (1,240 collected via Octoparse)
- [x] Store raw data in structured format
- [x] Verify: have enough data to proceed

### Phase 2: Annotation + NER Fine-tuning (5 days)
- [ ] Define entity types (SKILL, TOOL)
- [ ] Install Ollama + Llama 3.1 8B locally
- [ ] Sample 150 job postings for annotation
- [ ] Create annotation prompt for LLM
- [ ] Run LLM pre-annotation on 150 postings
- [ ] Set up Label Studio for review/correction
- [ ] Review and correct LLM annotations (150 postings)
- [ ] Prepare data in NER format (IOB tagging)
- [ ] Fine-tune xlm-roberta-large for NER
- [ ] Evaluate: F1 score on held-out test set

### Phase 3: Seniority Classifier (3 days)
- [ ] Fine-tune classifier (or train from extracted features)
- [ ] Evaluate accuracy
- [ ] Verify: classifier works on new postings

**Note:** Use existing experienceLevel field from dataset instead of manual labeling

### Phase 4: Analysis + Dashboard (3 days)
- [ ] Run NER on all job postings
- [ ] Cluster/group extracted skills
- [ ] Build simple Streamlit dashboard
- [ ] Show: top skills, skill co-occurrence, seniority distribution
- [ ] Verify: dashboard tells a story

### Phase 5: Finish (2 days)
- [ ] Write README (German + English)
- [ ] Clean up code
- [ ] Push to GitHub
- [ ] Add to CV/portfolio

**When all boxes are checked, the project is DONE.**

---

## One-Sentence Summary

Fine-tune a German NER model to extract skills from data science job postings, classify seniority levels, and visualize the German DS/ML job market.

---

## What You're Building (Input → Output)

### Input
Raw German job posting text, e.g.:
```
Wir suchen einen erfahrenen Data Scientist (m/w/d) mit 
3+ Jahren Erfahrung in Python und Machine Learning. 
Kenntnisse in AWS und Docker sind von Vorteil.
```

### What Happens Inside
1. Fine-tuned NER extracts: [Python: TOOL], [Machine Learning: SKILL], [3+ Jahren: EXPERIENCE], [AWS: TOOL], [Docker: TOOL]
2. Seniority classifier predicts: "Mid-level"
3. Results aggregated across all postings

### Output
Dashboard showing:
- Most requested skills/tools (bar chart)
- Skill co-occurrence (what's requested together)
- Seniority distribution
- Your match score (optional fun feature)

---

## Why This Project

**Portfolio value:**
- Fine-tuning a transformer model (not just using APIs)
- German NLP (differentiator in German job market)
- Custom NER (real NLP engineering, not just sentiment analysis)
- End-to-end: data collection → model training → visualization

**Practical value:**
- You'll actually learn what skills to emphasize
- Good talking point in interviews: "I analyzed 500 job postings and found..."

---

## Tech Stack

### Models
| Component | Choice | Reason |
|-----------|--------|--------|
| Base model | `xlm-roberta-large` | Multilingual BERT, handles both German & English |
| NER framework | Hugging Face Transformers | You know it, industry standard |
| Seniority classifier | Same base model, classification head | Reuse fine-tuned representations |

### Infrastructure
| Component | Choice | Reason |
|-----------|--------|--------|
| Annotation | Label Studio (local Docker) | Free, good NER support |
| Dashboard | Streamlit | Fast to build, looks professional |
| Data storage | SQLite or JSON files | Simple, no infrastructure needed |
| Development | Docker + Dev Containers | Same as Project 1 |

### Compute
- Fine-tuning: Your M4 MacBook (32GB RAM is plenty for BERT)
- No cloud needed for training

---

## Data Strategy

### Option A: Scrape live postings
- Pro: Fresh, real data
- Con: Legal gray area, sites block scrapers, takes time

### Option B: Find existing dataset
- Check Kaggle, HuggingFace datasets for German job postings
- Pro: Faster start
- Con: May not exist or be low quality

### Option C: Manual collection
- Copy-paste from job sites into structured format
- Pro: Definitely legal, controlled quality
- Con: Tedious

**Decision:** Start with Option B (search for datasets). Fall back to Option C if needed. Avoid scraping.

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
- `experienceLevel`: Entry level, Associate, Mid-Senior, Executive
- `location`: Job location
- `companyName`, `companyUrl`: Company information
- `salary`, `benefits`, `contractType`: Compensation details (often sparse)
- `publishedAt`: Posting date
- `jobUrl`, `applyUrl`: Application links
- `sector`, `jobCategory`: Job classification
- Other metadata fields

### Data Quality
- **Description field**: 100% filled (1,240/1,240)
- **Experience level**: 100% filled (1,240/1,240)
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
| EXPERIENCE | 3+ Jahre, mehrjährige Erfahrung | Years/level required |
| EDUCATION | Master, PhD, Studium Informatik | Degree requirements |
| SALARY_HINT | 65.000€, competitive salary | Any salary mention |
| NICE_TO_HAVE | von Vorteil, wünschenswert | Marks optional skills |

Start with SKILL and TOOL only. Add others if time permits.

---

## Scope Boundaries

### In scope
- Multilingual job postings (German & English)
- Data Scientist / ML Engineer / AI roles
- NER for skill/tool extraction
- Seniority classification
- Simple Streamlit dashboard
- ~500 job postings

### Out of scope (do NOT add)
- Salary prediction model (too complex)
- Job recommendation system
- Real-time scraping
- Company analysis
- Geographic analysis

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Can't find German job posting dataset | Manual collection (50-100 postings), or use English dataset to prove concept |
| Annotation takes too long | Start with 150 postings, increase only if needed |
| NER performance is poor | Acceptable for portfolio — document challenges in README |
| Fine-tuning too slow on laptop | Use smaller model (`xlm-roberta-base`), reduce batch size |

---

## Timeline

**Target: 3 weeks** (same as Project 1)

| Week | Focus |
|------|-------|
| Week 1 | Setup + Data collection + Start annotation |
| Week 2 | Finish annotation + Fine-tune NER + Seniority classifier |
| Week 3 | Dashboard + Polish + Ship |

Detailed daily schedule to be created separately.

---

## Definition of Done (MVP)

The project is **complete** when:

1. ☐ 200+ job postings annotated for NER
2. ☐ Fine-tuned German NER model with documented F1 score
3. ☐ Seniority classifier trained and evaluated
4. ☐ Streamlit dashboard shows skill analysis
5. ☐ README explains methodology and results
6. ☐ Code is clean and on GitHub
7. ☐ Can demo in under 5 minutes

**Everything beyond this is a separate project.**

---

## Notes

- Annotation is the bottleneck — don't skip it, don't over-engineer it
- A working model with 70% F1 is better than no model
- The dashboard doesn't need to be beautiful, just functional
- Document what you learn about the job market — that's interview material
