# German Data Jobs Analyzer — 3-Week Schedule

**Start date:** Thursday, January 29, 2026  
**Hard deadline:** Wednesday, February 19, 2026  
**Daily focused hours:** 6-7 hours (childcare 8:00-15:30)

---

## How to Use This Schedule

1. Each day, check off completed tasks
2. If you finish early → move to next day's tasks
3. If you fall behind → skip to next day, don't try to catch up
4. End of each week: update the Progress Tracker in the main project doc

**Rule:** If a task takes more than 1.5x the estimated time, stop and ask for help.

---

## Week 1: Setup + Data Collection

### Day 1 (Thursday, Jan 29) — Setup
**Goal:** Repo exists, environment works

| Task | Time | Done |
|------|------|------|
| Create GitHub repo "german-data-job-analyzer" | 15 min | [x] |
| Copy `.devcontainer/` from Project 1 | 15 min | [x] |
| Update `requirements.txt`: transformers, datasets, streamlit, label-studio-sdk | 30 min | [x] |
| Create project folder structure | 15 min | [x] |
| Open in VS Code Dev Container, verify it works | 30 min | [x] |
| Run `python -c "from transformers import AutoModel; print('OK')"` | 15 min | [x] |
| Git commit + push | 10 min | [x] |

**End of day checkpoint:** Can you import transformers in the container? Yes → Day 1 done. ✓

---

### Day 2 (Friday, Jan 30) — Data Source Research
**Goal:** Know where your data is coming from

| Task | Time | Done |
|------|------|------|
| Search Kaggle for German job posting datasets | 30 min | [x] |
| Search HuggingFace datasets | 30 min | [x] |
| Search for academic datasets (papers with data) | 30 min | [x] |
| Check Indeed/StepStone terms of service | 15 min | [x] |
| **Decision:** Which data source to use | 15 min | [x] |
| Document decision in project README | 15 min | [x] |
| If no dataset found: plan manual collection strategy | 30 min | [x] |

**End of day checkpoint:** Do you know where your data will come from? Yes → Day 2 done.

**Note:** If no good dataset exists, don't panic. Manual collection of 50-100 postings is fine for a portfolio project.

---

### Day 3 (Monday, Feb 3) — Data Collection
**Goal:** Have raw job postings ready

| Task | Time | Done |
|------|------|------|
| If dataset found: download and explore | 60 min | [x] |
| If manual: collect 50 job postings from job sites | 3 hrs | [x] |
| Create `data/raw/` folder structure | 15 min | [x] |
| Store postings in JSON format | 30 min | [x] |
| Write script to load and preview data | 30 min | [x] |
| Verify: can load at least 50 postings | 15 min | [x] |
| Install Ollama via brew | 15 min | [x] |
| Pull llama3.1:8b model | 15 min | [x] |
| Test LLM on sample job description | 15 min | [x] |
| Git commit + push | 10 min | [x] |

**End of day checkpoint:** Do you have 50+ job postings loadable in Python? Yes → Day 3 done.

---

### Day 4 (Tuesday, Feb 4) — LLM Annotation Setup
**Goal:** Annotation prompt ready, LLM tested

| Task | Time | Done |
|------|------|------|
| Sample 150 random job postings from dataset | 30 min | [ ] |
| Define entity labels clearly: SKILL vs TOOL | 30 min | [ ] |
| Create annotation prompt template for LLM | 45 min | [ ] |
| Test prompt on 5 job postings (German & English) | 45 min | [ ] |
| Refine prompt based on test results | 30 min | [ ] |
| Document annotation guidelines | 30 min | [ ] |
| Save sampled jobs to `data/annotation/sample_150.json` | 15 min | [ ] |

**End of day checkpoint:** Does LLM annotation prompt work on test jobs? Yes → Day 4 done.

---

### Day 5 (Wednesday, Feb 5) — LLM Pre-annotation
**Goal:** 150 job postings pre-annotated by LLM

| Task | Time | Done |
|------|------|------|
| Create script `scripts/04_llm_annotate.py` | 30 min | [ ] |
| Run LLM annotation on all 150 jobs | 2-3 hrs | [ ] |
| Save annotations in JSON format | 30 min | [ ] |
| Spot-check 10 annotations for quality | 30 min | [ ] |
| Install Label Studio (Docker) for review | 45 min | [ ] |
| Git commit + push | 10 min | [ ] |

**End of day checkpoint:** Do you have 150 LLM-annotated postings? Yes → Day 5 done.

---

### Day 6 (Thursday, Feb 6) — Annotation Review Day 1
**Goal:** 75 postings reviewed and corrected

| Task | Time | Done |
|------|------|------|
| Import pre-annotated jobs to Label Studio | 30 min | [ ] |
| Review and correct 75 LLM annotations | 4-5 hrs | [ ] |
| Take breaks every 45 min | — | [ ] |
| Document common LLM errors | 30 min | [ ] |

**End of day checkpoint:** Have you reviewed 75 postings? Yes → Day 6 done.

---

### Day 7 (Friday, Feb 7) — Annotation Review Day 2
**Goal:** 150 postings reviewed, ready for training

| Task | Time | Done |
|------|------|------|
| Review and correct remaining 75 annotations | 3-4 hrs | [ ] |
| Export all corrected annotations | 30 min | [ ] |
| Convert to IOB format for NER training | 60 min | [ ] |
| Create train/val/test split (70/15/15) | 30 min | [ ] |
| Save splits to `data/processed/` | 15 min | [ ] |
| Update Progress Tracker | 15 min | [ ] |
| Git commit + push | 10 min | [ ] |

**End of week checkpoint:** Do you have 150 annotated postings in training format? Yes → Week 1 done! 🎉

---

## Week 2: Model Training

### Day 8 (Monday, Feb 10) — NER Fine-tuning Setup
**Goal:** Training script ready, first training run

| Task | Time | Done |
|------|------|------|
| Create `src/ner/train.py` | 15 min | [ ] |
| Load `xlm-roberta-large` with AutoModelForTokenClassification | 45 min | [ ] |
| Write data loading function (IOB format → HF Dataset) | 60 min | [ ] |
| Configure training arguments (small batch, few epochs first) | 30 min | [ ] |
| Run first training (just 1 epoch to test) | 30 min | [ ] |
| Verify: training runs without errors | 15 min | [ ] |
| Git commit + push | 10 min | [ ] |

**End of day checkpoint:** Does training run without crashing? Yes → Day 8 done.

---

### Day 9 (Tuesday, Feb 11) — NER Training + Evaluation
**Goal:** Trained NER model with evaluation metrics

| Task | Time | Done |
|------|------|------|
| Run full training (3-5 epochs) | 2-3 hrs | [ ] |
| Write evaluation script | 45 min | [ ] |
| Calculate F1 score on test set | 30 min | [ ] |
| Analyze errors: what does the model get wrong? | 45 min | [ ] |
| Document results in `results/ner_evaluation.md` | 30 min | [ ] |
| Save best model to `models/ner/` | 15 min | [ ] |

**End of day checkpoint:** Do you have F1 score documented? Yes → Day 9 done.

**Note:** 60-70% F1 is fine for a portfolio project with limited data. Document why and what would improve it.

---

### Day 10 (Wednesday, Feb 12) — NER Inference + Seniority Prep
**Goal:** NER works on new text, seniority data ready

| Task | Time | Done |
|------|------|------|
| Create `src/ner/predict.py` | 15 min | [ ] |
| Write function: text → extracted entities | 45 min | [ ] |
| Test on 10 new job postings | 30 min | [ ] |
| Extract experienceLevel field from dataset | 30 min | [ ] |
| Map experienceLevel to Junior/Mid/Senior categories | 45 min | [ ] |
| Store seniority mappings in data file | 30 min | [ ] |
| Git commit + push | 10 min | [ ] |

**End of day checkpoint:** Can NER extract entities from new text? Yes → Day 10 done.

**Note:** Seniority classification will use existing experienceLevel field from dataset, no manual labeling needed.

---

### Day 11 (Thursday, Feb 13) — Seniority Classifier
**Goal:** Trained seniority classifier

| Task | Time | Done |
|------|------|------|
| Create `src/classifier/train.py` | 15 min | [ ] |
| Load `xlm-roberta-large` for sequence classification | 30 min | [ ] |
| Prepare data (text → label) | 45 min | [ ] |
| Train classifier (3 epochs) | 1-2 hrs | [ ] |
| Evaluate accuracy on test set | 30 min | [ ] |
| Document results | 30 min | [ ] |
| Save model to `models/classifier/` | 15 min | [ ] |

**End of day checkpoint:** Does classifier predict seniority? Yes → Day 11 done.

---

### Day 12 (Friday, Feb 14) — Pipeline Integration + Buffer
**Goal:** End-to-end pipeline works

| Task | Time | Done |
|------|------|------|
| Create `src/pipeline.py` | 30 min | [ ] |
| Function: raw text → NER entities + seniority prediction | 60 min | [ ] |
| Run pipeline on all collected job postings | 60 min | [ ] |
| Save results to `data/analyzed/results.json` | 30 min | [ ] |
| Catch up on any missed tasks | varies | [ ] |
| Git commit + push | 10 min | [ ] |
| Update Progress Tracker | 15 min | [ ] |

**End of week checkpoint:** Can you analyze a job posting end-to-end? Yes → Week 2 done! 🎉

---

## Week 3: Dashboard + Ship

### Day 13 (Monday, Feb 17) — Dashboard Setup
**Goal:** Basic Streamlit app running

| Task | Time | Done |
|------|------|------|
| Create `app/dashboard.py` | 15 min | [ ] |
| Load analyzed results | 30 min | [ ] |
| Display basic stats: total postings, date range | 30 min | [ ] |
| Add bar chart: top 10 skills | 60 min | [ ] |
| Add bar chart: top 10 tools | 60 min | [ ] |
| Run with `streamlit run app/dashboard.py` | 15 min | [ ] |
| Git commit + push | 10 min | [ ] |

**End of day checkpoint:** Does Streamlit show skill charts? Yes → Day 13 done.

---

### Day 14 (Tuesday, Feb 18) — Dashboard Features
**Goal:** Dashboard tells a story

| Task | Time | Done |
|------|------|------|
| Add seniority distribution pie chart | 45 min | [ ] |
| Add skill co-occurrence heatmap (what skills appear together) | 90 min | [ ] |
| Add filter: by seniority level | 45 min | [ ] |
| Add "analyze your own posting" text input | 60 min | [ ] |
| Make it visually decent (titles, layout) | 45 min | [ ] |
| Git commit + push | 10 min | [ ] |

**End of day checkpoint:** Is the dashboard useful and presentable? Yes → Day 14 done.

---

### Day 15 (Wednesday, Feb 19) — Documentation + Ship
**Goal:** Project is DONE and public

| Task | Time | Done |
|------|------|------|
| Write `README.md` (methodology, results, how to run) | 90 min | [ ] |
| Add screenshot of dashboard | 15 min | [ ] |
| Document model performance (F1, accuracy) | 30 min | [ ] |
| Write `README_DE.md` | 45 min | [ ] |
| Final code cleanup | 30 min | [ ] |
| Make GitHub repo public | 5 min | [ ] |
| Add to CV/portfolio | 30 min | [ ] |
| **CELEBRATE — PROJECT 2 SHIPPED** 🎉 | rest of day | [ ] |

---

## Emergency Rules

**If you can't find a dataset:**
- Manual collection of 100 postings is enough
- Quality over quantity

**If annotation is taking too long:**
- Stop at 100 postings
- A smaller, well-annotated dataset beats a large messy one

**If model performance is poor:**
- Document it honestly in README
- "With more data, performance would improve" is a valid conclusion

**If behind by more than 2 days:**
- Skip seniority classifier
- NER + simple dashboard is still a valid portfolio piece

**If overwhelmed:**
- Close this schedule
- Do the first unchecked box
- That's it

---

## After Completion

**What to do next:**
1. Start interview prep
2. Apply to jobs using your market insights
3. Consider Project 3 (optional)

**What NOT to do:**
- Add more features
- "Improve" the model
- Build a web scraper

---

*You've done this once. You can do it again. Ship it.*
