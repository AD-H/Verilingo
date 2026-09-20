import re
from datetime import datetime


def analyze_claim(claim):
    """
    Extract basic structured information from a user claim.

    This is intentionally domain-independent.
    """

    text = claim.strip()
    lower = text.lower()

    # -----------------------------
    # Detect location
    # -----------------------------

    location = None

    location_patterns = [
        r"\bin ([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
        r"\bat ([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
        r"\bnear ([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)",
    ]

    for pattern in location_patterns:
        match = re.search(pattern, text)

        if match:
            location = match.group(1).strip()
            break

    # Common location phrases written in lowercase
    known_locations = [
        "chennai",
        "vellore",
        "katpadi",
        "bangalore",
        "bengaluru",
        "mumbai",
        "delhi",
        "hyderabad",
        "kolkata",
        "pune",
        "coimbatore",
        "madurai",
        "tamil nadu",
        "india"
    ]

    if location is None:
        for place in known_locations:
            if place in lower:
                location = place.title()
                break

    # -----------------------------
    # Detect time
    # -----------------------------

    time_reference = "current"

    time_patterns = {
        "today": ["today", "currently", "right now", "at present"],
        "tomorrow": ["tomorrow", "next day"],
        "yesterday": ["yesterday"],
        "this week": ["this week"],
        "next week": ["next week"],
        "tonight": ["tonight"],
        "this month": ["this month"],
        "next month": ["next month"],
    }

    for reference, patterns in time_patterns.items():
        for pattern in patterns:
            if pattern in lower:
                time_reference = reference
                break

        if time_reference != "current":
            break

    # -----------------------------
    # Detect broad event/topic
    # -----------------------------

    event_keywords = [
        "flood",
        "flooding",
        "rain",
        "cyclone",
        "storm",
        "earthquake",
        "protest",
        "strike",
        "internet",
        "internet shutdown",
        "power cut",
        "school closure",
        "schools closed",
        "train cancellation",
        "flight cancellation",
        "election",
        "government",
        "policy",
        "ban",
        "accident",
        "fire",
        "warning",
        "outbreak"
    ]

    detected_events = []

    for keyword in event_keywords:
        if keyword in lower:
            detected_events.append(keyword)

    # -----------------------------
    # Detect negation
    # -----------------------------

    negative_patterns = [
        " no ",
        " not ",
        " never ",
        " doesn't ",
        " does not ",
        " won't ",
        " will not ",
        " isn't ",
        " is not ",
        " aren't ",
        " are not ",
        " hasn't ",
        " has not "
    ]

    padded_text = " " + lower + " "

    is_negative = any(
        pattern in padded_text
        for pattern in negative_patterns
    )

    return {
        "claim": text,
        "location": location,
        "time_reference": time_reference,
        "events": detected_events,
        "is_negative": is_negative
    }


if __name__ == "__main__":

    test_claims = [
        "Floods are affecting Chennai today.",
        "There will be no internet during the protest in Chennai.",
        "The Earth has a moon.",
        "Schools in Vellore will be closed tomorrow."
    ]

    for claim in test_claims:

        print("\n" + "=" * 60)
        print("CLAIM:", claim)
        print("=" * 60)

        result = analyze_claim(claim)

        for key, value in result.items():
            print(f"{key}: {value}")