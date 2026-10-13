import hashlib
import html
import os
import tempfile

import streamlit as st

import rag_engine

# ------------------------------------------------------------
# Research Paper Copilot — responsive UI (phone + laptop)
# Works with rag_engine.py. Also add .streamlit/config.toml (light theme).
# ------------------------------------------------------------

st.set_page_config(
    page_title="Research Paper Copilot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="auto",
)

# ---- Visual system ----------------------------------------------------------
st.markdown(
    r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

:root {
  color-scheme: light only;
  --ink: #172344;
  --muted: #5b6a8c;
  --line: #d9e3fa;
}
html, body, .stApp, [class*="css"] { font-family: 'DM Sans', sans-serif; color-scheme: light only; }

/* ---------- App background & base text ---------- */
.stApp {
  background:
    radial-gradient(ellipse at 78% 5%, rgba(176,162,255,.28), transparent 36%),
    radial-gradient(ellipse at 28% 65%, rgba(122,177,255,.20), transparent 35%),
    linear-gradient(135deg, #edf4ff 0%, #f4f1ff 52%, #edf6ff 100%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMain"] .block-container {
  max-width: 1500px; padding: 1.2rem 2rem 2rem;
}
[data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3,
[data-testid="stMain"] p, [data-testid="stMain"] li, [data-testid="stMain"] label,
[data-testid="stMain"] [data-testid="stMarkdownContainer"],
[data-testid="stMain"] [data-testid="stCaptionContainer"] {
  color: var(--ink);
}
[data-testid="stMain"] [data-testid="stCaptionContainer"] { color: var(--muted); }

/* ---------- Panels = real bordered containers ---------- */
[data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255,255,255,.94);
  border: 1px solid #d5e0f7 !important;
  border-radius: 18px;
  box-shadow: 0 8px 24px rgba(55,78,145,.06);
}
.panel-title { font: 800 1.02rem 'Manrope', sans-serif; color: var(--ink); margin: 0 0 4px; }
.muted { color: var(--muted); font-size: .86rem; line-height: 1.5; }

/* ---------- Hero ---------- */
.hero {
  position: relative; overflow: hidden; border-radius: 20px;
  padding: 28px 34px; margin-bottom: 16px;
  background:
    radial-gradient(circle at 80% 20%, rgba(133,84,255,.55), transparent 23%),
    radial-gradient(circle at 67% 105%, rgba(52,120,255,.55), transparent 30%),
    linear-gradient(110deg,#101b45 0%,#101e50 52%,#21175d 100%);
  box-shadow: 0 16px 38px rgba(51,76,166,.18);
}
.hero:after {
  content:"✦   ·      ✧       ·   ✦       ·      ✧";
  position:absolute; right:25px; top:24px; width:39%; height:100%;
  color:rgba(215,224,255,.45); font-size:22px; letter-spacing:16px;
  line-height:2.5; pointer-events:none;
}
.hero .kicker { font-size:.7rem; font-weight:700; letter-spacing:1.4px; margin-bottom:8px; }
.hero h1 { font: 800 clamp(1.7rem,3vw,2.6rem) 'Manrope',sans-serif; margin:0 0 8px; letter-spacing:-1px; }
.hero p { font-size:1.02rem; line-height:1.55; margin:0; max-width:640px; }
.pills { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
.pill { display:inline-block; border:1px solid rgba(180,205,255,.7); border-radius:999px;
        padding:6px 12px; font-size:.78rem; background:rgba(7,25,70,.45); }
/* hero colours — placed last + !important so nothing else can override them */
.stApp .hero, .stApp .hero h1, .stApp .hero p, .stApp .hero .pill,
.stApp .hero [data-testid="stMarkdownContainer"] p { color:#ffffff !important; }
.stApp .hero h1 span { color:#ecd5ff !important; }
.stApp .hero .kicker { color:#c4d4ff !important; }

/* ---------- Buttons (main area): always light with dark text ---------- */
[data-testid="stMain"] button[kind="secondary"],
[data-testid="stMain"] [data-testid="stBaseButton-secondary"] {
  background: #f3f7ff !important;
  color: var(--ink) !important;
  border: 1px solid #c9d8f5 !important;
  border-radius: 12px;
  min-height: 2.8rem;
  height: auto;
  padding: .55rem .9rem;
  text-align: left;
  justify-content: flex-start;
}
[data-testid="stMain"] button[kind="secondary"]:hover,
[data-testid="stMain"] [data-testid="stBaseButton-secondary"]:hover {
  background: #e4eeff !important; border-color: #8fb0f2 !important; color: #0f1c4d !important;
}
[data-testid="stMain"] button[kind="secondary"] *,
[data-testid="stMain"] [data-testid="stBaseButton-secondary"] * {
  color: inherit !important;
  white-space: normal !important;      /* no more "…" truncation on phones */
  text-align: left;
  line-height: 1.35;
}
button[kind="primary"], [data-testid="stBaseButton-primary"] {
  background: linear-gradient(110deg,#2168f5,#8150ef) !important;
  color: #ffffff !important; border: 0 !important; border-radius: 12px;
  font-weight: 700; min-height: 2.8rem;
  box-shadow: 0 6px 15px rgba(85,81,225,.22);
}
button[kind="primary"] *, [data-testid="stBaseButton-primary"] * { color:#ffffff !important; }

/* ---------- Inputs ---------- */
[data-testid="stMain"] input, [data-testid="stMain"] textarea {
  background:#ffffff !important; color: var(--ink) !important;
  -webkit-text-fill-color: var(--ink) !important; caret-color: var(--ink);
  font-size: 16px !important;   /* stops iOS zoom-on-focus */
}
[data-testid="stMain"] [data-baseweb="input"], [data-testid="stMain"] [data-baseweb="base-input"] {
  background:#ffffff !important; border-color:#b9c9e8 !important; border-radius:12px !important;
}
[data-testid="stMain"] input::placeholder { color:#6b7898 !important; -webkit-text-fill-color:#6b7898 !important; opacity:1 !important; }

/* ---------- File uploader (was dark + unreadable on phone) ---------- */
[data-testid="stFileUploaderDropzone"] {
  background:#f6f9ff !important; border:1.5px dashed #8fb0f2 !important; border-radius:14px;
}
[data-testid="stFileUploaderDropzone"] *,
[data-testid="stFileUploaderDropzoneInstructions"] * { color: var(--ink) !important; }
[data-testid="stFileUploaderDropzone"] button {
  background:#ffffff !important; border:1px solid #9db8ee !important; color: var(--ink) !important;
}
[data-testid="stFileUploaderFile"], [data-testid="stFileUploaderFile"] * { color: var(--ink) !important; }

/* ---------- Expanders / alerts / containers ---------- */
[data-testid="stMain"] [data-testid="stExpander"] {
  background:#fbfdff; border:1px solid #dbe5f8; border-radius:12px;
}
[data-testid="stMain"] [data-testid="stExpander"] summary,
[data-testid="stMain"] [data-testid="stExpander"] summary *,
[data-testid="stMain"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {
  color: var(--ink) !important; background: transparent;
}
[data-testid="stMain"] [data-testid="stAlert"] * { color: var(--ink) !important; }

/* ---------- Small components ---------- */
.paper-file {
  background:linear-gradient(110deg,#f7faff,#edf4ff); border:1px solid #d6e3fb;
  border-radius:13px; padding:12px; display:flex; gap:12px; align-items:center;
}
.paper-file b, .paper-file span, .paper-file div { color: var(--ink); }
.paper-file .muted { color: var(--muted); }
.pdf-icon { background:#ffebe9; color:#d93636 !important; border-radius:9px; padding:10px; font-weight:800; font-size:.8rem; }
.status { display:inline-block; border-radius:99px; background:#d9f9eb; color:#066a49 !important; padding:4px 10px; font-size:.72rem; font-weight:600; white-space:nowrap; }
.stat { text-align:center; background:linear-gradient(145deg,#eef6ff,#e9f0ff); border:1px solid #d9e5fb; border-radius:10px; padding:10px 4px; }
.stat strong { display:block; font-size:1.05rem; color:#172656 !important; }
.stat span { color:#5b6a8c !important; font-size:.72rem; }
.footer { text-align:center; color:#6b7898; font-size:.78rem; padding:18px; }

/* ---------- Sidebar (dark) ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(165deg, #101b3b 0%, #111d45 56%, #271b68 100%);
  border-right: 1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] *, [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
  color: #eaf0ff;
}
[data-testid="stSidebar"] button[kind="secondary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
  background: rgba(255,255,255,.07) !important; border: 1px solid rgba(255,255,255,.12) !important;
  border-radius: 12px; padding: .6rem .8rem; justify-content: flex-start; text-align: left;
}
[data-testid="stSidebar"] button[kind="secondary"] *,
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] * { color:#f0f4ff !important; }
[data-testid="stSidebar"] button[kind="secondary"]:hover { background: rgba(255,255,255,.16) !important; }
[data-testid="stSidebar"] button[kind="primary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] { justify-content:flex-start; box-shadow:none; }
.brand { text-align:center; padding: 8px 8px 22px; }
.brand-icon { font-size: 2.4rem; }
.brand-title { font: 800 1.25rem 'Manrope', sans-serif; line-height:1.2; margin-top:8px; }
.brand-sub { color:#b9c9ee !important; font-size:.83rem; line-height:1.5; margin-top:9px; }
.sidebar-note { margin-top: 26px; border:1px solid rgba(166,192,255,.25); background:rgba(255,255,255,.05);
  border-radius:16px; padding:16px; line-height:1.6; font-size:.86rem; }
[data-testid="stSidebar"] .sidebar-note, [data-testid="stSidebar"] .sidebar-note * { color:#d8e5ff !important; }

/* ---------- Mobile ---------- */
@media (max-width: 900px) {
  [data-testid="stMain"] .block-container { padding: .8rem 1rem 2rem; }
  .hero { padding: 22px 20px; border-radius: 16px; }
  .hero:after { display:none; }
  .hero h1 { font-size: 1.7rem !important; line-height: 1.2 !important; }
  .hero p { font-size: .98rem !important; }
  .hero p br { display:none; }
  .pill { font-size:.74rem; padding:5px 10px; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ---- Helpers ----------------------------------------------------------------
@st.cache_resource(show_spinner=False, max_entries=3)
def prepare_paper(file_bytes: bytes, filename: str):
    """Extract, chunk and index a PDF once; cached per unique file content."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        pdf_path = tmp.name
    try:
        pages = rag_engine.extract_pdf_pages(pdf_path)
        chunks = rag_engine.create_document_chunks(pages)
        if not chunks:
            raise ValueError(
                "No extractable text was found in this PDF. If it is scanned, OCR is needed."
            )
        vector_index, _ = rag_engine.build_vector_index(chunks)
        bm25_index = rag_engine.build_bm25_index(chunks)
        return {
            "chunks": chunks,
            "vector_index": vector_index,
            "bm25_index": bm25_index,
            "n_pages": len({p["page"] for p in pages}),
            "n_chunks": len(chunks),
        }
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


def go(page):
    st.session_state.active_nav = page


def set_question(q):
    st.session_state.question = q


def get_secret(name, default=""):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name, default)


def safe_md(text):
    """Escape $ so answers containing prices/numbers are not rendered as LaTeX."""
    return (text or "").replace("$", "\\$")


# ---- State ------------------------------------------------------------------
st.session_state.setdefault("active_nav", "Home")
st.session_state.setdefault("question", "")
st.session_state.setdefault("paper", None)  # {"name": str, "bytes": bytes}

# ---- Sidebar ----------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
          <div class="brand-icon">📚</div>
          <div class="brand-title">Research Paper<br>Copilot</div>
          <div class="brand-sub">Upload. Ask. Explore.<br>With Evidence.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for label, icon in [("Home", "⌂"), ("My Papers", "▤"), ("Insights", "⌁"), ("Settings", "⚙")]:
        st.button(
            f"{icon}   {label}",
            key=f"nav_{label}",
            use_container_width=True,
            type="primary" if st.session_state.active_nav == label else "secondary",
            on_click=go,
            args=(label,),
        )
    st.markdown(
        """
        <div class="sidebar-note">
          <div style="font-size:1.5rem">💡</div>
          <b>Turn research papers into understanding.</b><br><br>
          Ask questions, get answers with citations, and explore key insights — all in one place.
        </div>
        <div style="height:16px"></div>
        <div style="font-size:.8rem;opacity:.85">Powered by RAG · FAISS · BM25 · Groq</div>
        """,
        unsafe_allow_html=True,
    )

nav = st.session_state.active_nav
if nav == "Chat":  # legacy value
    nav = st.session_state.active_nav = "Home"

# ---- My Papers --------------------------------------------------------------
if nav == "My Papers":
    st.markdown("## 📚 My Papers")
    st.caption("Manage the research paper in your current session.")
    paper = st.session_state.paper
    with st.container(border=True):
        if paper:
            size_mb = len(paper["bytes"]) / (1024 * 1024)
            st.markdown(
                f"<div class='paper-file'><div class='pdf-icon'>PDF</div>"
                f"<div style='min-width:0;flex:1'><b>{html.escape(paper['name'])}</b><br>"
                f"<span class='muted'>{size_mb:.2f} MB · Available in this session</span></div>"
                f"<span class='status'>Uploaded</span></div>",
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns(2)
            c1.button("Open paper workspace", type="primary", use_container_width=True, on_click=go, args=("Home",))
            if c2.button("Remove paper", use_container_width=True):
                st.session_state.paper = None
                st.session_state.pop("last_result", None)
                st.rerun()
        else:
            st.info("No paper is uploaded in this session yet.")
            st.button("Go to Home to upload a PDF", type="primary", on_click=go, args=("Home",))
    st.stop()

# ---- Insights ---------------------------------------------------------------
if nav == "Insights":
    st.markdown("## ✨ Research Insights")
    st.caption("Use the paper workspace to ask evidence-based questions about the document.")
    with st.container(border=True):
        st.markdown(
            """
**What you can explore**

- **Research contributions** — the problem and what the authors add.
- **Methods** — the proposed approach and model design.
- **Experiments** — datasets, evaluation metrics, and reported results.
- **Limitations** — weaknesses or future work the paper states.

Answers are grounded in retrieved PDF passages and include source-page evidence.
"""
        )
        st.button("Start exploring this paper", type="primary", on_click=go, args=("Home",))
    st.stop()

# ---- Settings ---------------------------------------------------------------
if nav == "Settings":
    st.markdown("## ⚙️ Settings")
    st.caption("Current application configuration and pipeline details.")
    with st.container(border=True):
        st.markdown(
            """
**RAG pipeline**

- **PDF extraction:** PyMuPDF
- **Semantic retrieval:** Sentence Transformers + FAISS
- **Keyword retrieval:** BM25
- **Ranking:** Reciprocal Rank Fusion (hybrid search)
- **Answer generation:** Groq

Credentials are managed privately through Streamlit Secrets and are never displayed here.
"""
        )
        st.button("Return to workspace", type="primary", on_click=go, args=("Home",))
    st.stop()

# ---- Hero -------------------------------------------------------------------
st.markdown(
    """
    <section class="hero">
      <div class="kicker">YOUR PERSONAL RESEARCH WORKSPACE</div>
      <h1>Your AI <span>Research Partner</span></h1>
      <p>Upload a research paper, ask questions, and get accurate answers
      grounded in retrieved passages from your document.</p>
      <div class="pills">
        <span class="pill">♧ PDF Analysis</span><span class="pill">⌕ Intelligent Search</span>
        <span class="pill">▣ Cited Answers</span><span class="pill">✧ Key Insights</span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# ---- Layout: upload | examples | overview -----------------------------------
left, mid, right = st.columns([1.05, 1.1, 1], gap="medium")

with left:
    with st.container(border=True):
        st.markdown('<div class="panel-title">🔹 1. Upload a Research Paper</div>', unsafe_allow_html=True)
        up = st.file_uploader(
            "Upload a PDF", type=["pdf"], label_visibility="collapsed", key="paper_upload"
        )
        if up is not None:
            data = up.getvalue()
            cur = st.session_state.paper
            if not cur or cur["name"] != up.name or hashlib.md5(cur["bytes"]).digest() != hashlib.md5(data).digest():
                st.session_state.paper = {"name": up.name, "bytes": data}
                st.session_state.pop("last_result", None)
        st.markdown(
            '<div class="muted">PDF · up to 200 MB · text-based PDFs work best</div>',
            unsafe_allow_html=True,
        )

paper = st.session_state.paper
prepared, prep_error = None, None
if paper:
    try:
        with st.spinner("Reading and indexing your paper…"):
            prepared = prepare_paper(paper["bytes"], paper["name"])
    except Exception as exc:
        prep_error = str(exc)

with mid:
    with st.container(border=True):
        st.markdown('<div class="panel-title">💡 2. Try Example Questions</div>', unsafe_allow_html=True)
        examples = [
            "What are the main contributions of this paper?",
            "Explain the proposed method in simple terms.",
            "What datasets and evaluation metrics are used?",
            "What are the key experimental results?",
            "How does this method compare to previous work?",
        ]
        for i, q in enumerate(examples):
            st.button("›  " + q, key=f"example_{i}", use_container_width=True, on_click=set_question, args=(q,))

with right:
    with st.container(border=True):
        st.markdown('<div class="panel-title">📄 Paper Overview</div>', unsafe_allow_html=True)
        if paper:
            size_mb = len(paper["bytes"]) / (1024 * 1024)
            badge = "Ready" if prepared else "Error"
            st.markdown(
                f'<div class="paper-file"><div class="pdf-icon">PDF</div>'
                f'<div style="min-width:0;flex:1;overflow-wrap:anywhere"><b>{html.escape(paper["name"][:60])}</b><br>'
                f'<span class="muted">{size_mb:.2f} MB</span></div><span class="status">{badge}</span></div>',
                unsafe_allow_html=True,
            )
            if prep_error:
                st.error(prep_error)
        else:
            st.markdown(
                '<div class="paper-file"><div class="pdf-icon">PDF</div><div><b>No paper uploaded yet</b><br>'
                '<span class="muted">Your document details will appear here.</span></div></div>',
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        a, b, c = st.columns(3)
        pages_v = str(prepared["n_pages"]) if prepared else "—"
        chunks_v = str(prepared["n_chunks"]) if prepared else "—"
        a.markdown(f'<div class="stat"><strong>{pages_v}</strong><span>Pages</span></div>', unsafe_allow_html=True)
        b.markdown(f'<div class="stat"><strong>{chunks_v}</strong><span>Passages</span></div>', unsafe_allow_html=True)
        c.markdown('<div class="stat"><strong>Hybrid</strong><span>Search</span></div>', unsafe_allow_html=True)

# ---- Ask --------------------------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="panel-title">💬 3. Ask a Question</div>', unsafe_allow_html=True)
    question = st.text_input(
        "Ask a question about your paper",
        key="question",
        placeholder="e.g. What is the main contribution of this paper?",
        label_visibility="collapsed",
    )
    ask = st.button("✦  Ask Copilot", type="primary", use_container_width=True)
    st.markdown(
        "<div class='muted'>Answers are generated from retrieved passages in your uploaded paper.</div>",
        unsafe_allow_html=True,
    )

if ask:
    if not paper:
        st.warning("Upload a research paper PDF first.")
    elif prep_error or not prepared:
        st.error("This paper could not be processed. Please upload a text-based PDF.")
    elif not question.strip():
        st.warning("Enter a question first, or choose one of the example questions.")
    else:
        api_key = get_secret("GROQ_API_KEY")
        model_name = get_secret("GROQ_MODEL_NAME", "openai/gpt-oss-20b")
        if not api_key:
            st.error("Groq API key is not configured. Add GROQ_API_KEY in Streamlit app Settings → Secrets.")
        else:
            try:
                with st.spinner("Searching the paper for evidence and writing an answer…"):
                    client = rag_engine.get_groq_client(api_key)
                    sources = rag_engine.hybrid_search(
                        question,
                        prepared["chunks"],
                        prepared["vector_index"],
                        prepared["bm25_index"],
                        top_k=5,
                    )
                    result = rag_engine.generate_answer(question, sources, client, model_name)
                st.session_state["last_result"] = result
                st.session_state["last_question"] = question
                st.session_state["last_paper_name"] = paper["name"]
            except Exception as exc:
                st.error(f"Unable to answer the question: {exc}")

# ---- Answer + evidence ------------------------------------------------------
last_result = st.session_state.get("last_result")
if last_result:
    st.markdown("## ✨ Copilot Answer")
    st.caption(
        f"Question: {st.session_state.get('last_question', '')} · "
        f"Paper: {st.session_state.get('last_paper_name', '')}"
    )
    with st.container(border=True):
        st.markdown(safe_md(last_result.get("answer", "No answer was generated.")))

    st.markdown("## 🧾 Source Evidence")
    if not last_result.get("sources"):
        st.info("No relevant evidence was retrieved for this question.")
    else:
        for i, source in enumerate(last_result["sources"], start=1):
            score = source.get("score")
            score_text = f" · score {score:.4f}" if isinstance(score, (int, float)) else ""
            with st.expander(f"Source {i} · PDF page {source.get('page', '?')}{score_text}", expanded=(i == 1)):
                st.text(source.get("text", "No passage text available."))

    st.info("AI-generated answers may contain errors. Check important claims against the source passages above.")

st.markdown(
    "<div class='footer'>Research Paper Copilot · Built with Streamlit, FAISS, BM25 and Groq</div>",
    unsafe_allow_html=True,
)
