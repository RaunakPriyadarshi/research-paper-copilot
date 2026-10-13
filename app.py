import os
import tempfile
import html
import streamlit as st
import rag_engine

# ------------------------------------------------------------
# Research Paper Copilot — redesigned UI
# Compatible with the existing rag_engine.py module.
# ------------------------------------------------------------

st.set_page_config(
    page_title="Research Paper Copilot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Visual system ----------------------------------------------------------
st.markdown(
    r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  --ink: #101a45;
  --muted: #68769a;
  --blue: #2463eb;
  --violet: #7651f5;
  --line: #dfe7fa;
  --panel: rgba(255,255,255,.92);
}
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp {
  background:
    radial-gradient(ellipse at 78% 5%, rgba(176, 162, 255, .28), transparent 36%),
    radial-gradient(ellipse at 28% 65%, rgba(122, 177, 255, .20), transparent 35%),
    linear-gradient(135deg, #edf4ff 0%, #f4f1ff 52%, #edf6ff 100%);
  color: var(--ink);
}
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1600px; padding-top: 1.2rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] {
  background: linear-gradient(165deg, #101b3b 0%, #111d45 56%, #271b68 100%);
  border-right: 1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] * { color: #e9efff; }
[data-testid="stSidebar"] .stButton button {
  text-align: left; border: 1px solid rgba(255,255,255,.08);
  background: rgba(255,255,255,.045); color: #e8efff;
  border-radius: 12px; padding: .65rem .8rem;
}
[data-testid="stSidebar"] .stButton button:hover {
  background: linear-gradient(100deg,#1766f4,#5e37ca); border-color: transparent;
}
.brand { text-align:center; padding: 12px 8px 26px; }
.brand-icon { font-size: 2.4rem; filter: drop-shadow(0 6px 12px #6155f5); }
.brand-title { font: 800 1.25rem 'Manrope', sans-serif; line-height:1.2; margin-top:8px; }
.brand-sub { color:#9db5e6; font-size:.83rem; line-height:1.5; margin-top:9px; }
.sidebar-note {
  margin-top: 30px; border:1px solid rgba(166,192,255,.25);
  background:rgba(255,255,255,.045); border-radius:16px; padding:16px;
  color:#b8d4ff; line-height:1.65; font-size:.86rem;
}
.hero {
  position: relative; overflow:hidden; min-height: 205px; border-radius:20px;
  padding: 28px 34px; margin-bottom: 14px;
  color:white; background:
   radial-gradient(circle at 80% 20%, rgba(133,84,255,.55), transparent 23%),
   radial-gradient(circle at 67% 105%, rgba(52,120,255,.55), transparent 30%),
   linear-gradient(110deg,#101b45 0%,#101e50 52%,#21175d 100%);
  box-shadow: 0 16px 38px rgba(51,76,166,.16);
}
.hero:after {
  content:"✦   ·      ✧       ·   ✦       ·      ✧";
  position:absolute; right:25px; top:24px; width:39%; height:100%;
  color:rgba(215,224,255,.48); font-size:22px; letter-spacing:16px;
  line-height:2.5; pointer-events:none;
}
.hero h1 { font:800 clamp(1.8rem,3vw,2.7rem) 'Manrope',sans-serif; margin:0 0 7px; letter-spacing:-1.3px; }
.hero h1 span { color:#d8a8ff; }
.hero p { font-size:1.02rem; line-height:1.55; color:#e2eaff; margin:0; max-width:650px; }
.pills { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
.pill { display:inline-block; border:1px solid rgba(125,176,255,.55); color:#e5edff;
  border-radius:999px; padding:6px 12px; font-size:.78rem; background:rgba(7,25,70,.45); }
.panel {
  background:var(--panel); border:1px solid rgba(211,222,247,.95);
  border-radius:18px; padding:17px; box-shadow:0 8px 24px rgba(55,78,145,.055);
  margin-bottom:14px;
}
.panel-title { font:700 1rem 'Manrope',sans-serif; color:#101b46; margin:0 0 13px; }
.kicker { color:#7887aa; text-transform:uppercase; font-size:.68rem; font-weight:700; letter-spacing:1.3px; }
.muted { color:var(--muted); font-size:.85rem; }
.paper-file {
  background:linear-gradient(110deg,#f7faff,#edf4ff); border:1px solid #dce7fb;
  border-radius:13px; padding:12px; display:flex; gap:12px; align-items:center;
}
.pdf-icon { background:#ffebe9; color:#e94343; border-radius:9px; padding:10px; font-weight:800; }
.status { display:inline-block; border-radius:99px; background:#d9f9eb; color:#087a55; padding:4px 10px; font-size:.72rem; }
.stat { text-align:center; background:linear-gradient(145deg,#eef6ff,#e9f0ff); border:1px solid #e0e9fb; border-radius:10px; padding:10px 4px; }
.stat strong { display:block; font-size:1.05rem; color:#172656; }
.stat span { color:#7281a4; font-size:.72rem; }
.answer-box { background:#fff; border:1px solid #e2e8fb; border-radius:14px; padding:18px; box-shadow:0 5px 16px rgba(47,68,130,.04); }
.answer-label { font-weight:800; color:#101b46; margin-bottom:12px; }
.source-card { border:1px solid #e1e9f8; border-radius:12px; padding:12px; background:#fbfdff; margin-bottom:9px; }
.source-page { font-weight:800; color:#16234f; font-size:.85rem; }
.score { display:inline-block; color:#1758d1; background:#e5f0ff; border-radius:99px; padding:3px 8px; font-size:.7rem; }
div.stButton > button[kind="primary"] {
  background:linear-gradient(110deg,#2168f5,#8150ef); color:white; border:0;
  border-radius:11px; font-weight:700; box-shadow:0 6px 15px rgba(85,81,225,.18);
}
div.stButton > button[kind="primary"]:hover { background:linear-gradient(110deg,#1554db,#6a3bd8); color:white; }
.stTextInput input, .stTextArea textarea { border-radius:12px !important; border-color:#d8e2fb !important; background:#fff !important; }
[data-testid="stFileUploader"] { background:#f8fbff; border:1px dashed #9cbcff; border-radius:13px; padding:10px; }
div[data-testid="stExpander"] { background:#fbfdff; border:1px solid #e0e9fa; border-radius:12px; }
hr { border-color:#e2e9f8; }
@media (max-width: 900px) {
 .hero { padding:23px; } .hero:after { display:none; }
 .block-container { padding-left:1rem; padding-right:1rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

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
    if "active_nav" not in st.session_state:
        st.session_state.active_nav = "Home"
    for label, icon in [("Home", "⌂"), ("Chat", "☷"), ("My Papers", "▤"), ("Insights", "⌁"), ("Settings", "⚙")]:
        if st.button(f"{icon}   {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.active_nav = label
    st.markdown(
        """
        <div class="sidebar-note">
          <div style="font-size:1.5rem">💡</div>
          <b>Turn research papers into understanding.</b><br><br>
          Ask questions, get answers with citations, and explore key insights — all in one place.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:18px'></div><div class='muted'>Powered by RAG · FAISS · BM25 · Groq</div>", unsafe_allow_html=True)

# ---- Hero -------------------------------------------------------------------
st.markdown(
    """
    <section class="hero">
      <div class="kicker" style="color:#9fb8ff;margin-bottom:8px">YOUR PERSONAL RESEARCH WORKSPACE</div>
      <h1>Your AI <span>Research Partner</span></h1>
      <p>Upload a research paper, ask questions, and get accurate,<br>
      evidence-backed answers from the document.</p>
      <div class="pills">
        <span class="pill">♧ PDF Analysis</span><span class="pill">⌕ Intelligent Search</span>
        <span class="pill">▣ Cited Answers</span><span class="pill">✧ Key Insights</span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# ---- Layout -----------------------------------------------------------------
left, mid, right = st.columns([1.08, 1.08, 1], gap="medium")
with left:
    st.markdown('<div class="panel"><div class="panel-title">🔹 &nbsp; 1. Upload a Research Paper</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Drop your PDF here or browse", type=["pdf"], label_visibility="collapsed", key="paper_upload")
    st.markdown('<div class="muted">PDF format · Up to 200 MB · Text-based PDFs work best</div></div>', unsafe_allow_html=True)

with mid:
    st.markdown('<div class="panel"><div class="panel-title">💡 &nbsp; 2. Try Example Questions</div>', unsafe_allow_html=True)
    examples = [
        "What are the main contributions of this paper?",
        "Explain the proposed method in simple terms.",
        "What datasets and evaluation metrics are used?",
        "What are the key experimental results?",
        "How does this method compare to previous work?",
    ]
    for i, q in enumerate(examples):
        if st.button("›  " + q, key=f"example_{i}", use_container_width=True):
            st.session_state.question = q
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel"><div class="panel-title">📄 &nbsp; Paper Overview</div>', unsafe_allow_html=True)
    if uploaded:
        size_mb = len(uploaded.getvalue()) / (1024 * 1024)
        st.markdown(
            f'<div class="paper-file"><div class="pdf-icon">PDF</div><div style="min-width:0;flex:1"><b>{html.escape(uploaded.name[:34])}</b><br><span class="muted">{size_mb:.2f} MB · Uploaded</span></div><span class="status">Ready</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="muted">Your paper is ready to analyze. Ask a question to retrieve relevant passages.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="paper-file"><div class="pdf-icon">PDF</div><div><b>No paper uploaded yet</b><br><span class="muted">Your document details will appear here.</span></div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a: st.markdown('<div class="stat"><strong>PDF</strong><span>Input</span></div>', unsafe_allow_html=True)
    with b: st.markdown('<div class="stat"><strong>RAG</strong><span>Retrieval</span></div>', unsafe_allow_html=True)
    with c: st.markdown('<div class="stat"><strong>AI</strong><span>Answers</span></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---- Question / Answer ------------------------------------------------------
st.markdown('<div class="panel"><div class="panel-title">💬 &nbsp; 3. Ask a Question</div>', unsafe_allow_html=True)
if "question" not in st.session_state:
    st.session_state.question = ""
question = st.text_input(
    "Ask a question about your paper",
    key="question",
    placeholder="e.g. What is the main contribution of this paper?",
    label_visibility="collapsed",
)
go_col, hint_col = st.columns([1, 5])
with go_col:
    ask = st.button("✦  Ask Copilot", type="primary", use_container_width=True)
with hint_col:
    st.markdown("<div class='muted' style='padding:10px 4px'>Answers are generated from retrieved passages in your uploaded paper.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if ask:
    if not uploaded:
        st.warning("Upload a research paper PDF first.")
    elif not question.strip():
        st.warning("Enter a question first, or choose one of the example questions.")
    else:
        api_key = ""
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = os.getenv("GROQ_API_KEY", "")
        model_name = os.getenv("GROQ_MODEL_NAME", "openai/gpt-oss-20b")
        try:
            try:
                model_name = st.secrets.get("GROQ_MODEL_NAME", model_name)
            except Exception:
                pass
            if not api_key:
                st.error("Groq API key is not configured. Add GROQ_API_KEY in Streamlit app Settings → Secrets.")
                st.stop()

            with st.spinner("Reading your paper, building indexes, and searching for evidence…"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(uploaded.getvalue())
                    pdf_path = temp_file.name
                try:
                    pages = rag_engine.extract_pdf_pages(pdf_path)
                    chunks = rag_engine.create_document_chunks(pages)
                    if not chunks:
                        st.error("No extractable text was found in this PDF. If it is scanned, OCR may be needed.")
                        st.stop()
                    vector_index, _ = rag_engine.build_vector_index(chunks)
                    bm25_index = rag_engine.build_bm25_index(chunks)
                    client = rag_engine.get_groq_client(api_key)
                    sources = rag_engine.hybrid_search(
                        question, chunks, vector_index, bm25_index, top_k=5
                    )
                    result = rag_engine.generate_answer(
                        question, sources, client, model_name
                    )
                finally:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

            st.markdown('<div class="panel"><div class="panel-title">✨ &nbsp; Copilot Answer</div>', unsafe_allow_html=True)
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown(result["answer"])
            st.markdown("</div></div>", unsafe_allow_html=True)

            st.markdown('<div class="panel"><div class="panel-title">🧾 &nbsp; Source Evidence</div>', unsafe_allow_html=True)
            if not result["sources"]:
                st.info("No relevant evidence was retrieved for this question.")
            else:
                for i, source in enumerate(result["sources"], start=1):
                    score = source.get("score")
                    score_text = f" · RRF score {score:.4f}" if isinstance(score, (int, float)) else ""
                    with st.expander(f"Source {i}  ·  PDF page {source['page']}{score_text}", expanded=(i == 1)):
                        st.write(source["text"])
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception as exc:
            st.error(f"Unable to process the paper: {exc}")

st.markdown(
    "<div style='text-align:center;color:#8794b5;font-size:.78rem;padding:18px'>Research Paper Copilot · Built with Streamlit, FAISS, BM25 and Groq</div>",
    unsafe_allow_html=True,
)
