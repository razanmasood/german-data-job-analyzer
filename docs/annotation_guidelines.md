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

1. **Preserve original language.** Use "Statistik" if the description says "Statistik", not "Statistics".
2. **Preserve original casing.** Write it as it appears in the text.
3. **No duplicates.** If "Python" appears 5 times, list it once.
4. **Explicit mentions only.** Do not infer skills that aren't written in the text.
5. **One entity per item.** Use "machine learning" not "machine learning and deep learning".

## Edge Cases

- **"Python/R"** → two separate tools: "Python", "R"
- **"ML/DL"** → two separate skills: "ML", "DL" (or their expanded forms if written out)
- **"AWS (S3, EC2)"** → "AWS", "S3", "EC2" (list each service separately)
- **"Erfahrung in agilen Methoden"** → skill: "agile" (extract the methodology, not the sentence)
- **"Linux"** → tool (it's a specific technology, even though it's also an OS)
- **"Version Control"** → exclude if vague; include "Git" if Git is mentioned specifically

## LLM Pre-Annotation Accuracy

The Llama 3.1 8B pre-annotations are approximately 80% accurate. Common errors to watch for during human review:

- **Skills appearing in the tools list** (e.g., "machine learning" listed as a tool)
- **Tools appearing in the skills list** (e.g., "Python" listed as a skill)
- **Soft skills leaking in** despite the exclusion rule
- **Vague phrases** like "best practices" or "high coding standards" being extracted
- **Missed entities** in longer descriptions — the LLM occasionally skips items
- **Duplicates across categories** — the same item in both skills and tools
