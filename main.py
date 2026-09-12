import os
from dotenv import dotenv_values

config = dotenv_values(".env")
GROQ_API_KEY = config.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")


import os
import sqlite3
import streamlit as st
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# ─── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="SQL · Query Interface",
    page_icon="▸",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── CSS ────────────────────────────────────────────────────────
# Design statement: IBM Plex Mono EVERYWHERE — because this is a
# tool about code, and every element should speak that language.
# Light bg, single teal accent, SQL block is the only dark island.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace;
    background: #FAFAF7;
    color: #111111;
}
.stApp { background: #FAFAF7; }

.block-container {
    max-width: 740px !important;
    padding: 3.8rem 2rem 6rem !important;
}

/* ── Sidebar ────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #0F1F1E !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.4rem 2rem !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] * {
    font-family: 'IBM Plex Mono', monospace;
}

/* ── Wordmark ─────────────────────────── */
.wm {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 5.5rem;
    letter-spacing: -0.05em;
    line-height: 0.88;
    color: #111111;
    margin-bottom: 0.35rem;
    user-select: none;
}
.wm-accent { color: #00897B; }
.tagline {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 300;
    font-size: 0.7rem;
    letter-spacing: 0.16em;
    color: #C0BEB8;
    text-transform: uppercase;
    margin-bottom: 3rem;
}

/* ── Input ────────────────────────────── */
.stTextInput label { display: none !important; }
.stTextInput > div > div > input {
    font-family: 'IBM Plex Mono', monospace !important;
    background: #FFFFFF !important;
    border: 1.5px solid #E2E0DA !important;
    border-radius: 2px !important;
    color: #111111 !important;
    font-size: 0.92rem !important;
    padding: 0.88rem 1rem !important;
    caret-color: #00897B !important;
    transition: border-color 0.15s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00897B !important;
    box-shadow: 0 0 0 3px rgba(0,137,123,0.08) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: #C8C6C0 !important;
    font-style: italic;
    font-weight: 300;
}

/* ── Buttons ──────────────────────────── */
.stButton > button {
    font-family: 'IBM Plex Mono', monospace !important;
    background: #00897B !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.86rem 1.2rem !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    transition: background 0.1s !important;
}
.stButton > button:hover { background: #00796B !important; }

/* Secondary: example + history buttons */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #A8A6A0 !important;
    border: 1.5px solid #E2E0DA !important;
    font-size: 0.7rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.04em !important;
    text-transform: none !important;
    padding: 0.42rem 0.7rem !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #00897B !important;
    color: #00897B !important;
    background: rgba(0,137,123,0.05) !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: rgba(255,255,255,0.3) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    text-transform: none !important;
    letter-spacing: 0.02em !important;
    font-size: 0.7rem !important;
    padding: 0.4rem 0.7rem !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #4DB6AC !important;
    color: #4DB6AC !important;
    background: rgba(77,182,172,0.06) !important;
}

/* ── SQL output block ─────────────────── */
/* The only dark element — the design's signature move */
.sql-block {
    background: #0D1C1B;
    border-radius: 2px;
    padding: 1.3rem 1.5rem;
    margin: 1.1rem 0 0.7rem;
    position: relative;
}
.sql-block::before {
    content: '';
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 2px;
    background: #00897B;
    border-radius: 2px 0 0 2px;
}
.sql-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.57rem;
    color: rgba(77,182,172,0.45);
    letter-spacing: 0.24em;
    text-transform: uppercase;
    margin-bottom: 0.7rem;
    font-weight: 400;
}
.sql-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.94rem;
    color: #4DB6AC;
    line-height: 1.75;
    white-space: pre-wrap;
    word-break: break-all;
    font-weight: 500;
}
.sql-cursor {
    display: inline-block;
    width: 2px;
    height: 1em;
    background: #4DB6AC;
    vertical-align: sub;
    margin-left: 2px;
    animation: blink 1.2s step-end infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* ── Status ───────────────────────────── */
.status-line {
    display: flex;
    align-items: center;
    gap: 7px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 300;
    margin-bottom: 0.8rem;
}
.dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.dot-ok  { background: #00897B; animation: pulse 2s ease-in-out infinite; }
.dot-err { background: #D32F2F; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.2} }
.clr-ok  { color: #00897B; }
.clr-err { color: #D32F2F; }

/* ── Section labels ───────────────────── */
.eye {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.57rem;
    color: #C0BEB8;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    font-weight: 400;
    margin-bottom: 0.55rem;
}
.eye-teal {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.57rem;
    color: rgba(0,137,123,0.6);
    letter-spacing: 0.22em;
    text-transform: uppercase;
    font-weight: 400;
    margin-bottom: 0.55rem;
}

/* ── Scalar result ────────────────────── */
.scalar-wrap {
    display: inline-flex;
    flex-direction: column;
    background: #FFFFFF;
    border: 1.5px solid #E2E0DA;
    border-radius: 2px;
    padding: 1.6rem 2rem;
    min-width: 150px;
}
.scalar-num {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    font-size: 3.8rem;
    color: #00897B;
    line-height: 1;
    letter-spacing: -0.04em;
}
.scalar-col {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: #C0BEB8;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    margin-top: 0.5rem;
}

/* ── Divider ──────────────────────────── */
.hr {
    border: none;
    border-top: 1.5px solid #ECEAE4;
    margin: 2rem 0;
}

/* ── Sidebar internals ────────────────── */
.sb-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #4DB6AC;
    letter-spacing: -0.02em;
}
.sb-sub {
    font-size: 0.6rem;
    color: rgba(255,255,255,0.2);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-top: 0.15rem;
    margin-bottom: 1.4rem;
}
.sb-label {
    font-size: 0.57rem;
    color: rgba(255,255,255,0.22);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 1.2rem;
    margin-bottom: 0.55rem;
}
.sb-schema {
    font-size: 0.74rem;
    color: rgba(255,255,255,0.35);
    line-height: 2;
    background: rgba(0,0,0,0.2);
    border-radius: 2px;
    padding: 0.75rem 0.9rem;
}
.sb-schema .k  { color: #4DB6AC; opacity: 0.75; }
.sb-schema .col { color: rgba(255,255,255,0.6); }
.sb-stat {
    font-size: 1.6rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.03em;
    line-height: 1;
}
.sb-stat-lbl {
    font-size: 0.57rem;
    color: rgba(255,255,255,0.25);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}
.sb-hr { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 1rem 0; }

.empty-hint {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.15);
    font-style: italic;
    padding: 0.5rem 0;
}

/* DataFframe tweak */
.stDataFrame { border-radius: 2px !important; }

/* ── Hide Streamlit chrome ──────────────── */
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ─── LLM prompt ─────────────────────────────────────────────────
PROMPT = ChatPromptTemplate.from_template("""
You are an expert SQL engineer. Convert the English question into a valid SQLite query.

Database: STUDENT  
Columns: NAME (TEXT), COURSE (TEXT), SECTION (TEXT), MARKS (INTEGER)

Rules:
- Return ONLY the raw SQL. No backticks, no "sql" prefix, no explanation.
- Use double quotes for string values in WHERE clauses.
- Valid SQLite syntax only.

Examples:
Q: How many students?           → SELECT COUNT(*) FROM STUDENT;
Q: All in Data Science?         → SELECT * FROM STUDENT WHERE COURSE="Data Science";
Q: Top 5 by marks?              → SELECT NAME, MARKS FROM STUDENT ORDER BY MARKS DESC LIMIT 5;
Q: Average marks per course?    → SELECT COURSE, ROUND(AVG(MARKS),1) AS AVG_MARKS FROM STUDENT GROUP BY COURSE ORDER BY AVG_MARKS DESC;
Q: Students who scored above 80? → SELECT * FROM STUDENT WHERE MARKS > 80;

Convert this: {user_query}
""")


def load_llm():
    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing from .env and environment.")
        st.stop()
    return ChatGroq(groq_api_key=GROQ_API_KEY, model_name="openai/gpt-oss-20b")


def get_sql(question: str) -> str:
    chain = PROMPT | load_llm() | StrOutputParser()
    return chain.invoke({"user_query": question}).strip()


# ─── DB helpers ──────────────────────────────────────────────────
DB = "student.db"

def run_sql(sql: str) -> tuple[list, list]:
    with sqlite3.connect(DB) as conn:
        cur = conn.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return rows, cols

def db_stats() -> dict:
    try:
        with sqlite3.connect(DB) as conn:
            n = conn.execute("SELECT COUNT(*) FROM STUDENT").fetchone()[0]
            c = conn.execute("SELECT COUNT(DISTINCT COURSE) FROM STUDENT").fetchone()[0]
            return {"rows": n, "courses": c}
    except Exception:
        return {"rows": "—", "courses": "—"}


# ─── Quick examples ──────────────────────────────────────────────
EXAMPLES = [
    "Show all students",
    "Count per course",
    "Top 5 by marks",
    "Who scored highest?",
    "Marks above 80",
    "Avg by section",
]

# ─── Session state ───────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "prefill" not in st.session_state:
    st.session_state.prefill = ""


# ════════════════════════════════════════════════════════════════
#  SIDEBAR
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    stats = db_stats()

    st.markdown(f"""
    <div class="sb-name">▸ STUDENT.db</div>
    <div class="sb-sub">{stats['rows']} rows · {stats['courses']} courses</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-hr"></div>', unsafe_allow_html=True)

    # Stats
    st.markdown('<div class="sb-label">Database</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="sb-stat">{stats["rows"]}</div><div class="sb-stat-lbl">Total rows</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="sb-stat">{stats["courses"]}</div><div class="sb-stat-lbl">Courses</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-hr"></div>', unsafe_allow_html=True)

    # Schema
    st.markdown('<div class="sb-label">Schema</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sb-schema">
      <span class="k">TABLE</span> STUDENT (<br>
      &nbsp;&nbsp;<span class="col">NAME</span>&nbsp;&nbsp;&nbsp;&nbsp;TEXT,<br>
      &nbsp;&nbsp;<span class="col">COURSE</span>&nbsp;&nbsp;TEXT,<br>
      &nbsp;&nbsp;<span class="col">SECTION</span>&nbsp;TEXT,<br>
      &nbsp;&nbsp;<span class="col">MARKS</span>&nbsp;&nbsp;&nbsp;INT<br>
      );
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-hr"></div>', unsafe_allow_html=True)

    # History
    st.markdown('<div class="sb-label">Recent</div>', unsafe_allow_html=True)
    if st.session_state.history:
        for i, h in enumerate(reversed(st.session_state.history[-7:])):
            q = h["query"]
            label = q if len(q) <= 28 else q[:26] + "…"
            if st.button(f"↺  {label}", key=f"hist_{i}", use_container_width=True):
                st.session_state.prefill = h["query"]
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.markdown('<div class="empty-hint">no queries yet</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ════════════════════════════════════════════════════════════════

# ── Wordmark ─────────────────────────────────────────────────────
st.markdown("""
<div class="wm">TXT<wbr><span class="wm-accent">▸</span>SQL</div>
<div class="tagline">▸ natural language · database interface</div>
""", unsafe_allow_html=True)

# ── Example chips ─────────────────────────────────────────────────
st.markdown('<div class="eye">Quick queries</div>', unsafe_allow_html=True)
chip_cols = st.columns(3)
for i, ex in enumerate(EXAMPLES):
    with chip_cols[i % 3]:
        if st.button(ex, key=f"ex_{i}", type="secondary", use_container_width=True):
            st.session_state.prefill = ex
            st.rerun()

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# ── Input row ─────────────────────────────────────────────────────
input_col, btn_col = st.columns([5, 1])
with input_col:
    user_query = st.text_input(
        "query",
        value=st.session_state.prefill,
        placeholder="ask your database anything…",
        label_visibility="collapsed",
    )
with btn_col:
    run = st.button("Run ▸", use_container_width=True)


# ─── Execution ───────────────────────────────────────────────────
if run:
    if not user_query.strip():
        st.warning("Type a question first.")
        st.stop()

    st.session_state.prefill = ""

    # Step 1: generate SQL
    with st.spinner(""):
        try:
            sql = get_sql(user_query)
        except Exception as e:
            st.error(f"LLM error: {e}")
            st.stop()

    # ── Show SQL — the dark island in the light page
    st.markdown('<div class="eye-teal">Generated query</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sql-block">'
        f'<div class="sql-eyebrow">▸ SQLite · STUDENT.db</div>'
        f'<div class="sql-text">{sql}<span class="sql-cursor"></span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Step 2: run query
    try:
        rows, col_names = run_sql(sql)
        error = None
    except Exception as e:
        rows, col_names, error = [], [], str(e)

    if error:
        st.markdown(
            f'<div class="status-line">'
            f'<div class="dot dot-err"></div>'
            f'<span class="clr-err">query failed — {error}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption("Rephrase your question — the model may have generated invalid SQL.")

    else:
        n = len(rows)
        st.markdown(
            f'<div class="status-line">'
            f'<div class="dot dot-ok"></div>'
            f'<span class="clr-ok">{n} row{"s" if n != 1 else ""} returned</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="eye" style="margin-top:0.5rem">Results</div>', unsafe_allow_html=True)

        if n == 0:
            st.markdown(
                '<div style="font-size:0.8rem;color:#C0BEB8;font-style:italic;padding:1rem 0">no records matched</div>',
                unsafe_allow_html=True,
            )

        elif len(col_names) == 1 and n == 1:
            # Single scalar: COUNT, AVG, MAX etc. — show as big number
            val = rows[0][0]
            st.markdown(
                f'<div class="scalar-wrap">'
                f'<div class="scalar-num">{val}</div>'
                f'<div class="scalar-col">{col_names[0]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        else:
            df = pd.DataFrame(rows, columns=col_names)
            st.dataframe(df, use_container_width=True, hide_index=True)

        # Save history
        st.session_state.history.append({
            "query": user_query,
            "sql":   sql,
            "rows":  n,
        })

elif not run:
    st.markdown(
        '<div style="font-size:0.68rem;color:#DEDAD4;text-align:left;margin-top:0.5rem;font-style:italic;font-weight:300">'
        'type a question or pick an example above</div>',
        unsafe_allow_html=True,
    )
