import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("BOT_TOKEN")

QUESTIONS = {
    "رياضيات": [
        {"q": "تكامل x^2 يساوي؟", "a": ["x^3/3+C", "2x", "x^2/2", "x^3"], "c": 0},
        {"q": "مشتق sin(x) يساوي؟", "a": ["cos(x)", "-cos(x)", "tan(x)", "-sin(x)"], "c": 0},
    ],
    "فيزياء": [
        {"q": "وحدة القوة؟", "a": ["نيوتن", "جول", "واط", "باسكال"], "c": 0},
        {"q": "سرعة الضوء؟", "a": ["3x10^8", "3x10^6", "3x10^5", "3x10^9"], "c": 0},
    ],
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("السنة الاولى", callback_data="y1")],
        [InlineKeyboardButton("السنة الثانية", callback_data="y2")],
        [InlineKeyboardButton("السنة الثالثة", callback_data="y3")],
        [InlineKeyboardButton("السنة الرابعة", callback_data="y4")],
    ]
    await update.message.reply_text("مرحبا! اختر سنتك:", reply_markup=InlineKeyboardMarkup(kb))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    if d.startswith("y"):
        kb = [
            [InlineKeyboardButton("رياضيات", callback_data="s_رياضيات")],
            [InlineKeyboardButton("فيزياء", callback_data="s_فيزياء")],
        ]
        await q.edit_message_text("اختر المادة:", reply_markup=InlineKeyboardMarkup(kb))
    elif d.startswith("s_"):
        sub = d[2:]
        context.user_data.update({"sub": sub, "i": 0, "score": 0})
        await ask(q, context, sub, 0)
    elif d.startswith("a_"):
        sub = context.user_data["sub"]
        i = context.user_data["i"]
        score = context.user_data["score"]
        if int(d[2:]) == QUESTIONS[sub][i]["c"]:
            score += 1
            context.user_data["score"] = score
            res = "صح!"
        else:
            res = f"خطا! الجواب: {QUESTIONS[sub][i]['a'][QUESTIONS[sub][i]['c']]}"
        i += 1
        context.user_data["i"] = i
        if i < len(QUESTIONS[sub]):
            await q.edit_message_text(res)
            await ask(q, context, sub, i)
        else:
            await q.edit_message_text(f"{res}\nالنتيجة: {score}/{len(QUESTIONS[sub])}")

async def ask(q, context, sub, i):
    qd = QUESTIONS[sub][i]
    kb = [[InlineKeyboardButton(a, callback_data=f"a_{j}")] for j, a in enumerate(qd["a"])]
    await q.message.reply_text(f"سؤال {i+1}: {qd['q']}", reply_markup=InlineKeyboardMarkup(kb))

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling(drop_pending_updates=True)
