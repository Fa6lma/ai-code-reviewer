from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    code = data.get("code", "")
    language = data.get("language", "Python")

    if not code.strip():
        return jsonify({
            "error": "Please enter some code."
        }), 400

    prompt = f"""
You are an expert software engineer.

Review this {language} code:

{code}

Explain:
- Bugs
- Security problems
- Performance problems
- Readability problems
- How to improve it

Then provide an improved version of the code.

Keep the explanation simple and beginner-friendly.
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-oss-20b:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        timeout=60
    )

    if response.status_code != 200:
        return jsonify({
            "error": response.text
        }), response.status_code

    result = response.json()

    answer = result["choices"][0]["message"]["content"]

    return jsonify({
        "result": answer
    })


if __name__ == "__main__":
    app.run(debug=True)
    