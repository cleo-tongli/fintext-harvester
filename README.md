# FinText Harvester

**FinText Harvester** is a powerful data ingestion engine designed to fetch, clean, and consolidate financial news text from major public sources (CNBC, Yahoo Finance, MarketWatch, Nasdaq, etc.) into a structured, daily-partitioned format.

Ideally suited for NLP research, sentiment analysis, and financial modeling, this tool handles the complexity of scraping, normalization, and deduplication so you can focus on the data itself.

## 🚀 Key Features

*   **Multi-Source Ingestion**: Fetches articles via RSS feeds and GDELT domain slices.
*   **Intelligent Normalization**: Standardizes diverse article formats into a unified schema (`url`, `title`, `description`, `published_at`, `text`, `source`).
*   **Deduplication**: Eliminates duplicate articles across sources using `url_hash` and canonical URLs.
*   **Structured Output**: Exports clean data to **JSONL** (for streaming) and **Parquet** (for efficient analytics/pandas).
*   **Daily Partitioning**: Organizes data into `data/bronze/YYYY-MM-DD/` directories for easy time-series access.
*   **Docker Ready**: Fully containerized for reliable, reproducible deployment.

---

## 🛠️ Project Structure

```
fintext-harvester/
├── config/                 # Configuration files
├── data/                   # Data storage (bronze/silver layers)
├── docker/                 # Dockerfile and related scripts
├── scripts/                # Utility scripts for backfilling & maintenance
├── src/                    # Source code
│   ├── adapters/           # Source-specific parsers
│   ├── core/               # Core logic (Fetcher, Extractor, Normalizer)
│   └── pipeline.py         # Main orchestration pipeline
├── Dockerfile              # Container definition
├── Makefile                # Command shortcuts
├── requirements.txt        # Python dependencies
└── docker-compose.yml      # Service orchestration
```

---

## 📦 Installation

### Prerequisites

*   **Docker** (Recommended)
*   **Python 3.10+** (For local execution)

### Option 1: Docker (Fastest)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/cleo-tongli/fintext-harvester.git
    cd fintext-harvester
    ```

2.  **Build the image:**
    ```bash
    docker compose build
    # OR
    make build
    ```

### Option 2: Local Python Environment

1.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 🏃 Usage

### Running via Docker

**Start the harvester (background mode):**
```bash
make up
# OR
docker compose up -d
```

**View logs:**
```bash
make logs
```

**Run a one-off backfill job (e.g., last 30 days):**
```bash
make run-once
```

### Configuration (Environment Variables)

You can configure the behavior via `.env` file or Docker environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `GDELT_BACKFILL_DAYS` | Number of past days to check in GDELT | `30` |
| `GDELT_SLICES_PER_DAY` | Number of GDELT slices to process per day | `12` |
| `GDELT_DOMAINS` | Comma-separated list of domains to track | `cnbc.com,finance.yahoo.com,...` |
| `MIN_TEXT_CHARS` | Minimum article length to keep | `500` |
| `FILTER_YH_NEWS` | Enable specific Yahoo Finance filters | `1` |

### Manual Backfill Command

To manually trigger a backfill and deduplication process using Docker:

```bash
docker run --rm --entrypoint /usr/bin/env \
  -e GDELT_BACKFILL_DAYS=30 \
  -e GDELT_DOMAINS="cnbc.com,finance.yahoo.com,marketwatch.com,nasdaq.com" \
  -v "$PWD/data:/app/data" \
  tongliyn/fintext-harvester:latest \
  bash -lc "python /app/scripts/backfill_gdelt_domains.py && DEDUPE_DAYS=all python /app/scripts/dedupe_repair.py"
```

---

## 📊 Data Output

Data is stored in the `data/bronze/` directory, partitioned by date:

```
data/bronze/2023-10-27/
├── docs.jsonl              # Raw collected articles
├── docs_dedup.jsonl        # Deduplicated articles
└── docs_dedup.parquet      # Deduplicated articles (Parquet format)
```

Each record contains:
*   `url`: Original article URL
*   `url_hash`: Unique hash for deduplication
*   `title`: Article headline
*   `description`: Brief summary/snippet
*   `published_at`: ISO 8601 timestamp
*   `source`: Domain source (e.g., cnbc.com)
*   `text`: Full article body text

---

## 🤝 Contributing

Contributions are welcome! Please submit a Pull Request or open an Issue for any bugs or feature requests.

1.  Fork the repo
2.  Create your feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request
