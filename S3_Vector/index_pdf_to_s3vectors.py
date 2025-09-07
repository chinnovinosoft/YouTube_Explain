#!/usr/bin/env python3
import os
import argparse
import logging
import re
from typing import List

import boto3
from botocore.exceptions import ClientError
from openai import OpenAI
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
log = logging.getLogger("indexer")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_VECTOR_BUCKET = os.getenv("S3_VECTOR_BUCKET") or "your-vector-bucket"
S3_VECTOR_INDEX = os.getenv("S3_VECTOR_INDEX") or "pdf-index-1536"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")  # 1536 dims
S3_VECTOR_DIM = int(os.getenv("S3_VECTOR_DIM", "1536"))  # must match your index

EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "64"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

s3vectors = boto3.client("s3vectors", region_name=AWS_REGION)
client = OpenAI(api_key=OPENAI_API_KEY)

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()

def read_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return normalize_whitespace("\n".join(parts))

def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    text = text if text else ""
    n = len(text)
    if n == 0:
        return []
    chunks, start = [], 0
    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        if end >= n:
            break
        start = max(0, end - overlap)
    return chunks

def embed_texts(texts: List[str]) -> List[List[float]]:
    out: List[List[float]] = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i:i + EMBED_BATCH_SIZE]
        resp = client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=batch)
        for d in resp.data:
            out.append([float(x) for x in d.embedding])
    return out

def ensure_index(bucket: str, index: str, dim: int) -> None:
    try:
        info = s3vectors.get_index(vectorBucketName=bucket, indexName=index)
        actual_dim = info.get("dimension")
        if actual_dim and int(actual_dim) != dim:
            raise RuntimeError(f"Index '{index}' exists with dimension {actual_dim}, expected {dim}.")
        log.info("Index found: %s (dimension=%s)", index, actual_dim)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "")
        if code in {"ResourceNotFoundException", "404", "NotFoundException"}:
            try:
                s3vectors.create_index(vectorBucketName=bucket, indexName=index, dimension=dim)
                log.info("Created index: %s (dimension=%d)", index, dim)
            except Exception as ce:
                log.warning("create_index not available or failed (%s). Assuming index already created.", ce)
        else:
            raise

def upsert_vectors(bucket: str, index: str, keys: List[str], embeddings: List[List[float]], chunks: List[str]) -> None:
    vectors = []
    for k, emb, txt in zip(keys, embeddings, chunks):
        vectors.append({
            "key": k,
            "data": {"float32": emb},
            "metadata": {"text": txt, "source": k.split("::chunk_")[0], "type": "pdf_chunk"},
        })
    s3vectors.put_vectors(vectorBucketName=bucket, indexName=index, vectors=vectors)
    log.info("Upserted %d vectors into %s/%s", len(vectors), bucket, index)

def index_pdf(pdf_path: str):
    base = os.path.basename(pdf_path)
    log.info("Reading PDF: %s", pdf_path)
    text = read_pdf_text(pdf_path)
    if not text:
        log.warning("No text extracted: %s", pdf_path)
        return
    chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
    log.info("Chunked into %d parts", len(chunks))
    embeds = embed_texts(chunks)
    if not embeds:
        log.warning("No embeddings produced for %s", pdf_path)
        return
    if len(embeds[0]) != S3_VECTOR_DIM:
        raise RuntimeError(f"Embedding dim {len(embeds[0])} != index dim {S3_VECTOR_DIM}.")
    keys = [f"{base}::chunk_{i}" for i in range(len(chunks))]
    upsert_vectors(S3_VECTOR_BUCKET, S3_VECTOR_INDEX, keys, embeds, chunks)

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument("pdfs", nargs="+", help="PDF file(s) to index")
    # args = parser.parse_args()
    if not OPENAI_API_KEY:
        raise RuntimeError("Set OPENAI_API_KEY")
    ensure_index(S3_VECTOR_BUCKET, S3_VECTOR_INDEX, S3_VECTOR_DIM)
    # for p in args.pdfs:
    p = "trump.pdf"
    index_pdf(p)

if __name__ == "__main__":
    main()
