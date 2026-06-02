import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

QUESTIONS = {
    "الرياضيات": [
        {"q": "ما هو تكامل x^2؟", "a": ["x^3/3 + C", "2x", "x^2/2", "x^3"], "correct": 0},
        {"q": "ما هو مشتق sin(x)؟", "a": ["cos(x)", "-cos(x)", "tan(x)", "-sin(x)"], "correct": 0},
    ],
    "الفيزياء": [
        {"q": "ما هي وحدة القوة؟", "a": ["نيوتن", "جول", "واط", "باسكال"], "correct": 0},
        {"q": "سرعة الضوء تقريباً؟", "a": ["3x10^8 م/ث", "3x10^6 م/ث", "3x10^5 م/ث", "3x10^9 م/ث"], "correct": 0},
    ],
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("السنة الاولى", callback_data="year_1")],
        [InlineKeyboardButton("السنة الثانية", callback_data="year_2")],
        [InlineKeyboardButton("السنة الثالثة", callback_data="year_3")],
        [InlineKeyboardButton("السنة الرابعة", callback_data="year_4")],
    ]
    await update.message.reply_text(
        "مرحبا بك في بوت امتحانات الجامعة العراقية!\n\nاختر سنتك الدراسية:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("year_"):
        keyboard = [
            [InlineKeyboardButton("رياضيات", callback_data="subject_الرياضيات")],
            [InlineKeyboardButton("فيزياء", callback_data="subject_الفيزياء")],
            [InlineKeyboardButton("رجوع", callback_data="back_start")],
        ]
        await query.edit_message_text("اختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("subject_"):
        subject = data.replace("subject_", "")
        context.user_data["subject"] = subject
        context.user_data["q_index"] = 0
        context.user_data["score"] = 0
        await send_question(query, context, subject, 0)

    elif data.startswith("ans_"):
        subject = context.user_data.get("subject")
        index = context.user_data.get("q_index", 0)
        score = context.user_data.get("score", 0)
        chosen = int(data.split("_")[1])
        correct = QUESTIONS[subject][index]["correct"]
        if chosen == correct:
            score += 1
            context.user_data["score"] = score
            result = "صحيحة!"
        else:
            result = f"خطا! الصواب: {QUESTIONS[subject][index]['a'][correct]}"
        index += 1
        context.user_data["q_index"] = index
        if index < len(QUESTIONS[subject]):
            await query.edit_message_text(result)
            await send_question(query, context, subject, index)
        else:
            await query.edit_message_text(f"{result}\n\nانتهى الاختبار!\nنتيجتك: {score}/{len(QUESTIONS[subject])}")

    elif data == "back_start":
        keyboard = [
            [InlineKeyboardButton("السنة الاولى", callback_data="year_1")],
            [InlineKeyboardButton("السنة الثانية", callback_data="year_2")],
            [InlineKeyboardButton("السنة الثالثة", callback_data="year_3")],
            [InlineKeyboardButton("السنة الرابعة", callback_data="year_4")],
        ]
        await query.edit_message_text("اختر سنتك الدراسية:", reply_markup=InlineKeyboardMarkup(keyboard))

async def send_question(query, context, subject, index):
    q = QUESTIONS[subject][index]
    keyboard = [[InlineKeyboardButton(ans, callback_data=f"ans_{i}")] for i, ans in enumerate(q["a"])]
    await query.message.reply_text(f"سؤال {index+1}:\n{q['q']}", reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling(drop_pending_updates=True)
