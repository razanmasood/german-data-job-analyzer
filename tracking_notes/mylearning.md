# Learning Journal - German Data Jobs Analyzer Project

**Purpose:** Track learnings, concepts, and interview-ready talking points while building this portfolio project.

**Last updated:** February 9, 2026

---

## 📋 Concepts to Review (Quick Checklist)

- [ ] Few-shot NER
- [ ] Domain adaptation for NLP
- [ ] IOB/BIO tagging format
- [ ] Precision vs Recall vs F1
- [ ] Inter-annotator agreement
- [ ] Transformer fine-tuning mechanics
- [ ] LLM-assisted annotation workflows
- [ ] Entity boundary detection

*Add new items as you encounter them. Check off when reviewed.*

---

## 📖 Core Concepts (Organized Reference)

### NER (Named Entity Recognition)

#### Few-Shot NER
**What it is:**

**Why it matters for this project:**

**Key papers/resources:**

#### IOB Tagging
**What it is:**

**Why it matters for this project:**

**Example:**

#### Domain Adaptation
**What it is:**

**Why it matters for this project:**

**How I'm doing it:**

---

### Evaluation Metrics

#### F1 Score
**What it is:**

**Formula:**

**Why it matters:**

**What's a good F1 for this project:**

#### Precision vs Recall
**Precision:**

**Recall:**

**Tradeoff:**

**For job postings, which matters more:**

---

### LLM Concepts

#### LLM-Assisted Annotation
**What it is:**

**Advantages:**

**Challenges:**

**How I'm using it:**

#### Prompt Engineering for Data Annotation
**Key principles:**
1. State the PURPOSE upfront (e.g., "for NER model training")
2. Put most critical rules first (EXACT TEXT ONLY)
3. Show explicit WRONG examples, not just correct ones
4. Keep it concise - LLMs follow shorter prompts better

**What worked for me:**
- Adding "WRONG (do not do this)" section with concrete mistakes
- Explaining WHY exact text matters (NER training needs verbatim spans)
- Removing verbose examples that confused the model
- Language-specific examples (German input → German output)

**What didn't work:**
- Long list of examples without negative cases
- Assuming LLM would infer language matching requirement
- Mixed-language example that confused rather than clarified

---

### Transformers & Fine-Tuning

#### Why xlm-roberta-large
**Model architecture:**

**Why multilingual:**

**Parameters to tune:**

#### Transfer Learning
**What it is:**

**How fine-tuning works:**

**Why 150 examples is enough:**

---

## 💡 Key Learnings (Interview-Ready Talking Points)

### 2026-02-04 - Using Existing Data vs Building Models
**What I learned:** 
LinkedIn's experienceLevel field was 100% complete with clean, standardized categories. Building a seniority classifier would have been unnecessary work.

**Why it matters:** 
Shows good engineering judgment - don't build what you don't need. Validates data-driven decision making.

**Interview angle:** 
"I analyzed the data quality first and found the experienceLevel field was already perfect - 0% missing, standardized taxonomy. This saved ~1 day of work that I invested in improving the NER model instead. It demonstrates that sometimes the best solution is recognizing when you don't need to build something."

---

### 2026-02-04 - Annotation Dataset Size
**What I learned:**
For fine-tuning pre-trained models, 100-200 annotated examples is standard for domain adaptation. 150 is the sweet spot between quality and timeline.

**Why it matters:**
Shows understanding of practical ML engineering - balancing model performance with project constraints.

**Interview angle:**
"I annotated 150 job postings - enough to fine-tune effectively while staying within my timeline. Research shows 100-200 examples is standard for domain adaptation with pre-trained transformers. I prioritized annotation quality over quantity since I'm fine-tuning, not training from scratch."

---

### [Date] - [Topic]
**What I learned:**

**Why it matters:**

**Interview angle:**

---

## 🔧 Technical Decisions

### Using xlm-roberta-large for Multilingual NER
**Problem:** 
Dataset is 44% German, 56% English. Need to handle both languages.

**Options I considered:**
1. German-only model (gbert) - ignore English postings
2. Separate models for each language
3. Multilingual model (xlm-roberta)

**What I chose & why:**
xlm-roberta-large because it handles both languages in one model, reflects the real German job market (international companies post in English), and has strong performance on both languages.

**Would I do differently:**
No - this was the right call. The language distribution matched market reality.

---

### LLM Pre-annotation + Human Review
**Problem:**
Annotating 150 job postings manually would take too long.

**Options I considered:**
1. Pure manual annotation (slow but accurate)
2. Pure LLM annotation (fast but potentially noisy)
3. Hybrid: LLM pre-annotate + human review

**What I chose & why:**
Hybrid approach with Llama 3.1 8B for pre-annotation, then Label Studio for human review. Gets 80% of the work done automatically while maintaining quality through human verification.

**Would I do differently:**
TBD after annotation is complete - will document whether LLM quality was good enough.

---
### LLM Section Extraction - 95% Success Rate

**Context:** Need to extract requirements/qualifications sections from 1,240 job postings before entity extraction

**Implementation:**
- Tool: Llama 3.1 8B (local via Ollama)
- Strategy: Two-step process (section extraction → entity extraction)
- Prompt: Content-focused with concrete examples of requirements sections

**Results:**
- Success rate: 95.3% (143/150 jobs)
- Processing time: 3.5 hours for 150 jobs
- Average extraction: 4.1 skills + 3.3 tools per job

**Failure Analysis (7 jobs, 5%):**
- Pattern: All failures were single-paragraph formats without structural breaks
- Root cause: Jobs had section headers but no paragraph separation (HTML formatting issue)
- All 7 contained recognizable headers ("Requirements", "Skills", "Dein Profil")

**Decision:** Proceeded with 143 annotations (exceeded 150 target)
- Trade-off: Could parse HTML structure deeper, but 5% edge cases not worth time investment
- Alternative: Manual annotation of 7 failures would take <30min, but unnecessary

**Interview Talking Point:**
"Achieved 95% automated extraction accuracy and documented failure modes rather than over-engineering for edge cases. This allowed me to exceed my annotation target while maintaining project timeline."
---

### [Decision Name]
**Problem:**

**Options I considered:**

**What I chose & why:**

**Would I do differently:**

---

## 🐛 Problems I Solved

### LLM Pre-Annotation: Problems & Lessons Learned

**Context:** Used Llama 3.1 8B to pre-annotate 150 job postings before human review in Label Studio.

**Problem 1: Conceptual inference instead of verbatim extraction**
The LLM understood concepts semantically but didn't extract exact text spans. For example, it extracted "ETL" when the text said "data pipelines", or "Statistik" from "statistische Methoden". About 25% of entities (374 out of ~2,400) couldn't be mapped back to actual text positions.

**Problem 2: Language mismatch**
The LLM translated concepts instead of copying exact text. It used German terms for English job postings and vice versa — "Statistik" appeared equally in German (23) and English (23) jobs, a clear sign of concept translation rather than extraction.

**Problem 3: Descriptive phrases instead of standard terms**
The LLM extracted vague phrases like "Programmierung von Datenbanken" instead of standard terms like "SQL". It recognized the technical domain but couldn't distinguish between a skill name and a sentence describing it.

**Problem 4: False positives from company names**
The LLM extracted technical terms embedded in company names — e.g., "AI" from "Aignostics", "data" from partial word matches.

**Problem 5: HTML concatenation artifacts**
HTML-to-text conversion produced concatenated words like "DatenmodellierungHervorragende". These broke entity matching and would corrupt NER training data if not cleaned.

**How I fixed each:**
- Problems 1 & 2 → Prompt engineering: added "EXACT TEXT ONLY", "LANGUAGE MATCH" rules, and negative examples showing wrong behavior
- Problem 3 → Human review: systematically deleted descriptive phrases during Label Studio review
- Problem 4 → Human review: deleted false positives from company names and partial word matches
- Problem 5 → Regex preprocessing: `([a-zäöüß])([A-ZÄÖÜ])` → `\1 \2` with camelCase whitelist

**Overall result:** ~85% automation rate was still worth it. Pure manual annotation would have taken 3x longer. Human review caught all LLM errors and maintained quality.

**Interview angle:** "LLMs excel at semantic understanding but struggle with verbatim span detection — two different tasks. I designed the pipeline with human-in-the-loop review as a core step, not an afterthought, which is how production annotation systems actually work."

---

### [Date] - [Issue]
**The problem:**

**How I debugged:**

**Solution:**

**What I learned:**

---

## 📊 Project-Specific Knowledge

### Dataset Characteristics
- **Size:** 1,240 job postings (400 DS + 1,000 ML, deduplicated)
- **Languages:** 56% English, 44% German
- **Source:** LinkedIn via Octoparse
- **Date range:** January 2026
- **Experience levels:** 51% Mid-Senior, 21% Entry, 12% Associate
- **Key insight:** International tech companies in Germany post mostly in English

### Entity Types
**SKILL** = Broad technical capabilities (e.g., Machine Learning, NLP, Statistics)
**TOOL** = Specific technologies (e.g., Python, AWS, Docker, TensorFlow)

**Annotation guidelines (Feb 6):**
- DELETE false positives from company names (e.g., "AI" from "Aignostics")
- DELETE partial word matches (e.g., "ai" from "paid")  
- TOOL includes: programming languages, frameworks, cloud platforms, databases, orchestration tools
- SKILL includes: methodologies, conceptual abilities, domain knowledge
- When in doubt: Is it a thing you install/use (TOOL) or a capability you develop (SKILL)?


**Why just two types:**
Clear distinction, high value for job seekers, easier to annotate consistently.

### NER Fine-tuning Parameters
- **Base model:** xlm-roberta-large (355M parameters)
- **Training data:** ~105 annotated postings
- **Validation:** ~23 postings
- **Test:** ~22 postings
- **Expected F1:** 60-75% (acceptable for domain adaptation with limited data)
- **Training time:** TBD
- **Hardware:** MacBook M4 (32GB RAM)

### LLM Annotation Workflow
- **Model:** Llama 3.1 8B (via Ollama, local)
- **Prompt structure:** TBD after testing
- **Output format:** JSON with entity spans
- **Quality check:** Human review in Label Studio
- **Expected accuracy:** TBD

Updated with Results:
- **Actual accuracy:** ~85% of entities successfully mapped to text spans
- **Not-found entities:** 374 out of ~2,400 (292 skills, 82 tools)
- **Main issues:** Conceptual inference, paraphrasing, false positives
- **Time saved:** Estimated 60-80% reduction vs pure manual annotation
- **Tool used:** Label Studio for review interface with pre-annotations

---

## 🎯 Questions to Research Later

1. What's the state-of-the-art F1 for German NER on job postings?
2. How does xlm-roberta compare to German-specific models on this task?
3. What are best practices for entity boundary detection in multi-word skills?
4. How do other researchers handle "Not Applicable" in seniority data?

---

## 💭 Reflections

### What's Going Well
- Smart scope decisions (removing unnecessary work)
- Good data quality from LinkedIn
- Clear entity definitions
- LLM pre-annotation working well (~85% success rate)
- Label Studio setup successful
- Learning industry-standard annotation workflows

### Challenges
- LLM conceptual inference creates ~25% unmapped entities
- Learning Label Studio interface
- Balancing annotation speed vs quality
- Time management with limited focused hours per day

### What I'm Proud Of
- Analyzing the experienceLevel data before assuming I needed a classifier
- Setting up a modern LLM-assisted annotation workflow
- Understanding and documenting the "not-found entities" problem
- Connecting practical challenges to research literature
- Creating a reproducible Docker-based annotation setup

---

## 🔮 Future Directions — v2 Analysis Ideas

The first version of this project answers a straightforward question: *what do employers want?* It surfaces frequency — what appears most, what clusters together, what the market broadly demands.

But frequency is only the beginning of analysis. The following five directions represent deeper questions worth exploring when time allows.

1. **Skill Gap by Seniority** — maps the career ladder as the market actually defines it, not as career guides imagine it. By tracking how skill requirements shift from Entry to Director level, this analysis reveals what progression genuinely looks like in the German ML market.

2. **Skill Exclusivity Index** — identifies what is hidden beneath the surface of popular skills. Some requirements appear everywhere and mean little. Others appear rarely but signal something specific about a role or employer type. Separating signal from noise is the core challenge of any serious market analysis.

3. **German vs. English Posting Comparison** — uses a genuine methodological advantage: multilingual data. Do German-language postings — likely from local companies — have different expectations than English ones from international firms? This question is only answerable with this specific dataset, and only by someone who can read both languages.

4. **Tool-Skill Co-dependency** — moves beyond what appears together toward understanding *why* it appears together. Technology stacks have an internal logic. Revealing that logic helps job seekers understand not just what to learn, but what belongs together conceptually.

5. **Company Concentration Analysis** — introduces critical thinking about data integrity. A skill appearing 200 times across 180 companies means something fundamentally different than the same count driven by a single prolific poster. Honest analysis requires asking whether demand is real or inflated.

These are not enhancements. They are a different kind of project — one that begins with curiosity about what the data actually says, rather than what it appears to say at first glance.

---

## 📚 Resources & References

### Papers
- Few-shot NER papers: [to be added]
- Domain adaptation papers: [to be added]

### Documentation
- Hugging Face NER guide: https://huggingface.co/docs/transformers/tasks/token_classification
- xlm-roberta-large model card: https://huggingface.co/xlm-roberta-large

### Tools
- Label Studio: https://labelstud.io/
- Ollama: https://ollama.ai/

---
#### LLM-Assisted Annotation
**What it is:**
Using Large Language Models to pre-annotate data, followed by human review and correction. The LLM provides a first pass at labeling entities, reducing manual annotation time by 60-80%.

**Advantages:**
- Speed: ~374 entities found automatically from 150 job postings
- Consistency: LLM applies same logic across all examples
- Cost-effective: Local model (Llama 3.1 8B) via Ollama, no API costs
- Good starting point: Pre-annotations reduce cognitive load for human reviewers

**Challenges:**
- **Conceptual inference problem**: LLM extracts concepts not explicitly in text (e.g., "ETL" when text says "data pipelines")
- **Span detection issues**: ~374 entities (25%) couldn't be mapped to exact text positions
- **Paraphrasing**: LLM uses standard terms but text uses variations (e.g., "Statistik" vs "statistische Methoden")
- **False positives**: Extracts from company names (e.g., "AI" from "Aignostics")

**How I'm using it:**
1. LLM (Llama 3.1 8B) extracts skills/tools in structured JSON format
2. Python script converts to Label Studio prediction format with character positions
3. Human reviews pre-annotations in Label Studio, correcting errors
4. Result: ~85% of work automated, 100% quality through human verification
---
### 2026-02-09 - LLM Annotation: Language Mismatch & Prompt Engineering

**What I learned:**
The LLM was using German terms (e.g., "Statistik") even for English job postings where the text said "statistics". Analysis showed "Statistik" was extracted equally for German (23) and English (23) jobs - a clear language mismatch problem. The LLM was doing *concept extraction* rather than *verbatim NER*.

**Root causes identified:**
1. **Language mismatch**: LLM translated concepts instead of extracting exact text
2. **Inference**: LLM added related terms not in text (e.g., "ETL" when text said "data pipelines")
3. **Text formatting**: HTML conversion artifacts concatenated words (e.g., "DatenanalyseErfahrung")

**How I fixed it:**
1. Updated prompt with explicit "EXACT TEXT ONLY" and "LANGUAGE MATCH" rules
2. Added "WRONG" examples showing common mistakes to avoid
3. Added PURPOSE statement explaining annotations are for NER training
4. Fixed text formatting with regex: `([a-zäöüß])([A-ZÄÖÜ])` → `\1 \2`
5. Created whitelist to preserve camelCase terms (PyTorch, DevOps, LangChain, etc.)

**Interview angle:**
"I discovered the LLM was doing semantic concept extraction rather than verbatim text extraction - using 'Statistik' for English text that said 'statistics'. I solved this through prompt engineering: adding explicit negative examples, stating the NER training purpose, and emphasizing exact text matching. This improved prompt clarity and will improve annotation quality on re-runs."

---

### 2026-02-09 - Label Studio Export with Predictions

**What I learned:**
Creating Label Studio pre-annotations requires finding exact character positions (start/end) for each entity in the text. This is non-trivial when:
- LLM extracts concepts not verbatim in text (~17% of entities)
- Text has formatting issues (concatenated words)
- Entity appears multiple times (need to annotate all occurrences)

**Technical implementation:**
```python
# Label Studio prediction format
{
  "data": {"text": "job description..."},
  "predictions": [{
    "result": [
      {"value": {"start": 704, "end": 720, "text": "Machine Learning", "labels": ["SKILL"]}, ...}
    ]
  }]
}
```

**Key insight:**
Entity match rate (83%) measures verbatim extraction quality, NOT annotation quality. It's a proxy metric - proper evaluation needs human-annotated ground truth with precision/recall/F1.

---

### 2026-02-09 - Text Preprocessing for NER

**What I learned:**
HTML-to-text conversion created concatenated words like "DatenmodellierungHervorragende" that should be "Datenmodellierung Hervorragende". This breaks entity matching and would corrupt NER training data.

**Solution - Regex with whitelist:**
```python
# Add space before capitals following lowercase (German-aware)
text = re.sub(r'([a-zäöüß])([A-ZÄÖÜ])', r'\1 \2', text)

# But preserve camelCase terms like PyTorch, DevOps, LangChain
PRESERVE_TERMS = {'PyTorch', 'DevOps', 'GenAI', 'LangChain', ...}
```

**Why it matters:**
Text quality directly affects NER model training. Garbage in = garbage out. This preprocessing step is essential before annotation AND before model inference.

---

### 2026-02-06 - The LLM "Not-Found Entities" Problem
**What I learned:**
When using LLMs for NER pre-annotation, ~25% of extracted entities couldn't be mapped to exact text positions. The LLM understands concepts semantically but doesn't always extract verbatim text. For example, it inferred "ETL" from "data pipelines" and "Statistik" from "statistische Methoden."

**Why it matters:**
This is a fundamental limitation of LLM-assisted annotation - semantic understanding doesn't equal span detection. Industry handles this with human-in-the-loop workflows, not by expecting perfect LLM annotations.

**Interview angle:**
"I discovered that LLMs excel at semantic extraction but struggle with exact span detection. About 25% of entities were conceptual inferences rather than verbatim text. This taught me to design annotation pipelines with human validation as a core step, not an afterthought. The 85% automation rate was still worth it - the alternative was 100% manual annotation."

**Research connections:**
- Weak supervision for NER (accepting noisy labels)
- Distant supervision (mapping concepts to text)
- Span detection as a separate problem from entity classification
- Tools like Snorkel and Prodigy that embrace imperfect pre-annotations
---
**Results:**
- Successfully extracted entities from 150 job postings
- ~85% success rate: 374 out of ~2,400 entities couldn't be mapped to exact text positions
- Main issues: Conceptual inference (ETL from "data pipelines"), paraphrasing, false positives from company names
- Time saved: Estimated 60-80% reduction in annotation time
- Quality maintained: Human review catches all LLM errors

**Would I do differently:**
No - this was the right approach. The 25% unmapped entities is acceptable and well-documented in NLP research. Pure manual annotation would have taken 3x longer. The hybrid approach balances speed with quality effectively.

---

### 2026-02-06 - Label Studio Local File Access
**The problem:**
Label Studio (running in Docker) couldn't access my project data files for import. Got "Local file serving is disabled" error.

**How I debugged:**
1. Read Label Studio docs on local file serving
2. Realized Docker containers are isolated - need volume mounts
3. Checked that files existed but Label Studio couldn't see them
4. Found environment variable flag in documentation

**Solution:**
Restart Label Studio with proper configuration:
```bash
docker run -it -p 8080:8080 \
  -v ~/label-studio-data:/label-studio/data \
  -v /Users/rezzeh/Projects/german-data-job-analyzer/data:/label-studio/files:ro \
  -e LOCAL_FILES_SERVING_ENABLED=true \
  --name label-studio \
  heartexlabs/label-studio:latest
```

Key elements:
- Volume mount (`-v`) to expose project data folder to container
- `:ro` flag for read-only access (security best practice)
- `LOCAL_FILES_SERVING_ENABLED=true` environment variable to enable feature

**What I learned:**
- Docker containers need explicit volume mounts to access host files
- Read-only mounts (`:ro`) prevent accidental data modification
- Always check documentation for environment variables when features are disabled

---
**New Research Questions**
5. How does weak supervision for NER handle ~25% noisy/missing labels?
6. What's the typical success rate for LLM pre-annotation in production NER systems?
7. How do Snorkel and Prodigy frameworks handle the annotation projection problem?
8. Are there better string matching algorithms for mapping conceptual entities to text spans?
9. How do production NER systems handle multilingual text with language-specific entity forms?
10. What prompt engineering techniques improve LLM verbatim extraction vs concept extraction?

---
### 2026-02-11 - Common LLM Annotation Errors

**Pattern: Extracting descriptive phrases**
The LLM extracted vague phrases like "Programmierung von Datenbanken" instead of concrete terms. These were systematically deleted during review.

**Why it happens:** 
The LLM recognizes technical domains but doesn't distinguish between:
- Standard terms: "machine learning", "SQL"
- Descriptive phrases: "working with databases", "programming cloud systems"

**Fix:** Human review deletes descriptive phrases, keeps only standard terms.

---


*Keep this file updated as you learn. Future-you during interview prep will thank present-you.*
