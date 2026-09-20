from web_search import search_web
from source_retriever import fetch_webpage
from document_processor import create_chunks


claim = "The RBI will discontinue UPI."

results = search_web(
    claim,
    max_results=5
)

print("\n===== WEBPAGE → CHUNKS TEST =====\n")

for result in results:

    print("Source:", result["title"])
    print("URL:", result["url"])

    try:

        text = fetch_webpage(
            result["url"]
        )

        chunks = create_chunks(
            text,
            chunk_size=80,
            overlap=20
        )

        print("\nNumber of chunks:", len(chunks))

        for i, chunk in enumerate(chunks[:5], start=1):

            print(f"\nChunk {i}:")
            print(chunk[:500])

        break

    except Exception as error:

        print("Failed:", error)
        print("\nTrying next source...\n")