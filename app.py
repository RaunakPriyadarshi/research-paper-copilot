
import streamlit as st
import tempfile
import os

import rag_engine


st.set_page_config(
    page_title="Research Paper Copilot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Research Paper Copilot")
st.write(
    "Upload a research paper, ask questions, "
    "and explore evidence from the document."
)

# API key is configured through Streamlit secrets.
api_key = st.secrets.get("GROQ_API_KEY", "")

if not api_key:
    st.info(
        "Configure GROQ_API_KEY in Streamlit secrets "
        "before asking questions."
    )

uploaded_file = st.file_uploader(
    "Upload a research paper",
    type=["pdf"]
)

question = st.text_input(
    "Ask a question about your paper",
    placeholder="What are the main contributions?"
)

if uploaded_file and st.button("Get answer"):
    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    if not api_key:
        st.error("The Groq API key is not configured.")
        st.stop()

    with st.spinner("Reading and indexing your paper..."):
        # Save the uploaded PDF temporarily.
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            pdf_path = temp_file.name

        try:
            pages = rag_engine.extract_pdf_pages(pdf_path)
            chunks = rag_engine.create_document_chunks(pages)

            if not chunks:
                st.error("No extractable text was found in this PDF.")
                st.stop()

            vector_index, _ = rag_engine.build_vector_index(chunks)
            bm25_index = rag_engine.build_bm25_index(chunks)

            client = rag_engine.get_groq_client(api_key)

            sources = rag_engine.hybrid_search(
                question,
                chunks,
                vector_index,
                bm25_index,
                top_k=5
            )

            result = rag_engine.generate_answer(
                question,
                sources,
                client,
                st.secrets.get(
                    "GROQ_MODEL_NAME",
                    "openai/gpt-oss-20b"
                )
            )

            st.subheader("Answer")
            st.markdown(result["answer"])

            st.subheader("Retrieved evidence")
            for i, source in enumerate(result["sources"], start=1):
                with st.expander(
                    f"Source {i} — PDF page {source['page']}"
                ):
                    st.write(source["text"])
                    st.caption(
                        f"RRF score: {source['score']:.4f}"
                    )

        except Exception as exc:
            st.error(f"Unable to process the paper: {exc}")

        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
