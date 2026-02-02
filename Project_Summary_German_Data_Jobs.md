# German Data Jobs Analyzer

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
- [ ] Research job posting sources (StepStone, Indeed.de, LinkedIn)
- [ ] Build scraper OR find existing dataset
- [ ] Collect 500+ German DS/ML job postings
- [ ] Store raw data in structured format
- [ ] Verify: have enough data to proceed

### Phase 2: Annotation + NER Fine-tuning (5 days)
- [ ] Define entity types (SKILL, TOOL, EXPERIENCE, EDUCATION, SALARY_HINT)
- [ ] Set up Label Studio or simple annotation tool
- [ ] Annotate 200-300 job postings (this takes time!)
- [ ] Prepare data in NER format (IOB tagging)
- [ ] Fine-tune `deepset/gbert-large` for NER
- [ ] Evaluate: F1 score on held-out test set
- [ ] Verify: model extracts entities reasonably well

### Phase 3: Seniority Classifier (3 days)
- [ ] Label job postings by seniority (Junior/Mid/Senior)
- [ ] Fine-tune classifier (or train from extracted features)
- [ ] Evaluate accuracy
- [ ] Verify: classifier works on new postings

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
| Base model | `deepset/gbert-large` | Best German BERT, proven for NER |
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
- German job postings only
- Data Scientist / ML Engineer / AI roles
- NER for skill/tool extraction
- Seniority classification
- Simple Streamlit dashboard
- ~500 job postings

### Out of scope (do NOT add)
- English postings
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
| Fine-tuning too slow on laptop | Use smaller model (`gbert-base`), reduce batch size |

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
