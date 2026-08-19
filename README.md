# RetainIQ

**Predicts which e-commerce customers are about to churn, explains why in plain language, and drafts a grounded, personalized retention offer for each one — reviewed by a human before it goes out.**

[![Python](https://img.shields.io/badge/Python-3.11-blue)]()
[![Flask](https://img.shields.io/badge/Flask-3.0-black)]()
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-orange)]()
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1)]()

## 🎥 Demo

[Watch the walkthrough](#) *(video link coming soon)*

## The problem

Online retailers lose a disproportionate share of revenue to high-value customers who go quiet with no warning. By the time a customer has been inactive long enough to obviously be "gone," it's to[...]

## What it does

1. Cleans and loads real e-commerce transaction data into MySQL
2. Engineers customer-level behavioral features (Recency, Frequency, Monetary, estimated CLV)
3. Trains an XGBoost classifier to predict churn probability per customer
4. Explains *why* each customer is flagged, using SHAP — not just a probability, a reason
5. Uses an LLM agent to draft a personalized, grounded retention email based on that customer's real purchase history and specific risk factors
6. Surfaces everything in a review dashboard for a human to approve before any action is taken

## Project Structure

```
.
├── README.md                   # Project overview & this structure
├── LICENSE
├── .env.example                # Example env vars (DB, LLM provider)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── scripts/                    # Convenience scripts
│   ├── run_pipeline.sh         # Full ETL -> train -> score pipeline
│   |__ shap_summary.py         # Shap summary
├── data/                       # Datasets (not committed: add to .gitignore)
│   ├── raw/                    # Original downloads (UCI dataset)
│   |___ processed/             # Cleaned/engineered CSVs
├── sql/
│   ├── schema.sql              # DB schema creation
├── src/                        # Application source code
│   ├── api/
│   │   ├── app.py              # Flask app entrypoint
│   │   ├── routes.py           # Routes for app
│   │   └── db.py               # Database credentials
│   ├── agent/
│   │   ├── retention_agent.py  # LLM agent setup
│   │   └── prompts.py          # Prompt for the LLM
│   ├── data/
│   │   ├── clean.py            # Cleaning the data
│   │   └── load_to_db.py       # Loading data into the database
│   ├── features/
│   │   ├── rfm.py              # making features 
│   ├── models/
│   │   ├── train.py            # training the model   
│   │   ├── predict.py          # predecting the outcomes
|   |   |---evaluate.py         # evaluate the business outcomes
│   │   ├── explain.py          # explain the prediction using SHAP
│   │   └── model_selection.ipynb
├── dashboard/                  # Review UI
│   ├── templates/              
│   │   └── index.html          # interactive dashboard
│   └── static/
│       ├── css/
├── notebooks/                  # EDA & experiments
│   └── 01_eda.ipynb
|   |__ books_data.html         # entire EDA in this file
├── tests/
│   ├── test_api.py
│   └── test_features.py
├── docs/                       # Additional docs and architecture notes
│   ├── shap.png                # SHAP scores
```

## Architecture

```
Raw transactions (UCI Online Retail II)
        |
   src/data/clean.py            -> data/processed/transactions_clean.csv
        |
   src/data/load_to_db.py       -> MySQL: customers, transactions
        |
   src/features/rfm.py          -> MySQL: rfm_features
        |                         (recency_ratio, frequency, monetary,
        |                         avg_order_value, estimated_clv, is_churned)
   src/models/
   model_selection.ipnb         -> Selection of model based on performance
        |
   src/models/train.py          -> churn_model.pkl (XGBoost)
        |
   src/models/predict.py        -> MySQL: churn_predictions
        |
   src/models/explain.py        -> SHAP: per-customer risk factors
        |
   Flask API (src/api/app.py)   -> at-risk list | explain | generate-action
        |
   src/agent/retention_agent.py  -> LLM call grounded in customer data + SHAP reasons
        |
   Dashboard (dashboard/templates/index.html) -> review generated retention actions
```

## Tech stack

| Layer | Tools |
|---|---|
| Data & features | Python, pandas, SQLAlchemy |
| Modeling | XGBoost, scikit-learn |
| Explainability | SHAP (`TreeExplainer`) |
| Storage | MySQL |
| API | Flask |
| Agent | Ollama (local, free — default) or Claude API (optional, faster) |
| Dashboard | HTML/JS |
| Containerization | Docker, Docker Compose |
| Testing | pytest |

## Results

Trained and evaluated on a real dataset — not a synthetic or pre-cleaned Kaggle sample.

**Dataset**
- ~779,425 cleaned transaction line items
- 5,500+ unique customers
- Source: UCI "Online Retail II" — real UK-based online retailer transactions

**Model performance** *(held-out test set, not cross-validation)*
- ROC-AUC: **0.928**
- Precision (churned class): **0.83**
- Recall (churned class): **0.97**
- Overall churn rate in the data: **61%**

**Business impact**
- Customers flagged at-risk: **3,501**
- Total estimated CLV flagged at-risk: **$5,758,699.22**
- Projected value protected: **$863,804.88**, *assuming a 15% win-back rate on contacted customers — this is a stated assumption, not a measured outcome, since there was no A/B control group.*

**A note on the churn rate:** at 61%, "at-risk" describes the majority of the customer base, not a rare minority — expected for a non-subscription retailer where many customers buy once or twice[...]

## Why the model can be trusted, not just its score

- Evaluated on a genuine **held-out test set**, separate from the folds used for model selection — avoids the optimistic bias of tuning and reporting on the same data.
- Compared against a logistic regression baseline before committing to XGBoost.
- Features were deliberately chosen to avoid label leakage: `recency_ratio` (a customer's overdue-ness relative to *their own* historical buying rhythm) is used instead of raw `recency_days`, whic[...]
- `customer_id`, `invoice_no`, and `stock_code` are never fed to the model — they're identifiers, not behavioral signal.

## Explainability (SHAP)

Every flagged customer comes with a plain-language "why," not just a probability:

```
Top factors for customer 12346:
• how overdue they are relative to their usual buying rhythm (increases risk)
• how often they order (decreases risk)
• their average order size (decreases risk)
```

This directly shapes the retention agent's output — a customer flagged mainly for being overdue gets different email framing and offer logic than one flagged for shrinking order value.

## Setup

```bash
git clone <this-repo>
cd retainiq
cp .env.example .env          # edit with your DB credentials + LLM provider
docker compose up -d db       # starts MySQL, applies sql/schema.sql
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Download the [UCI Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) into `data/raw/`, then:

```bash
bash scripts/run_pipeline.sh    # clean -> load -> features -> train -> score
python -m src.api.app           # visit http://localhost:5000
```

The agent defaults to a local Ollama model (`llama3.2`), keeping the project runnable at **$0 cost**. Set `LLM_PROVIDER=anthropic` in `.env` for faster (paid) responses.

## Testing

```bash
pytest tests/
```

## Known limitations / honest scope

This project is intentionally scoped for what's been built and verified — not overclaimed:

- **CLV formula is a heuristic**, not a full probabilistic model — `estimated_clv` uses historical spend scaled by a fixed multiplier. A proper BG/NBD + Gamma-Gamma model (via the `lifetimes` librar[...]
- **Label-lag isn't yet accounted for.** Customers whose first purchase is too recent to have a settled 90-day churn outcome aren't currently excluded from training — a production version shoul[...]
- **Approve/send flow exists at the API level** (`POST /api/customers/<id>/approve`) but isn't yet wired into the dashboard UI — currently reachable via direct API call only.
- **No scheduled retraining or scoring pipeline yet.** In production this would split into a frequent scoring job (re-score new customers with the current model) and an infrequent retraining job [...]
- **No live deployment.** Demonstrated via a recorded walkthrough and a fully reproducible local/Docker setup rather than a hosted free-tier link, to avoid cold-start delays misrepresenting the p[...]

## License

MIT
