import os
import requests
from flask import Flask, request
import fitz  # PyMuPDF
import base64
from PIL import Image
from io import BytesIO
import pytesseract

TOKEN = "1773390714:SivnB7yFmA3IItUGShilTQPUFRTE2FEPrOTpurTX"
OPENROUTER_API_KEY = "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"
VALID_QUESTIONS = ["2+2", "سوال 1", "سوال ریاضی", "جمع اعداد", "Who is Newton?"]

app = Flask(__name__)

@app.route('/')
def home():
    return '🤖 ربات مشق‌نویس آرتین فعاله!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    if "text" in message:
        handle_text(chat_id, message["text"])

    elif "photo" in message:
        file_id = message["photo"][-1]["file_id"]
        handle_file(chat_id, file_id, is_photo=True)

    elif "document" in message:
        file_id = message["document"]["file_id"]
        handle_file(chat_id, file_id, is_photo=False)

    return "ok"

def handle_text(chat_id, text):
    if any(q in text for q in VALID_QUESTIONS):
        answer = ask_openrouter(text)
        send_message(chat_id, answer)
    else:
        send_message(chat_id, "❗️سوال مورد تایید نیست.")

def handle_file(chat_id, file_id, is_photo):
    file_url = get_file_url(file_id)
    content = requests.get(file_url).content

    if is_photo:
        image = Image.open(BytesIO(content))
        extracted_text = pytesseract.image_to_string(image, lang='fas+eng')
    else:
        extracted_text = extract_text_from_pdf(BytesIO(content))

    if any(q in extracted_text for q in VALID_QUESTIONS):
        answer = ask_openrouter(extracted_text)
        send_message(chat_id, f"✅ پاسخ: {answer}")
    else:
        send_message(chat_id, "📄 فایل شما دریافت شد ولی سوال مورد تایید نبود.")

def extract_text_from_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def get_file_url(file_id):
    # از سرور بله فایل رو دریافت می‌کنیم
    resp = requests.get(f"https://tapi.bale.ai/bot{TOKEN}/getFile?file_id={file_id}")
    file_path = resp.json()["result"]["file_path"]
    return f"https://tapi.bale.ai/file/bot{TOKEN}/{file_path}"

def send_message(chat_id, text):
    url = f"https://tapi.bale.ai/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def ask_openrouter(question):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.7
    }
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    try:
        return res.json()['choices'][0]['message']['content']
    except:
        return "⚠️ مشکلی در دریافت پاسخ از هوش مصنوعی پیش آمد."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
