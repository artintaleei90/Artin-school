import requests

API_KEY = "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"

def get_answer(question):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": question}]
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]
