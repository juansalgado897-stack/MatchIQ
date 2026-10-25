
"""
MatchIQ — Microsoft Foundry Local Demo

Runs a football analytics question using a local AI model.
Requires Microsoft Foundry Local and a loaded model.

This is an optional local demonstration.
The public Streamlit app continues to use Groq.
"""

import json
import subprocess
from urllib.request import urlopen

from openai import OpenAI


MODEL_ID = "qwen3-0.6b-generic-cpu:4"


def get_foundry_url():
    """Discover the active Foundry Local server URL."""
    result = subprocess.run(
        ["foundry", "server", "status", "--output", "json"],
        capture_output=True,
        text=True,
        check=True,
    )

    status = json.loads(result.stdout)

    # Find the local URL without hardcoding the changing port.
    def find_url(value):
        if isinstance(value, str):
            if value.startswith("http://127.0.0.1:"):
                return value
        elif isinstance(value, dict):
            for item in value.values():
                found = find_url(item)
                if found:
                    return found
        elif isinstance(value, list):
            for item in value:
                found = find_url(item)
                if found:
                    return found
        return None

    url = find_url(status)

    if not url:
        raise RuntimeError(
            "Foundry Local URL not found. Run: foundry server status"
        )

    return url.rstrip("/")


def main():
    server_url = get_foundry_url()

    client = OpenAI(
        base_url=f"{server_url}/v1",
        api_key="local",
    )

    prompt = (
        "You are MatchIQ, a football analytics assistant. "
        "Analyze these fictional, synthetic match statistics:\n"
        "Harbor City FC: 193 events, 12 shots, 1.967 simulated xG.\n"
        "Northbridge United: 198 events, 11 shots, "
        "2.527 simulated xG.\n"
        "Which team has higher simulated xG? "
        "Answer in one sentence. Do not invent a final score."
    )

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )

    print("MatchIQ — Microsoft Foundry Local")
    print(f"Model: {MODEL_ID}")
    print(f"Server: {server_url}")
    print()
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
