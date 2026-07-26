import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables (.env locally, Render environment in production)
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

client = Groq(api_key=API_KEY)


def analyze_label(text):
    prompt = f"""
You are a Senior CDSCO Regulatory Affairs Officer.

Analyze the following pharmaceutical label.

Return the response in this format:

Compliance Score: XX

Mandatory Fields Present

Missing Mandatory Fields

Regulatory Observations

AI Compliance Suggestions

Final Compliance Summary

Label:

{text}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=1800
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error:\n\n{str(e)}"