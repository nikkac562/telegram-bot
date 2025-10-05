import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3

BOT_TOKEN = "8091451459:AAGzkhi-Em5IEA3WKAHtFi_HKRo6coBgJg8"

logging.basicConfig(level=logging.INFO)

def init_db():
    conn = sqlite3.connect('numbers.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE,
            status TEXT DEFAULT 'free',
            donor_user_id INTEGER,
            donor_username TEXT
        )
    ''')
    conn.commit()
    conn.close()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Бот работает! Используйте /num или /giveNumb")

async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("📞 Использование: /num +77051234567")
            return
        
        phone = context.args[0]
        user = update.message.from_user
        
        if not phone.startswith('+') or len(phone) < 10:
            await update.message.reply_text("❌ Ошибка! Формат: +77051234567")
            return
        
        conn = sqlite3.connect('numbers.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO numbers (phone_number, donor_user_id, donor_username) VALUES (?, ?, ?)', (phone, user.id, user.username or user.first_name))
            conn.commit()
            await update.message.reply_text("✅ Номер взят, ожидайте)")
        except:
            await update.message.reply_text("❌ Этот номер уже занят!")
        finally:
            conn.close()
    except:
        await update.message.reply_text("❌ Ошибка!")

async def givenumb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = sqlite3.connect('numbers.db')
        cursor = conn.cursor()
        cursor.execute('SELECT phone_number FROM numbers WHERE status="free" LIMIT 1')
        number_data = cursor.fetchone()
        
        if not number_data:
            await update.message.reply_text("📵 Свободных номеров нет")
            return
        
        phone = number_data[0]
        cursor.execute('UPDATE numbers SET status="taken" WHERE phone_number=?', (phone,))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(f"📱 Ваш номер: {phone}\n📸 Отправьте фото")
        context.user_data['awaiting_photo'] = phone
    except:
        await update.message.reply_text("❌ Ошибка!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if 'awaiting_photo' not in context.user_data:
            return
        
        phone = context.user_data['awaiting_photo']
        conn = sqlite3.connect('numbers.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE numbers SET status="used" WHERE phone_number=?', (phone,))
        conn.commit()
        conn.close()
        
        await update.message.reply_text("✅ Фото принято!")
        del context.user_data['awaiting_photo']
    except:
        await update.message.reply_text("❌ Ошибка!")

def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("num", num_command))
    application.add_handler(CommandHandler("giveNumb", givenumb_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🚀 Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
