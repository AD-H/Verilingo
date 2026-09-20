from ddgs import DDGS

from claim_analyzer import analyze_claim


BLOCKED_DOMAINS = [
    "facebook.com",
    "linkedin.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "youtube.com"
]


def build_search_queries(claim):
    analysis = analyze_claim(claim)

    queries = []

    # Original claim
    queries.append(claim)

    location = analysis["location"]
    events = analysis["events"]
    time_reference = analysis["time_reference"]

    # Build a topic phrase
    topic = " ".join(events)

    if location and topic:
        queries.append(
            f"{topic} {location} {time_reference}"
        )

        queries.append(
            f"{location} {topic} latest"
        )

        queries.append(
            f"{location} {topic} news"
        )

    elif location:
        queries.append(
            f"{location} {claim} latest"
        )

        queries.append(
            f"{location} latest news"
        )

    elif topic:
        queries.append(
            f"{topic} latest"
        )

        queries.append(
            f"{topic} news"
        )

    # Remove duplicates
    unique_queries = []

    for query in queries:
        if query not in unique_queries:
            unique_queries.append(query)

    return unique_queries


def search_web(claim, max_results=5):

    results = []

    queries = build_search_queries(claim)

    print("\n===== SEARCH QUERIES =====")

    for query in queries:
        print(query)

    print("==========================\n")

    with DDGS() as ddgs:

        for query in queries:

            try:
                search_results = ddgs.text(
                    query,
                    max_results=max_results
                )

                for result in search_results:

                    url = result.get("href", "")

                    if not url:
                        continue

                    if any(
                        domain in url.lower()
                        for domain in BLOCKED_DOMAINS
                    ):
                        continue

                    results.append({
                        "title": result.get("title", ""),
                        "url": url,
                        "snippet": result.get("body", "")
                    })

            except Exception as error:

                print(
                    f"Search failed for query: {query}"
                )

                print(
                    f"Reason: {error}"
                )

    # Remove duplicate URLs

    unique_results = []
    seen_urls = set()

    for result in results:

        if result["url"] in seen_urls:
            continue

        seen_urls.add(result["url"])
        unique_results.append(result)

    return unique_results


if __name__ == "__main__":

    test_claims = [
        "Floods are affecting Chennai today.",
        "There will be no internet during the protest in Chennai."
    ]

    for claim in test_claims:

        print("\n")
        print("=" * 70)
        print("CLAIM:", claim)
        print("=" * 70)

        results = search_web(
            claim,
            max_results=3
        )

        for i, result in enumerate(results, start=1):

            print(f"\nResult {i}")
            print("Title:", result["title"])
            print("URL:", result["url"])
            print("Snippet:", result["snippet"])