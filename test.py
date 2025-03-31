from google import genai

client = genai.Client(api_key="AIzaSyA_YKTvtQzS7_z8hZfSZkW0KHw8Bwb108Q")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain how AI works",
)

print(response.text)