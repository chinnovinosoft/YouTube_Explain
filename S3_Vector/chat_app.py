#!/usr/bin/env python3
import os
import logging
import streamlit as st
import boto3
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger("chat")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_VECTOR_BUCKET = os.getenv("S3_VECTOR_BUCKET") or "your-vector-bucket"
S3_VECTOR_INDEX = os.getenv("S3_VECTOR_INDEX") or "pdf-index-1536"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")  # 1536 dims
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
TOP_K = int(os.getenv("TOP_K", "6"))

s3vectors = boto3.client("s3vectors", region_name=AWS_REGION)
client = OpenAI(api_key=OPENAI_API_KEY)

def embed_query(q: str):
    r = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=[q])
    return [float(x) for x in r.data[0].embedding]

def retrieve(embedding):
    resp = s3vectors.query_vectors(
        vectorBucketName=S3_VECTOR_BUCKET,
        indexName=S3_VECTOR_INDEX,
        queryVector={"float32": embedding},
        topK=TOP_K,
        returnDistance=True,
        returnMetadata=True,
    )
    return resp.get("vectors", [])

def answer_with_context(question: str, context_blocks: list) -> str:
    context_text = "\n\n---\n\n".join(context_blocks) if context_blocks else "N/A"
    system_prompt = (
        "You are a helpful assistant. Use the provided context to answer the user's question concisely. "
        "If the answer is not in the context, say you don't know."
    )
    user_content = f"Question: {question}\n\nContext:\n{context_text}"
    resp = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

st.set_page_config(page_title="PDF QA Chat", layout="wide")

st.markdown(
    """
    <div style='position:fixed; top:0; left:0; right:0; padding:10px 20px;
                background:#f8f9fa; border-bottom:1px solid #ddd; z-index:1000;'>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

st.markdown("## 💬 PDF Knowledge Chat")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"user": "", "bot": "👋 Hi! Ask me anything about your indexed PDFs."}
    ]

chat_box = st.container()
with chat_box:
    for m in st.session_state.chat_history:
        if m["user"]:
            st.markdown(f"🧑‍💻 **You:** {m['user']}")
        st.markdown(f"🤖 **Bot:** {m['bot']}")

st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)

with st.form("chat_input", clear_on_submit=True):
    st.markdown(
        """
        <style>
        .input-container {
            position: fixed; bottom: 0; left: 0; right: 0; padding: 10px 20px;
            background-color: #fff; border-top: 1px solid #ccc; z-index: 999;
            display: flex; align-items: center; gap: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_q = st.text_input("Ask your question", label_visibility="collapsed")
    submitted = st.form_submit_button("➤")
    st.markdown("</div>", unsafe_allow_html=True)

if submitted and user_q:
    with st.spinner("Retrieving..."):
        emb = embed_query(user_q)
        hits = retrieve(emb)
        ctx_blocks = []
        for h in hits:
            md = h.get("metadata") or {}
            txt = md.get("text") or ""
            src = md.get("source") or ""
            dist = h.get("distance")
            ctx_blocks.append(f"[source: {src} | dist: {dist}]\n{txt}")
        ans = answer_with_context(user_q, ctx_blocks)
    st.session_state.chat_history.append({"user": user_q, "bot": ans})
    st.rerun()
