# Text-to-SQL-AI
Natural language to SQL interface — type plain English, get query results instantly. Built with LangChain, Groq (Llama 3.1), and Streamlit.

# TXT▸SQL — Natural Language Database Interface

A Streamlit app that converts plain English questions into SQL queries and runs them against a SQLite database in real time — powered by LangChain + Groq (Llama 3.1).

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.x-green?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-Llama_3.1-orange?style=flat-square)

---

## What it does

Type a question in plain English → get the SQL query generated instantly → results shown in a clean table.

No SQL knowledge needed.

---

## Demo

> "Who scored the highest marks?"
> → `SELECT NAME, MARKS FROM STUDENT ORDER BY MARKS DESC LIMIT 1;`

> "Average marks per course?"
> → `SELECT COURSE, ROUND(AVG(MARKS), 1) AS AVG_MARKS FROM STUDENT GROUP BY COURSE;`

---

## Features

- Natural language to SQL using Llama 3.1 via Groq API
- Live query execution against SQLite
- Query history with one-click re-run
- Scalar results (COUNT, AVG, MAX) displayed as big numbers
- Database schema and stats in sidebar
- Quick example queries to get started

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| LLM | Llama 3.1 8B Instant (Groq) |
| LLM Framework | LangChain |
| Database | SQLite |
| Env Management | python-dotenv |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/taranshrathore/text-to-sql-ai.git
cd text-to-sql-ai
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your environment variables

Create a `.env` file in the root directory:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key at [console.groq.com](https://console.groq.com)

### 5. Set up the database

Make sure `student.db` exists in the root directory with a `STUDENT` table:

```sql
CREATE TABLE STUDENT (
    NAME    TEXT,
    COURSE  TEXT,
    SECTION TEXT,
    MARKS   INTEGER
);
```

### 6. Run the app

```bash
streamlit run main.py
```

---

## Project Structure

```
text-to-sql-ai/
├── main.py              # Streamlit app + LangChain pipeline
├── student.db           # SQLite database (not tracked in git)
├── .env                 # API keys (not tracked in git)
├── requirements.txt     # Dependencies
└── README.md
```

---

## Requirements

Create a `requirements.txt` with:

```
streamlit
langchain
langchain-groq
python-dotenv
pandas
```

---

## Author

**Taransh Rathore**
[GitHub](https://github.com/taranshrathore) · [LinkedIn](https://linkedin.com/in/taransh-rathore)
