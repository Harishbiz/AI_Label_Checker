import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

client = Groq(api_key=API_KEY)


def analyze_label(text):

    prompt = f"""
You are a Senior CDSCO Regulatory Affairs Officer.

Analyze the pharmaceutical label below according to CDSCO Rule 96.

Scoring Rules:
- Start with a score of 100.
- Deduct 10 marks for every missing mandatory field.
- Deduct 5 marks for every important regulatory deficiency.
- Do NOT return a fixed score.
- Calculate the score only from the uploaded label.

Return ONLY in this format:

Compliance Score: <number>

Mandatory Fields Present:
- ...

Missing Mandatory Fields:
- ...

Regulatory Observations:
- ...

AI Compliance Suggestions:
- ...

Final Compliance Summary:
...

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