import os
from dotenv import dotenv_values
from groq import Groq

# Read .env
config = dotenv_values(".env")

API_KEY = config["GROQ_API_KEY"]

print("Loaded Groq Key:", API_KEY[:12] + "...")

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