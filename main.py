from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import BOT_TOKEN

app = ApplicationBuilder().token(BOT_TOKEN).build()
user_names = {}
waiting_for_reminder = set()

# ⏳ دالة تنفيذ التذكير
async def remind(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.chat_id
    name = user_names.get(user_id, "حبي")
    await context.bot.send_message(chat_id=user_id, text=f"⏰ هااا {name}، لا تنسى: {job.data}، مثل ما وصيتني 😎")

# 🚀 دالة البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_names:
        await update.message.reply_text("هلا حبي، شنو اسمك حتى أناديك بيه بالتذكيرات؟")
    else:
        keyboard = [[KeyboardButton("➕ أضف تذكير")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"هلا {user_names[user_id]} 🌟، شتريدني أذكّرك؟",
            reply_markup=reply_markup
        )

# 🧠 معالجة الرسائل النصية (اسم أو تذكير)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # حفظ الاسم
    if user_id not in user_names:
        user_names[user_id] = text
        await update.message.reply_text(f"تم، سجلتك باسم {text} ✅")
        keyboard = [[KeyboardButton("➕ أضف تذكير")]]
        await update.message.reply_text("هسة تقدر تضيف تذكير، اختار من الزر 👇", 
                                        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    # الضغط على زر إضافة تذكير
    if text == "➕ أضف تذكير":
        waiting_for_reminder.add(user_id)
        await update.message.reply_text("كلي التذكير بهالشكل:\n`بعد 10 اشرب دواك`")
        return

    # إدخال تذكير
    if user_id in waiting_for_reminder:
        # تعديل هنا لتحليل الرسالة بشكل مرن
        if text.startswith("بعد"):
            try:
                # تقسيم النص إلى أجزاء باستخدام مسافة كفاصل
                parts = text.split(" ", 2)
                
                if len(parts) < 3:
                    await update.message.reply_text("❌ صيغة خطأ، لازم تكتب: بعد [عدد الدقائق] [المهمة]")
                    return
                
                delay = int(parts[1])  # الدقائق
                task = parts[2]         # المهمة

                # إضافة التذكير
                context.job_queue.run_once(remind, delay * 60, chat_id=user_id, data=task)
                await update.message.reply_text(f"تمام {user_names[user_id]}، راح أذكرك بـ: {task} بعد {delay} دقيقة ⏳")
                waiting_for_reminder.remove(user_id)
                return
            except ValueError:
                await update.message.reply_text("❌ صيغة خطأ، الدقائق لازم تكون رقم صحيح.")
        else:
            await update.message.reply_text("❌ الصيغة خطأ، حاول تكتب: بعد [عدد الدقائق] [المهمة]")

# ✅ إعداد التطبيق
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("🤖 بوت التذكير باللهجة العراقية شغّال...")
app.run_polling()
