import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Încarcă variabilele din .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Sistem de puncte simplu (stocare in memorie)
user_points = {}

# Povestea tokenului
TOKEN_STORY = """
🐢 **@MarioAMG - Token Comunitar Energie Verde** 🐢

Adresa token: `EmCyM99NzMErfSoQhx6hgPo7qNTdeF2eDmdqiEy8pump`
Supply: **1 miliard**
No mint! Imutabil!
Tranzacționabil pe: Pump.fun, Jupiter, MEXC, DEX Tools și multe altele.

**Misiune:** Susținerea energiei verzi și a panourilor solare. Comunitate activă, direcție clară pentru energie regenerabilă!

**Reguli MICA:** Mesaje clare, Interactivitate, Claritate, Accesibilitate.

**Quiz & Rewards:** Răspunde la quiz-uri, adună puncte! La 10.000 puncte primești 100 $MarioAMG. 
Airdropuri și mining – curând!

**Join the green movement!**
"""

QUIZ_QUESTIONS = [
    {
        "q": "Ce misiune are tokenul MarioAMG?",
        "a": ["Energie verde și panouri solare", "Trading", "Gaming"],
        "correct": 0
    },
    {
        "q": "Care este supply-ul total?",
        "a": ["10.000", "1 miliard", "100"],
        "correct": 1
    },
    {
        "q": "Tokenul MarioAMG poate fi mintat?",
        "a": ["Da", "Nu"],
        "correct": 1
    }
]

QUIZ, QUIZ_ANSWER = range(2)

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Trimite logo + poveste
    chat_id = update.effective_chat.id
    img_path = os.path.join("assets", "logo.png")
    if os.path.exists(img_path):
        await context.bot.send_photo(chat_id, photo=open(img_path, 'rb'))
    await update.message.reply_text(TOKEN_STORY, parse_mode="Markdown")

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['quiz_score'] = 0
    context.user_data['quiz_step'] = 0
    await update.message.reply_text(f"Începe quiz-ul MarioAMG! Răspunde la întrebări și câștigă puncte.")
    return await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data['quiz_step']
    if step < len(QUIZ_QUESTIONS):
        q = QUIZ_QUESTIONS[step]
        options = "\n".join([f"{idx+1}. {opt}" for idx, opt in enumerate(q["a"])])
        await update.message.reply_text(f"{q['q']}\n{options}")
        return QUIZ_ANSWER
    else:
        score = context.user_data['quiz_score']
        user_id = update.effective_user.id
        user_points[user_id] = user_points.get(user_id, 0) + score * 100  # 100 puncte per răspuns corect
        await update.message.reply_text(f"Quiz terminat! Ai câștigat {score*100} puncte.\nTotal puncte: {user_points[user_id]}")
        if user_points[user_id] >= 10000:
            await update.message.reply_text("Felicitări! Ai câștigat 100 $MarioAMG 🎉")
        return ConversationHandler.END

async def answer_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data['quiz_step']
    q = QUIZ_QUESTIONS[step]
    try:
        answer = int(update.message.text.strip()) - 1
    except ValueError:
        await update.message.reply_text("Introdu numărul răspunsului!")
        return QUIZ_ANSWER
    if answer == q["correct"]:
        context.user_data['quiz_score'] += 1
        await update.message.reply_text("Corect! ✅")
    else:
        await update.message.reply_text("Greșit! ❌")
    context.user_data['quiz_step'] += 1
    return await ask_question(update, context)

def main():
    if not TELEGRAM_TOKEN:
        print("EROARE: Telegram token-ul nu este setat! Verifică fișierul .env.")
        return
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("info", info))

    quiz_conv = ConversationHandler(
        entry_points=[CommandHandler("quiz", start_quiz)],
        states={
            QUIZ_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer_quiz)],
        },
        fallbacks=[],
    )
    app.add_handler(quiz_conv)

    app.run_polling()

if __name__ == "__main__":
    main()
