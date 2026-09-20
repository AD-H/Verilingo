import requests
from bs4 import BeautifulSoup


def fetch_webpage(url):

    response = requests.get(
        url,
        timeout=10,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            )
        }
    )

    if response.status_code == 403:
        raise Exception(
            "This website blocks automated requests."
        )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove clearly non-content HTML elements
    unwanted_tags = [
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "noscript",
        "iframe",
        "svg",
        "button"
    ]

    for element in soup(unwanted_tags):
        element.decompose()

    # Try to locate the actual article
    main_content = (
        soup.find("article")
        or soup.find("main")
        or soup.find(
            "div",
            class_=lambda value:
            value and "article" in str(value).lower()
        )
    )

    if main_content:

        text = main_content.get_text(
            separator=" ",
            strip=True
        )

    else:

        text = soup.get_text(
            separator=" ",
            strip=True
        )

    # Clean excessive whitespace
    text = " ".join(
        text.split()
    )

    return text