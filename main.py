import os
import fitz  # PyMuPDF
import pytesseract
import openai
from PIL import Image
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# جواب گرفتن از مدل زبانی
def solve_question(text):
    prompt = f"سوالات زیر را حل کن و مرحله به مرحله توضیح بده:\n{text}"
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

# اگر PDF باشه
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    return all_text

# اگر عکس باشه
def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="eng+fas")
    return text

# بررسی وجود عدد خاص (مثلاً 13) برای حل فقط اون سوال
def extract_specific_question(text):
    lines = text.strip().split("\n")
    first_line = lines[0]
    if first_line.strip().isdigit():
        question_number = int(first_line.strip())
        rest = "\n".join(lines[1:])
        questions = [q.strip() for q in rest.split("\n\n") if q.strip()]
        if 0 < question_number <= len(questions):
            return questions[question_number - 1]
        else:
            return "شماره سوال یافت نشد."
    else:
        return text  # همه سوالات حل شوند

# شروع ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام سلطان 🎓! عکس یا PDF یا متن سوالتو بفرست تا حلش کنم.")

# رسیدگی به فایل و عکس و متن
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document or update.message.photo[-1]
    file_path = f"downloads/{file.file_id}"
    os.makedirs("downloads", exist_ok=True)

    file.get_file().download(file_path)

    if file.mime_type == "application/pdf":
        raw_text = extract_text_from_pdf(file_path)
    else:
        raw_text = extract_text_from_image(file_path)

    final_text = extract_specific_question(raw_text)
    update.message.reply_text("در حال حل سوال...")
    answer = solve_question(final_text)
    update.message.reply_text(answer)

def handle_text(update: Update, context: CallbackContext):
    user_text = update.message.text
    final_text = extract_specific_question(user_text)
    update.message.reply_text("در حال حل سوال...")
    answer = solve_question(final_text)
    update.message.reply_text(answer)

# راه‌اندازی
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document | Filters.photo, handle_file))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
