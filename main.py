import os
import fitz
import pytesseract
import openai
from PIL import Image
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# بارگذاری تنظیمات
BOT_TOKEN = "7739258515:AAEUXIZ3ySZ9xp9W31l7qr__sZkbf6qcKnE"
OPENROUTER_API_KEY = "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"
# تنظیمات OpenRouter
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_type = "open_router"

# تولید پاسخ
def solve_question(text):
    prompt = f"سوالات زیر را حل کن و با توضیح مرحله به مرحله پاسخ بده:\n{text}"
    res = openai.ChatCompletion.create(
        model="mistralai/mistral-7b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

# استخراج متن از PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    return all_text

# استخراج متن از عکس
def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="eng+fas")
    return text

# بررسی عدد اول برای حل یک سوال خاص
def extract_specific_question(text):
    lines = text.strip().split("\n")
    first_line = lines[0]
    if first_line.strip().isdigit():
        number = int(first_line.strip())
        rest = "\n".join(lines[1:])
        questions = [q.strip() for q in rest.split("\n\n") if q.strip()]
        if 0 < number <= len(questions):
            return questions[number - 1]
        return "شماره سوال وجود ندارد."
    else:
        return text  # همه سوالات

# شروع
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام سلطان 🎓!\nسوالتو به صورت عکس یا PDF یا متن بفرست تا حلش کنم.")

# مدیریت فایل‌ها (عکس و PDF)
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document or update.message.photo[-1]
    file_id = file.file_id
    file_path = f"downloads/{file_id}"
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

# مدیریت متن مستقیم
def handle_text(update: Update, context: CallbackContext):
    user_text = update.message.text
    final_text = extract_specific_question(user_text)
    update.message.reply_text("در حال حل سوال...")
    answer = solve_question(final_text)
    update.message.reply_text(answer)

# راه‌اندازی ربات
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
