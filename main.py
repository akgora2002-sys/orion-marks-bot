import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("8006374981:AAE0rR2MrQwqzu0l3bBvGuOQyeOoLh-6S6Q")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to ORION Marks Calculator!\n\n"
        "📩 Please send your SSC HTML result link.\n"
        "📊 I’ll calculate your score instantly."
    )

def extract_score_from_html_url(html_url):
    try:
        response = requests.get(html_url)
        soup = BeautifulSoup(response.content, "html.parser")

        name_tag = soup.find("div", {"id": "candName"})
        candidate_name = name_tag.text.strip() if name_tag else "Candidate"

        all_questions = soup.find_all("table", class_="menu-tbl")
        correct = wrong = 0

        for q in all_questions:
            selected = q.find("td", class_="bordertbl selectedOption")
            correct_ans = q.find("td", class_="rightAnsOption")

            if selected and correct_ans:
                if selected.text.strip() == correct_ans.text.strip():
                    correct += 1
                else:
                    wrong += 1

        attempted = correct + wrong
        unattempted = 100 - attempted
        score = correct * 2 - wrong * 0.5
        accuracy = (correct / attempted * 100) if attempted else 0

        return {
            "name": candidate_name,
            "correct": correct,
            "wrong": wrong,
            "unattempted": unattempted,
            "score": score,
            "accuracy": round(accuracy, 2)
        }

    except Exception as e:
        return {"error": str(e)}

async def handle_html_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid HTML link.")
        return

    await update.message.reply_text("🔍 Processing your result...")

    result = extract_score_from_html_url(url)

    if "error" in result:
        await update.message.reply_text(f"❌ Error: {result['error']}")
    else:
        await update.message.reply_text(
            f"📄 Candidate: {result['name']}\n"
            f"✅ Correct: {result['correct']}\n"
            f"❌ Wrong: {result['wrong']}\n"
            f"⭕ Unattempted: {result['unattempted']}\n\n"
            f"🧮 Score: {result['score']} / 200\n"
            f"📊 Accuracy: {result['accuracy']}%"
        )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_html_link))
    app.run_polling()

if __name__ == "__main__":
    main()
