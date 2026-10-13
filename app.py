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
.hero h1, .hero h1 *, .hero p, .hero .pill { color:#ffffff !important; }
.hero .kicker { color:#b9ccff !important; }
.hero:after {
  content:"✦   ·      ✧       ·   ✦       ·      ✧";
  position:absolute; right:25px; top:24px; width:39%; height:100%;
  color:rgba(215,224,255,.48); font-size:22px; letter-spacing:16px;
  line-height:2.5; pointer-events:none;
}
.hero h1 { color:#ffffff !important; font:800 clamp(1.8rem,3vw,2.7rem) 'Manrope',sans-serif; margin:0 0 7px; letter-spacing:-1.3px; text-shadow:0 1px 2px rgba(0,0,0,.18); }
.hero h1 span { color:#e6c8ff !important; }
.hero p { color:#f1f5ff !important; font-size:1.02rem; line-height:1.55; margin:0; max-width:650px; }
.pills { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
.pill { display:inline-block; border:1px solid rgba(180,205,255,.75); color:#ffffff !important;
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
/* ---- Readability / contrast fixes ------------------------------------- */
/* Keep the main workspace light with consistently dark readable text. */
.stApp, .stApp p, .stApp li, .stApp label,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stMarkdownContainer"] span {
  color: #172344;
}
/* Inputs: dark typed text, light field, and visible placeholder. */
.stApp input, .stApp textarea,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea {
  background-color: #ffffff !important;
  color: #172344 !important;
  -webkit-text-fill-color: #172344 !important;
  caret-color: #172344 !important;
  border-color: #b9c9e8 !important;
}
.stApp input::placeholder, .stApp textarea::placeholder,
.stApp [data-baseweb="input"] input::placeholder,
.stApp [data-baseweb="textarea"] textarea::placeholder {
  color: #667493 !important;
  -webkit-text-fill-color: #667493 !important;
  opacity: 1 !important;
}
/* Buttons and example-question controls. */
.stApp div.stButton > button,
.stApp [data-testid="stFileUploader"] button {
  color: #172344;
}
.stApp div.stButton > button p { color: inherit !important; }
/* Uploader area and instructions. */
.stApp [data-testid="stFileUploader"],
.stApp [data-testid="stFileUploader"] section,
.stApp [data-testid="stFileUploader"] small,
.stApp [data-testid="stFileUploader"] span {
  color: #172344 !important;
}
/* Expanders/source evidence: readable whether opened or closed. */
.stApp [data-testid="stExpander"],
.stApp [data-testid="stExpander"] details,
.stApp [data-testid="stExpander"] summary,
.stApp [data-testid="stExpander"] summary p,
.stApp [data-testid="stExpander"] [data-testid="stMarkdownContainer"],
.stApp [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
  color: #172344 !important;
}
.stApp [data-testid="stExpander"] details,
.stApp [data-testid="stExpander"] summary {
  background-color: #fbfdff !important;
}
/* Alerts and status text. */
.stApp [data-testid="stAlert"] p { color: #172344 !important; }
/* The sidebar intentionally stays dark, so force light text there. */
[data-testid="stSidebar"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] .muted {
  color: #e9efff !important;
}
[data-testid="stSidebar"] .brand-sub { color: #b9c9ee !important; }
[data-testid="stSidebar"] .sidebar-note { color: #d8e5ff !important; }
[data-testid="stSidebar"] div.stButton > button,
[data-testid="stSidebar"] div.stButton > button p {
  color: #f0f4ff !important;
}
/* Mobile contrast safeguards: some mobile browsers/Streamlit themes apply
   different foreground colors to nested widget elements. */
.stApp .hero,
.stApp .hero * { color: #ffffff !important; }
.stApp .hero .kicker { color: #dbe6ff !important; }
.stApp .hero h1 span { color: #f0d7ff !important; }
.stApp .panel, .stApp .panel *,
.stApp .answer-box, .stApp .answer-box *,
.stApp .source-card, .stApp .source-card *,
.stApp .paper-file, .stApp .paper-file *,
.stApp .stat, .stApp .stat * { -webkit-text-fill-color: currentColor; }
.stApp .panel, .stApp .answer-box, .stApp .source-card,
.stApp .paper-file, .stApp .stat { color: #172344 !important; }
.stApp [data-testid="stTextInput"] label,
.stApp [data-testid="stTextArea"] label,
.stApp [data-testid="stFileUploader"] label,
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li { color: #172344 !important; }
.stApp [data-testid="stTextInput"] input,
.stApp [data-testid="stTextArea"] textarea,
.stApp [data-baseweb="input"] input,
.stApp [data-baseweb="textarea"] textarea {
  background: #ffffff !important;
  color: #172344 !important;
  -webkit-text-fill-color: #172344 !important;
  opacity: 1 !important;
}
.stApp div.stButton > button,
.stApp div.stButton > button * {
  -webkit-text-fill-color: inherit !important;
}
.stApp [data-testid="stExpander"] summary,
.stApp [data-testid="stExpander"] summary * {
  color: #172344 !important;
  -webkit-text-fill-color: #172344 !important;
}
@media (max-width: 900px) {
 .hero { padding:23px; }
 .hero:after { display:none; }
 .hero h1 { font-size:1.75rem !important; line-height:1.25 !important; }
 .hero p { font-size:1rem !important; }
 .block-container { padding-left:1rem; padding-right:1rem; }
 /* Keep contrast independent of the phone's light/dark browser preference. */
 .stApp, .stApp [data-testid="stMain"] { color: #172344 !important; }
 .stApp .panel-title, .stApp .muted, .stApp .kicker { color: #435274 !important; }
 [data-testid="stSidebar"] *,
 [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
   color: #f0f4ff !important;
   -webkit-text-fill-color: #f0f4ff !important;
 }
 [data-testid="stSidebar"] .brand-sub { color: #c8d8ff !important; -webkit-text-fill-color:#c8d8ff !important; }
}
</style>
""",
    unsafe_allow_html=True,
)

# Preserve the uploaded file outside the file_uploader widget state.
# Streamlit removes widget state when that widget is not rendered on another page.
if st.session_state.get("paper_upload") is not None:
    st.session_state["saved_paper_upload"] = st.session_state["paper_upload"]

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

# ---- Real page routing -------------------------------------------------------
# The sidebar buttons update active_nav. This block makes that state control
# the visible page. The Home/Chat workspace below retains the original RAG flow.
active_nav = st.session_state.get("active_nav", "Home")

if active_nav == "My Papers":
    st.markdown("# 📚 My Papers")
    st.markdown("Manage the research paper in your current session.")
    current_upload = st.session_state.get("saved_paper_upload") or st.session_state.get("paper_upload")
    if current_upload is not None:
        size_mb = len(current_upload.getvalue()) / (1024 * 1024)
        st.markdown(
            f"<div class='panel'><div class='paper-file'><div class='pdf-icon'>PDF</div>"
            f"<div style='min-width:0;flex:1'><b>{html.escape(current_upload.name)}</b><br>"
            f"<span class='muted'>{size_mb:.2f} MB · Available in this session</span></div>"
            f"<span class='status'>Uploaded</span></div></div>",
            unsafe_allow_html=True,
        )
        if st.button("Open paper workspace", type="primary"):
            st.session_state.active_nav = "Home"
            st.rerun()
    else:
        st.info("No paper is uploaded in this session yet.")
        if st.button("Go to Home to upload a PDF", type="primary"):
            st.session_state.active_nav = "Home"
            st.rerun()
    st.stop()

if active_nav == "Insights":
    st.markdown("# ✨ Research Insights")
    st.markdown("Use the paper workspace to ask evidence-based questions about the document.")
    st.markdown(
        """
        <div class="panel">
          <div class="panel-title">What you can explore</div>
          <ul>
            <li><b>Research contributions</b> — identify the problem and what the authors add.</li>
            <li><b>Methods</b> — understand the proposed approach and model design.</li>
            <li><b>Experiments</b> — find datasets, evaluation metrics, and reported results.</li>
            <li><b>Limitations</b> — ask what the paper states about weaknesses or future work.</li>
          </ul>
          <p class="muted">Answers are grounded in retrieved PDF passages and include source-page evidence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Start exploring this paper", type="primary"):
        st.session_state.active_nav = "Home"
        st.rerun()
    st.stop()

if active_nav == "Settings":
    st.markdown("# ⚙️ Settings")
    st.markdown("Current application configuration and pipeline details.")
    st.markdown(
        """
        <div class="panel">
          <div class="panel-title">RAG pipeline</div>
          <p><b>PDF extraction:</b> PyMuPDF</p>
          <p><b>Semantic retrieval:</b> Sentence Transformers + FAISS</p>
          <p><b>Keyword retrieval:</b> BM25</p>
          <p><b>Ranking:</b> Reciprocal Rank Fusion (hybrid search)</p>
          <p><b>Answer generation:</b> Groq</p>
          <p class="muted">Credentials are managed privately through Streamlit Secrets. They are not displayed here.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Return to workspace", type="primary"):
        st.session_state.active_nav = "Home"
        st.rerun()
    st.stop()

# ---- Hero -------------------------------------------------------------------
if st.session_state.get("active_nav", "Home") == "Chat":
    st.markdown("## 💬 Chat with your research paper")
    st.caption("Upload a PDF, choose an example, or type your own question below.")

st.markdown(
    """
    <section class="hero">
      <div class="kicker" style="color:#9fb8ff;margin-bottom:8px">YOUR PERSONAL RESEARCH WORKSPACE</div>
      <h1>Your AI <span>Research Partner</span></h1>
      <p>Upload a research paper, ask questions, and get accurate,<br>
      answers grounded in retrieved passages from your document.</p>
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
    uploaded_widget = st.file_uploader("Drop your PDF here or browse", type=["pdf"], label_visibility="collapsed", key="paper_upload")
    if uploaded_widget is not None:
        st.session_state["saved_paper_upload"] = uploaded_widget
    uploaded = uploaded_widget or st.session_state.get("saved_paper_upload")
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
                    # Keep the last result in this browser session so it remains
                    # visible after normal Streamlit reruns or sidebar navigation.
                    st.session_state["last_result"] = result
                    st.session_state["last_question"] = question
                    st.session_state["last_paper_name"] = uploaded.name
                finally:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
        except Exception as exc:
            st.error(f"Unable to process the paper: {exc}")

# Render the latest answer outside the button event.
# Use native Streamlit containers instead of opening an HTML <div> in one
# st.markdown call and closing it in another. Streamlit renders each call as
# a separate block, so split HTML wrappers can cause content styling/layout
# problems and, on some themes, make the answer appear missing.
last_result = st.session_state.get("last_result")
if last_result:
    last_question = st.session_state.get("last_question", "")
    last_paper_name = st.session_state.get("last_paper_name", "your uploaded paper")

    st.markdown("## ✨ Copilot Answer")
    st.caption(f"Question: {last_question} · Paper: {last_paper_name}")
    with st.container(border=True):
        # Explicitly render the generated Markdown as normal Streamlit content.
        st.markdown(
            last_result.get("answer", "No answer was generated."),
            unsafe_allow_html=False,
        )

    st.markdown("## 🧾 Source Evidence")
    if not last_result.get("sources"):
        st.info("No relevant evidence was retrieved for this question.")
    else:
        for i, source in enumerate(last_result["sources"], start=1):
            score = source.get("score")
            score_text = f" · RRF score {score:.4f}" if isinstance(score, (int, float)) else ""
            page = source.get("page", "?")
            with st.expander(
                f"Source {i} · PDF page {page}{score_text}",
                expanded=(i == 1),
            ):
                st.markdown(
                    source.get("text", "No passage text available."),
                    unsafe_allow_html=False,
                )

    st.info(
        "AI-generated answers may contain errors. Check important claims "
        "against the source passages above."
    )

st.markdown(
    "<div style='text-align:center;color:#8794b5;font-size:.78rem;padding:18px'>Research Paper Copilot · Built with Streamlit, FAISS, BM25 and Groq</div>",
    unsafe_allow_html=True,
)
