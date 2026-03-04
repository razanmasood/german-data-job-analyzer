# German Data Jobs Analyzer — 3-Week Schedule

**Start date:** Thursday, January 29, 2026  
**Hard deadline:** Wednesday, February 19, 2026  
**Daily focused hours:** 6-7 hours (childcare 8:00-15:30)

**🎯 SCOPE CHANGE:** Removed seniority classifier (using existing experienceLevel data instead). This saves ~1 day of work.

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

### Day 4 (Tuesday, Feb 4) — LLM Annotation Setup + Data Analysis
**Goal:** Annotation prompt ready, experienceLevel field verified

| Task | Time | Done |
|------|------|------|
| Sample 150 random job postings from dataset | 30 min | [x] |
| Define entity labels clearly: SKILL vs TOOL | 30 min | [x] |
| Create annotation prompt template for LLM | 45 min | [x] |
| Test prompt on 5 job postings (German & English) | 45 min | [x] |
| Refine prompt based on test results | 30 min | [x] |
| Document annotation guidelines | 30 min | [x] |
| **Analyze experienceLevel column distribution** | 15 min | [x] |
| Save sampled jobs to `data/annotation/sample_150.json` | 15 min | [x] |

**End of day checkpoint:** Does LLM annotation prompt work on test jobs? Yes → Day 4 done.

---

### Day 5 (Wednesday, Feb 5) — LLM Pre-annotation
**Goal:** 150 job postings pre-annotated by LLM

| Task | Time | Done |
|------|------|------|
| Create script `scripts/04_llm_annotate.py` | 30 min | [x] |
| Run LLM annotation on all 150 jobs | 2-3 hrs | [x] |
| Save annotations in JSON format | 30 min | [x] |
| Spot-check 10 annotations for quality | 30 min | [x] |
| Install Label Studio (Docker) for review | 45 min | [x] |
| Git commit + push | 10 min | [x] |

**End of day checkpoint:** Do you have 150 LLM-annotated postings? Yes → Day 5 done.

---

### Day 6 (Thursday, Feb 6) — Annotation Review Day 1
**Goal:** 75 postings reviewed and corrected

| Task | Time | Done |
|------|------|------|
| Import pre-annotated jobs to Label Studio | 30 min | [x] |
| Review and correct 150 LLM annotations | 4-5 hrs | [x] |
| Take breaks every 45 min | — | [x] |
| Document common LLM errors | 30 min | [x] |

**End of day checkpoint:** Have you reviewed 150 postings? Yes → Day 6 done.

---

### Day 7 (Friday, Feb 7) — Annotation Review Day 2
**Goal:** 150 postings reviewed, ready for training

| Task | Time | Done |
|------|------|------|
| Export all corrected annotations | 30 min | [x] |
| Convert to IOB format for NER training | 60 min | [x] |
| Create train/val/test split (70/15/15) | 30 min | [x] |
| Save splits to `data/processed/` | 15 min | [x] |
| Update Progress Tracker | 15 min | [x] |
| Git commit + push | 10 min | [x] |

**End of week checkpoint:** Do you have 150 annotated postings in training format? Yes → Week 1 done! 🎉

---

## Week 2: Model Training

### Day 8 (Monday, Feb 10) — NER Fine-tuning Setup
**Goal:** Training script ready, first training run

| Task | Time | Done |
|------|------|------|
| Create `src/ner/train.py` | 15 min | [x] |
| Load `xlm-roberta-large` with AutoModelForTokenClassification | 45 min | [x] |
| Write data loading function (IOB format → HF Dataset) | 60 min | [x] |
| Configure training arguments (small batch, few epochs first) | 30 min | [x] |
| Run first training (just 1 epoch to test) | 30 min | [x] |
| Verify: training runs without errors | 15 min | [x] |
| Git commit + push | 10 min | [x] |

**End of day checkpoint:** Does training run without crashing? Yes → Day 8 done.

---

### Day 9 (Tuesday, Feb 11) — NER Training + Evaluation
**Goal:** Trained NER model with evaluation metrics

| Task | Time | Done |
|------|------|------|
| Run full training (3-5 epochs) | 2-3 hrs | [x] |
| Write evaluation script | 45 min | [x] |
| Calculate F1 score on test set | 30 min | [x] |
| Analyze errors: what does the model get wrong? | 45 min | [x] |
| Document results in `results/ner_evaluation.md` | 30 min | [x] |
| Save best model to `models/ner/` | 15 min | [x] |

**End of day checkpoint:** Do you have F1 score documented? Yes → Day 9 done.

**Note:** 60-70% F1 is fine for a portfolio project with limited data. Document why and what would improve it.

---

### Day 10 (Wednesday, Feb 12) — NER Inference Pipeline
**Goal:** End-to-end NER extraction works on new text

| Task | Time | Done |
|------|------|------|
| Create `src/ner/predict.py` | 15 min | [x] |
| Write function: text → extracted entities | 45 min | [x] |
| Test on 10 new job postings | 30 min | [x] |
| Create `src/pipeline.py` for full processing | 30 min | [x] |
| Add function to load experienceLevel from data | 30 min | [x] |
| Test pipeline: text → entities + seniority (from data) | 45 min | [x] |
| Git commit + push | 10 min | [x] |

**End of day checkpoint:** Can NER extract entities from new text? Yes → Day 10 done.

**Note:** Seniority comes directly from experienceLevel field, no classification needed.

---

### Day 11 (Thursday, Feb 13) — Data Processing + Analysis
**Goal:** All job postings analyzed and results ready

| Task | Time | Done |
|------|------|------|
| Run NER pipeline on all 1,240 job postings | 90 min | [x] |
| Extract and standardize experienceLevel data | 30 min | [x] |
| Create aggregated statistics (skill counts, etc.) | 60 min | [x] |
| Analyze skill co-occurrence patterns | 60 min | [x] |
| Save results to `data/analyzed/results.json` | 30 min | [x] |
| Document interesting findings | 45 min | [x] |
| Git commit + push | 10 min | [x] |

**End of day checkpoint:** Do you have analyzed results for all postings? Yes → Day 11 done.

---

### Day 12 (Friday, Feb 14) — Polish + Buffer
**Goal:** Clean code, catch up on missed tasks

| Task | Time | Done |
|------|------|------|
| Code cleanup: remove debug prints, add docstrings | 60 min | [x] |
| Add error handling to pipeline | 45 min | [x] |
| Write unit tests for key functions (optional) | 60 min | [x] |
| Catch up on any missed tasks from Week 1-2 | varies | [x] |
| Update Progress Tracker | 15 min | [x] |
| Git commit + push | 10 min | [x] |

**End of week checkpoint:** Is your code clean and pipeline robust? Yes → Week 2 done! 🎉

---

## Week 3: Dashboard + Ship

### Day 13 (Monday, Feb 17) — Dashboard Setup
**Goal:** Basic Streamlit app running

| Task | Time | Done |
|------|------|------|
| Create `app/dashboard.py` | 15 min | [x] |
| Load analyzed results | 30 min | [x] |
| Display basic stats: total postings, date range | 30 min | [x] |
| Add bar chart: top 10 skills | 60 min | [x] |
| Add bar chart: top 10 tools | 60 min | [x] |
| Add seniority distribution chart (from experienceLevel) | 45 min | [x] |
| Run with `streamlit run app/dashboard.py` | 15 min | [x] |
| Git commit + push | 10 min | [x] |

**End of day checkpoint:** Does Streamlit show skill charts? Yes → Day 13 done.

---

### Day 14 (Tuesday, Feb 18) — Dashboard Features + Polish
**Goal:** Dashboard tells a story and looks professional

| Task | Time | Done |
|------|------|------|
| Add skill co-occurrence heatmap | 90 min | [x] |
| Add filter: by experience level | 45 min | [x] |
| Add "analyze your own posting" text input | 60 min | [x] |
| Improve visual design (colors, layout, titles) | 60 min | [x] |
| Add explanatory text and insights | 45 min | [ ] |
| Test dashboard thoroughly | 30 min | [ ] |
| Git commit + push | 10 min | [ ] |

**End of day checkpoint:** Is the dashboard useful and presentable? Yes → Day 14 done.


**💡 Optional Enhancement Idea:**
If you finish Day 14 with time/energy remaining, consider adding:
- Skill comparison by seniority level (shows skill progression Junior → Senior)
- Estimated time: 30 minutes
- Decision point: Assess at end of Day 14 whether this adds value or is just nice-to-have

---

### Day 15 (Wednesday, Feb 19) — Documentation + Ship
**Goal:** Project is DONE and public

| Task | Time | Done |
|------|------|------|
| Write `README.md` (methodology, results, how to run) | 90 min | [ ] |
| Add screenshots of dashboard | 15 min | [ ] |
| Document model performance (F1 score) | 30 min | [ ] |
| Document key findings about German job market | 30 min | [ ] |
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
- Just keep going with NER + dashboard
- A working NER model is still a strong portfolio piece

**If overwhelmed:**
- Close this schedule
- Do the first unchecked box
- That's it

---

## What Changed (Feb 4 Update)

**REMOVED:** 
- Day 11 (Seniority Classifier training) — using existing experienceLevel data instead
- Seniority annotation tasks
- Classifier training and evaluation

**GAINED:**
- More time for NER polish (Day 12)
- More time for dashboard features (Day 13)
- Earlier finish = earlier job applications

**Why this is better:**
- LinkedIn already provides clean experienceLevel data (0% missing)
- Saves ~1 day of work
- Still demonstrates NLP skills (NER is the core value)
- Gets you to job applications faster

---

## After Completion

**What to do next:**
1. Start interview prep
2. Apply to jobs using your market insights
3. Consider Project 3 (optional, but NOT required)

**What NOT to do:**
- Add more features
- "Improve" the model
- Build a web scraper
- Add salary prediction
- Perfect the dashboard

---

*You've done this once. You can do it again. Ship it.*
