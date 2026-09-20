from google import genai
import json


def verify_with_gemini(prompt):

    client = genai.Client()

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt
    )

    result = response.output_text

    try:
        return json.loads(result)

    except json.JSONDecodeError:
        return {
            "verdict": "UNCERTAIN",
            "confidence": "LOW",
            "explanation": result
        }