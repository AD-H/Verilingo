from web_search import search_web
from source_retriever import fetch_webpage


claim = "The RBI will discontinue UPI."

results = search_web(
    claim,
    max_results=5
)

print("\n===== TESTING WEB SOURCE EXTRACTION =====\n")

for i, result in enumerate(results, start=1):

    print(f"Trying Result {i}:")
    print(result["title"])
    print(result["url"])

    try:

        text = fetch_webpage(
            result["url"]
        )

        print("\nSUCCESS")
        print("Extracted characters:", len(text))
        print("\nPreview:")
        print(text[:1000])

        break

    except Exception as error:

        print("FAILED:", error)

    print("\n" + "=" * 60)