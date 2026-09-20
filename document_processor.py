def clean_text(text):
    """
    Clean unnecessary whitespace from source text.
    """

    text = text.replace("\n", " ")
    text = " ".join(text.split())

    return text


def create_chunks(text, chunk_size=50, overlap=15):
    """
    Split text into sentence-based chunks.

    This keeps related sentences together and avoids
    arbitrary word boundaries.
    """

    text = clean_text(text)

    # Split approximately at sentence boundaries
    sentences = []

    current = ""

    for word in text.split():

        current += " " + word

        if word.endswith((".", "!", "?")):
            sentences.append(current.strip())
            current = ""

    if current.strip():
        sentences.append(current.strip())

    chunks = []

    current_chunk = []
    current_words = 0

    for sentence in sentences:

        sentence_words = len(sentence.split())

        if current_words + sentence_words <= chunk_size:

            current_chunk.append(sentence)
            current_words += sentence_words

        else:

            if current_chunk:
                chunks.append(
                    " ".join(current_chunk)
                )

            # Start a new chunk
            current_chunk = [sentence]
            current_words = sentence_words

    if current_chunk:
        chunks.append(
            " ".join(current_chunk)
        )

    return chunks
        
def is_useful_chunk(text):
    """
    Check whether a chunk contains meaningful article content
    rather than navigation, advertisements, or related-content sections.
    """

    text_lower = text.lower()

    unwanted_terms = [
        "breaking news",
        "editor picks",
        "most viewed",
        "photos videos",
        "subscribe",
        "advertisement",
        "sign in",
        "login",
        "latest news",
        "read more",
        "join our",
        "newsletter",
        "download the app",
        "follow us",
        "share this",
        "related articles",
        "recommended",
        "trending"
    ]

    unwanted_count = 0

    for term in unwanted_terms:
        if term in text_lower:
            unwanted_count += 1

    # Reject chunks containing multiple navigation/website terms
    if unwanted_count >= 2:
        return False

    # Reject very short chunks
    if len(text.split()) < 20:
        return False

    return True