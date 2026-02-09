# Annotation Guidelines: SKILL and TOOL Extraction

These guidelines apply to both the LLM pre-annotation step and the human review that follows.

## Entity Definitions

### SKILL
A technical competency, methodology, or domain of knowledge requiring specialized training.

| English | German |
|---------|--------|
| machine learning | Maschinelles Lernen |
| deep learning | Deep Learning |
| NLP | NLP |
| computer vision | Computer Vision |
| data analysis | Datenanalyse |
| statistical analysis | statistische Analyse |
| feature engineering | Feature Engineering |
| A/B testing | A/B Testing |
| data visualization | Datenvisualisierung |
| time series analysis | Zeitreihenanalyse |
| ETL | ETL |
| MLOps | MLOps |
| DevOps | DevOps |
| CI/CD | CI/CD |
| data engineering | Datenpipelines |
| agile methodology | Agile Methodik |

### TOOL
A specific technology, programming language, framework, platform, library, or software product.

Examples: Python, R, Java, PyTorch, TensorFlow, scikit-learn, Docker, Kubernetes, AWS, Azure, GCP, SQL, PostgreSQL, Spark, Hadoop, Tableau, Power BI, Git, Jenkins, Pandas, NumPy, Hugging Face, LangChain

Tool names are almost always the same in German and English.

## What to INCLUDE

- Programming languages: Python, R, Java, Scala, Go
- ML/DL frameworks: PyTorch, TensorFlow, scikit-learn, Keras
- Cloud platforms: AWS, Azure, GCP (and specific services like S3, SageMaker, BigQuery)
- Databases: SQL, PostgreSQL, MongoDB, Redis
- Data tools: Spark, Hadoop, Kafka, Airflow, dbt
- DevOps/infra: Docker, Kubernetes, Terraform, Jenkins, Git
- Visualization: Tableau, Power BI, Matplotlib, Seaborn
- Technical methodologies: machine learning, deep learning, NLP, computer vision, MLOps, CI/CD, ETL, A/B testing, statistical modeling, data engineering, prompt engineering
- Domain knowledge when technical: Zeitreihenanalyse, Bildverarbeitung, Sprachverarbeitung

## What to EXCLUDE

| Category | Examples | Why |
|----------|----------|-----|
| Soft skills | communication, teamwork, leadership, problem-solving, Teamfähigkeit, Kommunikationsfähigkeit | Not technical |
| Job titles | Data Scientist, ML Engineer, Senior Developer | Roles, not skills |
| Vague phrases | "best practices", "high coding standards", "modern technologies", "state-of-the-art" | Too unspecific to be useful |
| Degree names | Master, PhD, Bachelor, Studium Informatik | Education, not skills |
| Experience claims | "3+ years experience", "mehrjährige Erfahrung" | Metadata, not skills |
| Company/product names | "our platform", "the product" | Not general skills/tools |
| Generic terms | "software", "code", "data", "model" | Too broad |

## Annotation Rules

1. **EXACT TEXT ONLY.** Extract terms exactly as written in the text. Do not translate or paraphrase.
2. **LANGUAGE MATCH.** If the text is in English, output English terms. If German, output German terms.
   - Text says "statistics" → output "statistics" (NOT "Statistik")
   - Text says "Statistik" → output "Statistik" (NOT "statistics")
3. **Preserve original casing.** Write it as it appears in the text.
4. **No duplicates.** If "Python" appears 5 times, list it once.
5. **Explicit mentions only.** Do not infer skills that aren't written in the text.
6. **One entity per item.** Use "machine learning" not "machine learning and deep learning".

### Common Mistakes to Avoid

| Wrong | Why | Correct |
|-------|-----|---------|
| Text: "statistics" → "Statistik" | Language mismatch | "statistics" |
| Text: "data pipelines" → "ETL" | Inference, not exact | "data pipelines" |
| Text: "cloud platforms" → "AWS, Azure, GCP" | Inference | "cloud platforms" or nothing |
| Text: "ML frameworks" → "PyTorch, TensorFlow" | Inference | Only if explicitly named |

## Edge Cases

- **"Python/R"** → two separate tools: "Python", "R"
- **"ML/DL"** → two separate skills: "ML", "DL" (or their expanded forms if written out)
- **"AWS (S3, EC2)"** → "AWS", "S3", "EC2" (list each service separately)
- **"Erfahrung in agilen Methoden"** → skill: "agile" (extract the methodology, not the sentence)
- **"Linux"** → tool (it's a specific technology, even though it's also an OS)
- **"Version Control"** → exclude if vague; include "Git" if Git is mentioned specifically

## LLM Pre-Annotation Accuracy

The Llama 3.1 8B pre-annotations achieve ~83% **entity match rate**.

### How This Metric is Calculated

```
Match Rate = Entities Found in Text / Total Entities Extracted
           = 1898 / 2278 = 83.3%
```

For each entity the LLM extracts, we search for that exact string (case-insensitive) in the source text. If found, it counts as "matched".

### What This Measures
- Whether the LLM extracted **verbatim text spans** vs inferred concepts

### What This Does NOT Measure
- **Recall**: Entities the LLM missed that ARE in the text
- **Category accuracy**: Whether SKILL vs TOOL classification is correct
- **Usefulness**: Whether extractions are valuable for downstream tasks

### For Proper NER Evaluation
A complete evaluation requires human-annotated ground truth to calculate precision, recall, and F1 scores.

### Common Errors to Watch For

### Category Errors
- **Skills in tools list** (e.g., "machine learning" listed as a tool)
- **Tools in skills list** (e.g., "Python" listed as a skill)
- **Duplicates across categories** — same item in both skills and tools

### Extraction Errors
- **Language mismatch** — German terms for English text (e.g., "Statistik" when text says "statistics")
- **Inferred concepts** — adding related terms not explicitly in text (e.g., "ETL" when text says "data pipelines")
- **Soft skills leaking in** — despite exclusion rule
- **Vague phrases** — "best practices", "high coding standards"
- **Missed entities** — especially in longer descriptions

### Text Quality Issues
- **Concatenated words** — HTML conversion artifacts like "DatenanalyseErfahrung" (should be "Datenanalyse Erfahrung")
- Entity positions may be incorrect if text wasn't cleaned before annotation
