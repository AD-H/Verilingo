from web_search import search_web
from source_retriever import fetch_webpage
from document_processor import (
    create_chunks,
    is_useful_chunk
)
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import urlparse

def is_good_web_text(text):
    """
    Check whether extracted webpage text is substantial
    enough to be used as evidence.
    """

    if not text:
        return False

    words = text.split()

    # Reject very short pages
    if len(words) < 30:
        return False

    navigation_terms = [
        "facebook",
        "twitter",
        "linkedin",
        "telegram",
        "subscribe",
        "newsletter",
        "download the app",
        "related articles",
        "related stories",
        "recommended",
        "trending",
        "latest news",
        "read more",
        "see less",
        "more from",
        "more news coverage",
        "web stories",
        "videos",
        "photos",
        "mobile recharge",
        "apply now",
        "explore more"
    ]

    text_lower = text.lower()

    matches = 0

    for term in navigation_terms:
        if term in text_lower:
            matches += 1

    # Too many navigation signals = probably webpage junk
    if matches >= 3:
        return False

    return True

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_source_quality(url):
    """
    Assign a source-quality score based on the domain.
    This score is used together with semantic similarity.
    """

    domain = urlparse(url).netloc.lower()

    # Remove www.
    domain = domain.replace("www.", "")

    # Primary / official sources
    official_domains = [
        "rbi.org.in",
        "npci.org.in",
        "gov.in",
        "nic.in",
        "nasa.gov",
        "who.int",
        "un.org",
        "isro.gov.in"
    ]

    # Major established news organizations
    major_news_domains = [
    "reuters.com",
    "bbc.com",
    "bbc.co.uk",
    "apnews.com",
    "thehindu.com",
    "indianexpress.com",
    "hindustantimes.com",
    "indiatoday.in",
    "businesstoday.in",
    "ndtv.com",
    "livemint.com",
    "mid-day.com",
    "thestatesman.com"
]

    # Government / official domain
    if (
        domain.endswith(".gov.in")
        or domain in official_domains
    ):
        return 1.0

    # Major news source
    if domain in major_news_domains:
        return 0.9

    # Other sources
    return 0.6


def retrieve_web_evidence(
    claim,
    max_sources=5,
    top_k=5,
    threshold=0.30
):
    search_results = search_web(
        claim,
        max_results=max_sources
    )

    all_chunks = []

    for result in search_results:

        try:
            page_text = fetch_webpage(result["url"])

            # Keep both webpage content and search-engine snippet.
            # The snippet may contain the most direct answer.
            texts_to_process = []

            if is_good_web_text(page_text):
                texts_to_process.append(page_text)

            if result.get("snippet"):
                texts_to_process.append(
                    result["snippet"]
                )

            # Remove duplicate/empty text
            unique_texts = []

            for text in texts_to_process:

                text = text.strip()

                if text and text not in unique_texts:
                    unique_texts.append(text)

            # Create chunks from both webpage and snippet
            for text in unique_texts:

                chunks = create_chunks(
                    text,
                    chunk_size=50,
                    overlap=15
                )

                for chunk in chunks:

                    if not is_useful_chunk(chunk):
                        continue

                    all_chunks.append({
                        "title": result["title"],
                        "url": result["url"],
                        "text": chunk
                    })

        except Exception as error:

            print(
                f"Skipping source: {result['url']}"
            )

            print(
                f"Reason: {error}"
            )

    if not all_chunks:
        return []

    # Encode claim
    claim_embedding = model.encode(
        [claim]
    )

    # Encode evidence
    evidence_texts = [
        item["text"]
        for item in all_chunks
    ]

    evidence_embeddings = model.encode(
        evidence_texts
    )

    similarities = cosine_similarity(
        claim_embedding,
        evidence_embeddings
    )[0]

    scored_chunks = []

    for i, score in enumerate(similarities):

        if score >= threshold:

            source_quality = get_source_quality(
                all_chunks[i]["url"]
            )

            final_score = (
                0.75 * float(score)
                +
                0.25 * source_quality
            )

            scored_chunks.append({
                "title": all_chunks[i]["title"],
                "url": all_chunks[i]["url"],
                "text": all_chunks[i]["text"],
                "similarity_score": round(
                    float(score),
                    4
                ),
                "source_quality": source_quality,
                "final_score": round(
                    final_score,
                    4
                )
            })

    scored_chunks.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    # Keep only the best result from each source
    unique_sources = []

    seen_urls = set()

    for item in scored_chunks:

        if item["url"] in seen_urls:
            continue

        seen_urls.add(
            item["url"]
        )

        unique_sources.append(
            item
        )

        if len(unique_sources) >= top_k:
            break

    return unique_sources


# -----------------------------------------
# Test
# -----------------------------------------

if __name__ == "__main__":

    claim = "The RBI will discontinue UPI."

    results = retrieve_web_evidence(
        claim,
        max_sources=5,
        top_k=5
    )

    print(
        "\n===== LIVE WEB EVIDENCE =====\n"
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print(f"Evidence {i}:")
        print("Title:", result["title"])
        print("URL:", result["url"])

        print(
            "Similarity:",
            result["similarity_score"]
        )

        print(
            "Source Quality:",
            result["source_quality"]
        )

        print(
            "Final Score:",
            result["final_score"]
        )

        print(
            "Text:",
            result["text"]
        )

        print(
            "\n" + "=" * 70
        )