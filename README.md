# Research Paper Copilot

An AI-powered research assistant that lets you upload a research paper
in PDF format, ask questions about its contents, and receive answers
grounded in retrieved passages with PDF page citations.

**Built with:** Python · Streamlit · FAISS · BM25 · Sentence
Transformers · PyMuPDF · Groq

> **Note:** This is a learning and portfolio project. AI-generated
> answers and citations can be incorrect or incomplete. Verify important
> claims against the original paper.

## Table of Contents

-   [Overview](#overview)
-   [Features](#features)
-   [How It Works](#how-it-works)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Getting Started](#getting-started)
-   [Configure Groq](#configure-groq)
-   [Run the Application](#run-the-application)
-   [Using the App](#using-the-app)
-   [Deployment on Streamlit Community
    Cloud](#deployment-on-streamlit-community-cloud)
-   [Configuration](#configuration)
-   [Evaluation and Testing](#evaluation-and-testing)
-   [Known Limitations](#known-limitations)
-   [Future Improvements](#future-improvements)
-   [Troubleshooting](#troubleshooting)
-   [Security and Privacy](#security-and-privacy)
-   [Contributing](#contributing)
-   [License](#license)
-   [Acknowledgements](#acknowledgements)

## Overview

Research papers can be lengthy and technically demanding. Finding a
specific result, understanding a method, or checking how two approaches
compare may require reading several sections.

Research Paper Copilot provides a question-answering interface over an
uploaded PDF. It extracts text, divides it into passages, retrieves
passages relevant to a question, and sends those passages to a language
model to generate an answer.

The app combines semantic search and keyword search so that retrieval
can use both meaning and exact terms. It also displays retrieved source
passages so users can check the generated response against the document.

## Features

-   **PDF upload:** Upload a research paper as a PDF.
-   **Text extraction:** Extract selectable text from the PDF using
    PyMuPDF.
-   **Passage chunking:** Split extracted text into overlapping chunks
    while retaining page metadata.
-   **Semantic retrieval:** Use Sentence Transformers embeddings and a
    FAISS vector index.
-   **Keyword retrieval:** Use BM25 to retrieve passages that match
    important terms.
-   **Hybrid ranking:** Combine semantic and keyword rankings with
    Reciprocal Rank Fusion (RRF).
-   **LLM answers:** Use the Groq API to generate answers based on
    retrieved passages.
-   **Evidence and citations:** Display retrieved passages and PDF page
    references to support manual verification.
-   **Reference filtering:** Identify bibliography sections and exclude
    reference chunks from hybrid retrieval.
-   **Responsive interface:** A Streamlit interface designed for desktop
    and mobile screens.
-   **Session-based paper workspace:** Work with an uploaded paper
    during the current app session.

## How It Works

The application follows a Retrieval-Augmented Generation (RAG) workflow.

``` text
Upload PDF
    |
    v
Extract text and page numbers (PyMuPDF)
    |
    v
Split text into overlapping chunks
    |
    +-------------------------------+
    |                               |
    v                               v
Create embeddings                Tokenize text
(Sentence Transformers)          (BM25)
    |                               |
    v                               v
FAISS vector index               BM25 index
    |                               |
    +---------------+---------------+
                    |
                    v
          User asks a question
                    |
                    v
       Semantic search + keyword search
                    |
                    v
      Reciprocal Rank Fusion (RRF)
                    |
                    v
       Retrieve relevant text passages
                    |
                    v
         Build evidence context
                    |
                    v
             Groq language model
                    |
                    v
       Answer + source passages/pages
```

### Retrieval details

1.  **PDF extraction:** Text is extracted page by page. Page numbers are
    retained as metadata.
2.  **Chunking:** Text is split into chunks with overlap so information
    near chunk boundaries is less likely to be lost.
3.  **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` converts
    passages and questions into vector representations.
4.  **FAISS search:** Normalized embeddings are indexed with
    `IndexFlatIP`, which supports inner-product similarity search over
    normalized vectors.
5.  **BM25 search:** The BM25 index provides a separate keyword-based
    ranking.
6.  **Reciprocal Rank Fusion:** The two rankings are combined into one
    candidate ranking.
7.  **Answer generation:** Retrieved passages are provided to Groq with
    instructions to answer from the supplied evidence and cite source
    IDs.
8.  **Evidence display:** The app displays the answer and retrieved
    passages with their PDF page numbers.

## Technology Stack

  Technology               Purpose
  ------------------------ ----------------------------------------
  Python                   Application and retrieval logic
  Streamlit                Web interface and session state
  PyMuPDF (`pymupdf`)      PDF text extraction
  Sentence Transformers    Text embeddings
  `all-MiniLM-L6-v2`       Default embedding model
  FAISS (`faiss-cpu`)      Vector indexing and semantic retrieval
  `rank-bm25`              Keyword-based retrieval
  Reciprocal Rank Fusion   Combines semantic and keyword rankings
  Groq Python SDK          Calls the hosted language model
  NumPy                    Numerical arrays and embedding vectors

## Project Structure

``` text
research-paper-copilot/
├── app.py                    # Streamlit UI, upload flow, session state, answer/evidence display
├── rag_engine.py             # PDF extraction, chunking, retrieval, citation handling, answer generation
├── requirements.txt          # Python dependencies
└── .streamlit/
    └── config.toml            # Streamlit theme and server configuration
```

Keep the configuration file at `.streamlit/config.toml` in the
repository.

## Getting Started

### Prerequisites

-   Python 3.10 or a compatible Python version supported by the
    installed dependencies.
-   A Groq account and API key.
-   Git, if cloning the repository.
-   Internet access for installing packages, downloading the embedding
    model on first use, and calling the Groq API.

### 1. Clone the repository

``` bash
git clone https://github.com/RaunakPriyadarshi/research-paper-copilot.git
cd research-paper-copilot
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the commands using Command
Prompt instead:

``` bat
.venv\Scripts\activate.bat
```

**macOS/Linux:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

FAISS and Sentence Transformers can require substantial dependencies and
memory. The embedding model is normally downloaded the first time it is
loaded.

## Configure Groq

The app reads the Groq API key from Streamlit Secrets first, with an
environment-variable fallback.

### Option A: Local development

Create `.streamlit/secrets.toml`:

``` toml
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL_NAME = "openai/gpt-oss-20b"
```

Replace the example key with your own key. **Do not commit
`secrets.toml` or any real API key to GitHub.**

Add the following to `.gitignore` if it is not already present:

``` gitignore
.streamlit/secrets.toml
.venv/
__pycache__/
*.py[cod]
.env
```

### Option B: Environment variables

You can set these environment variables instead:

**PowerShell:**

``` powershell
$env:GROQ_API_KEY="your_groq_api_key"
$env:GROQ_MODEL_NAME="openai/gpt-oss-20b"
```

**macOS/Linux:**

``` bash
export GROQ_API_KEY="your_groq_api_key"
export GROQ_MODEL_NAME="openai/gpt-oss-20b"
```

Use a Groq model that is available to your account. Model availability
and provider limits can change.

## Run the Application

From the project root, with your virtual environment active and the Groq
key configured:

``` bash
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`, which
you can open in your browser.

## Using the App

1.  Open the application.
2.  Upload a text-based research paper PDF.
3.  Wait for the paper to be extracted, chunked, and indexed.
4.  Enter a question about the paper, or select one of the example
    questions.
5.  Select **Ask Copilot**.
6.  Read the generated answer and check the source evidence and PDF page
    numbers.
7.  For important results, compare the answer with the original paper
    before using or sharing it.

### Example questions

-   What problem does this paper attempt to solve?
-   What are the main contributions?
-   Explain the proposed method in simple terms.
-   Which datasets and evaluation metrics are used?
-   What exact numerical results does the paper report?
-   How does the proposed method compare with the baselines?
-   What limitations do the authors acknowledge?
-   Does the paper provide the exact training cost?
-   What information cannot be determined from this paper?

For numerical or multi-part questions, ask focused questions and check
the retrieved evidence. A concise question can sometimes help retrieval
focus on the relevant section.

## Deployment on Streamlit Community Cloud

1.  Push `app.py`, `rag_engine.py`, `requirements.txt`, and
    `.streamlit/config.toml` to your GitHub repository.

2.  Open [Streamlit Community Cloud](https://share.streamlit.io/) and
    create or select an app.

3.  Select the repository, branch, and `app.py` as the main file.

4.  In the app's **Settings → Secrets**, add:

    ``` toml
    GROQ_API_KEY = "your_groq_api_key"
    GROQ_MODEL_NAME = "openai/gpt-oss-20b"
    ```

5.  Deploy the app and wait for dependency installation to finish.

6.  Test PDF upload, retrieval, answer generation, and source evidence
    on the live URL.

Do not put the API key in `app.py`, `rag_engine.py`, `requirements.txt`,
the README, or a public commit. Streamlit Cloud Secrets should be used
for deployment credentials.

## Configuration

### Streamlit theme

The `.streamlit/config.toml` file sets the app's light theme, primary
color, background colors, font, toolbar mode, and upload size limit.

The current configuration includes a maximum upload size of 200 MB.
Actual successful processing may still be constrained by the hosting
platform's memory, CPU, timeout, and request limits.

### Retrieval settings

The current retrieval defaults in `rag_engine.py` include:

-   `DEFAULT_TOP_K = 5`: number of passages returned for the final
    retrieval result.
-   `DEFAULT_CANDIDATE_K = 15`: candidate count used for each retrieval
    ranking.
-   `DEFAULT_RRF_K = 60`: reciprocal-rank-fusion constant.
-   Chunk size: 1,000 characters by default.
-   Chunk overlap: 200 characters by default.
-   Embedding model: `sentence-transformers/all-MiniLM-L6-v2`.

These are starting settings, not universally optimal values. Evaluate
changes against representative papers and questions before adopting
them.

## Evaluation and Testing

A RAG application should be evaluated on both answer quality and
evidence quality.

### Suggested test set

1.  **Basic understanding:** What is the paper's main contribution?
2.  **Method details:** How does the proposed method work?
3.  **Exact values:** What result is reported for a particular dataset
    and metric?
4.  **Comparison:** How do two methods compare, using the reported
    numbers?
5.  **Evidence across sections:** Find a conclusion that requires
    passages from multiple pages.
6.  **Missing information:** Does the paper report an exact monetary
    training cost?
7.  **Citation grounding:** Does each cited page support the claim next
    to the citation?
8.  **Answer completion:** Does the response finish its explanation and
    avoid ending mid-sentence?
9.  **Reference handling:** Does retrieval avoid returning bibliography
    text as if it were the main evidence?
10. **Unsupported claims:** Does the system acknowledge when the
    retrieved passages do not support an answer?

### Evaluation checklist

For each test, record:

-   Question
-   Expected answer or gold evidence
-   Retrieved passages and their page numbers
-   Factual correctness
-   Citation relevance
-   Numerical accuracy
-   Completeness
-   Whether the system appropriately acknowledges missing evidence

A citation that points to a real page is not necessarily proof that the
page supports the associated claim. Claim-level evidence checking is
important.

## Known Limitations

-   **Text-based PDFs work best.** Scanned documents may require OCR,
    which is not currently part of the described pipeline.
-   **Retrieval can miss evidence.** A relevant passage may not appear
    in the selected top results, especially for broad or multi-part
    questions.
-   **Generated answers can be wrong.** A language model can
    misinterpret or overstate retrieved evidence.
-   **Citations need verification.** Source IDs are mapped to retrieved
    passages and page numbers, but this does not guarantee that every
    claim is fully supported by its citation.
-   **Long answers may be truncated.** Output limits imposed by the
    selected model or API can result in incomplete responses.
-   **PDF extraction varies.** Complex layouts, multi-column papers,
    tables, equations, and scanned pages may extract imperfectly.
-   **Large PDFs can be resource-intensive.** Embedding and indexing
    require memory and processing time, particularly on limited hosting
    resources.
-   **One paper per active workspace.** The current UI manages the
    uploaded paper in the current session rather than providing a
    persistent, multi-user document library.
-   **External service dependency.** Answer generation requires network
    access and a working Groq API key. Rate limits and model
    availability can affect use.

## Future Improvements

Possible next steps include:

-   Build a repeatable evaluation dataset with expected answers and
    supporting pages.
-   Improve retrieval for questions that need evidence from multiple
    sections.
-   Add claim-level citation verification.
-   Detect incomplete model responses and provide a clear retry or
    continuation path.
-   Add reranking and compare its benefit against the current hybrid
    retrieval.
-   Improve extraction and handling of tables, equations, and scanned
    PDFs.
-   Add document-level controls for larger papers and limited-memory
    environments.
-   Add automated tests for citation conversion, reference filtering,
    and retrieval behavior.
-   Add persistent paper collections only if required, with clear
    privacy and storage controls.

These are potential improvements, not features that should be assumed to
exist in the current version.

## Troubleshooting

### The app says the Groq API key is missing

-   Confirm `GROQ_API_KEY` is set in `.streamlit/secrets.toml`,
    Streamlit Cloud Secrets, or the environment.
-   Restart the local Streamlit process after changing environment
    variables.
-   Check that the secret name is exactly `GROQ_API_KEY`.

### The selected model is unavailable

-   Confirm `GROQ_MODEL_NAME` refers to a model available to your Groq
    account.
-   Check the provider's current model and API documentation.
-   Update the model setting without exposing your API key.

### A PDF uploads but cannot be processed

-   Try a PDF with selectable text.
-   If the PDF is scanned, OCR may be required before the current
    pipeline can use its text.
-   Try a smaller PDF if the host runs out of memory or processing time.

### Answers are incomplete or miss important details

-   Ask one specific question at a time.
-   Inspect the retrieved source passages before changing generation
    settings.
-   If the evidence is missing, investigate retrieval settings and the
    paper's text extraction.
-   If evidence is present but the answer omits it, investigate the
    generation prompt and response-length handling.

### The app works locally but not after deployment

-   Check the Streamlit Cloud logs.
-   Confirm all dependencies are listed in `requirements.txt`.
-   Verify that `.streamlit/config.toml` is in the expected path.
-   Confirm the API key is configured in Streamlit Cloud Secrets.
-   Consider memory and startup-time limits when loading Sentence
    Transformers and FAISS.

## Security and Privacy

-   Keep API keys in local secrets or the hosting platform's secrets
    manager.
-   Never commit credentials, tokens, or private configuration files.
-   Upload only documents you are permitted to process.
-   Review the privacy and data-handling policies of your hosting
    platform and the external LLM provider before uploading confidential
    or unpublished research.
-   Treat model output as assistance, not a substitute for checking the
    source document.

## Contributing

Suggestions, bug reports, and improvements are welcome.

1.  Fork the repository.
2.  Create a branch for your change.
3.  Make a focused change and test it against representative questions
    and papers.
4.  Open a pull request describing the change and how it was tested.

Please avoid including API keys, private PDFs, or other sensitive data
in issues, logs, or pull requests.

## License

No license is specified in this README. Before inviting reuse or
contributions, choose a license that matches how you want others to use
the project and add a `LICENSE` file to the repository. Until then, do
not assume that the code is licensed for unrestricted reuse.

## Acknowledgements

This project builds on open-source tools and models, including:

-   [Streamlit](https://streamlit.io/)
-   [FAISS](https://github.com/facebookresearch/faiss)
-   [Sentence Transformers](https://www.sbert.net/)
-   [PyMuPDF](https://pymupdf.readthedocs.io/)
-   [rank-bm25](https://github.com/dorianbrown/rank_bm25)
-   [Groq](https://groq.com/)

------------------------------------------------------------------------

**Built as a hands-on project to explore Retrieval-Augmented Generation,
hybrid information retrieval, and evidence-grounded question
answering.**
