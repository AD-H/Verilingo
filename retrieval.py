import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from document_processor import create_chunks


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Load trusted-source data
with open(
    "sources/trusted_sources.json",
    "r",
    encoding="utf-8"
) as file:
    evidence_data = json.load(file)


# Create chunks from every source
all_chunks = []

for item in evidence_data:

    chunks = create_chunks(
    item["text"],
    chunk_size=80,
    overlap=20
)

    for chunk in chunks:

        all_chunks.append({
            "id": item["id"],
            "source": item["source"],
            "category":item["category"],
            "topic": item["topic"],
            "text": chunk
        })


# Create embeddings for all chunks
evidence_texts = [
    item["text"]
    for item in all_chunks
]

evidence_embeddings = model.encode(
    evidence_texts
)


def retrieve_evidence(
    claim,
    top_k=3,
    threshold=0.30
):

    # Convert claim into an embedding
    claim_embedding = model.encode(
        [claim]
    )

    # Compare claim with every evidence chunk
    similarities = cosine_similarity(
        claim_embedding,
        evidence_embeddings
    )[0]

    results = []

    for i, score in enumerate(similarities):

        if score >= threshold:

            results.append({
                "id": all_chunks[i]["id"],
                "source": all_chunks[i]["source"],
                "topic": all_chunks[i]["topic"],
                "text": all_chunks[i]["text"],
                "similarity_score": round(
                    float(score),
                    4
                )
            })

    # Highest similarity first
    results.sort(
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return results[:top_k]