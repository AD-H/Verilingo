from google import genai

client = genai.Client()

response = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain in one sentence what fact verification means."
)

print(response.output_text)