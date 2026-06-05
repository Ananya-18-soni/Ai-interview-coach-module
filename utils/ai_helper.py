import os
import google.generativeai as genai

# ---------------- GEMINI CONFIG ----------------

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
print("ERROR: GEMINI_API_KEY not found")
model = None
else:
try:
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
print("Gemini initialized successfully")
except Exception as e:
print(f"Gemini initialization failed: {e}")
model = None

# ---------------- GENERATE QUESTIONS ----------------

def generate_questions(role, level):

```
if model is None:
    return """
```

1. Tell me about yourself.
2. What are your strengths?
3. What are your weaknesses?
4. Why should we hire you?
5. Where do you see yourself in 5 years?
   """

   try:
   prompt = f"""
   Generate 5 interview questions.

Role: {role}
Level: {level}

Return only questions.
"""

```
    response = model.generate_content(prompt)

    if hasattr(response, "text"):
        return response.text

    return "Unable to generate questions."

except Exception as e:
    print("Question Generation Error:", e)

    return """
```

1. Tell me about yourself.
2. Why are you interested in this role?
3. What are your strengths?
4. Describe a challenge you faced.
5. Why should we hire you?
   """

# ---------------- EVALUATE ANSWERS ----------------

def evaluate_answer(role, question, answer):

```
if model is None:
    return """
```

Score: 7/10

Strengths:

* Answer provided
* Relevant information included

Weaknesses:

* Needs more detail

Suggestions:

* Add practical examples
* Improve explanation
  """

  try:
  prompt = f"""
  Evaluate this answer.

Role:
{role}

Question:
{question}

Answer:
{answer}

Give:

Score /10

Strengths

Weaknesses

Suggestions
"""

```
    response = model.generate_content(prompt)

    if hasattr(response, "text"):
        return response.text

    return "Unable to evaluate answer."

except Exception as e:
    print("Evaluation Error:", e)

    return f"""
```

Score: 6/10

Error occurred while evaluating:
{str(e)}

Please try again.
"""
