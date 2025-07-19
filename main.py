from flask import Flask, request
import requests
from utils.ocr import extract_text_from_image
from utils.pdf_reader import extract_text_from_pdf
from utils.ai_engine import get_answer
from utils.filters import is_question_allowed

app = Flask(__name__)

TOKEN = "1773390714:SivnB7yFmA3IItUGShilTQPUFRTE2FEPrOTpurTX"

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    question = None

    if "photo" in message:
        file_id = message["photo"][-1]["file_id"]
        file_url = get_file_url(file_id)
        if file_url:
            question = extract_text_from_image(file_url)
        else:
            return send_message(chat_id, "خطا در دریافت عکس سلطان 🫠")

    elif "document" in message:
        file_id = message["document"]["file_id"]
        file_url = get_file_url(file_id)
        if file_url:
            question = extract_text_from_pdf(file_url)
        else:
            return send_message(chat_id, "خطا در دریافت PDF سلطان 😓")

    elif "text" in message:
        question = message["text"]

    else:
        return send_message(chat_id, "یه فایل یا سوال بفرست سلطان 🫡")

    if not is_question_allowed(question):
        return send_message(chat_id, "این سوال جزو مشق نیست سلطان 😎")

    answer = get_answer(question)
    return send_message(chat_id, answer)

def send_message(chat_id, text):
    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    res = requests.post(url, json=payload)
    return res.text

def get_file_url(file_id):
    url = f"https://tapi.bale.ai/bot{TOKEN}/getFile?file_id={file_id}"
    res = requests.get(url).json()

    if res.get("ok") and "result" in res:
        file_path = res["result"]["file_path"]
        return f"https://cdn.bale.ai/file/bot{TOKEN}/{file_path}"
    else:
        return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
