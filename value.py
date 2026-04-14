import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 1. Логування
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- КОНФІГУРАЦІЯ ---
TOKEN = "takonn"
MY_ID = 8200640747  # <--- Твій ID від @userinfobot !!!

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {}
    
    # Вітання + Цінність
    welcome_text = (
        "Вітаємо 👋\n\n"
        "Ми допомагаємо оформити документи на нерухомість без черг, нервів та помилок. "
        "Відповідаємо протягом 15 хвилин!"
    )
    
    # Що потрібно? (Inline кнопки)
    keyboard = [
        [InlineKeyboardButton("📋 Техпаспорт", callback_data="service_Техпаспорт")],
        [InlineKeyboardButton("🏠 Введення в експлуатацію", callback_data="service_Введення")],
        [InlineKeyboardButton("🔍 Довідка БТІ", callback_data="service_Довідка")],
        [InlineKeyboardButton("❓ Інше / Консультація", callback_data="service_Консультація")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text)
    await update.message.reply_text("Що саме вам потрібно?", reply_markup=reply_markup)

async def button_tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    await query.answer()

    # Обробка вибору послуги
    if data.startswith("service_"):
        user_data[user_id]['service'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Квартира 🏢", callback_data="type_Квартира")],
            [InlineKeyboardButton("Будинок 🏡", callback_data="type_Будинок")],
            [InlineKeyboardButton("Земельна ділянка 🌱", callback_data="type_Ділянка")],
            [InlineKeyboardButton("Комерція 🏬", callback_data="type_Комерція")]
        ]
        await query.edit_message_text("Оберіть тип нерухомості:", reply_markup=InlineKeyboardMarkup(keyboard))

    # Обробка вибору типу нерухомості
    elif data.startswith("type_"):
        user_data[user_id]['realty_type'] = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Біла Церква", callback_data="city_Біла Церква"), 
             InlineKeyboardButton("Київ", callback_data="city_Київ")],
            [InlineKeyboardButton("Київська обл.", callback_data="city_Область"), 
             InlineKeyboardButton("Інше місто", callback_data="city_Інше")]
        ]
        await query.edit_message_text("Оберіть ваш населений пункт:", reply_markup=InlineKeyboardMarkup(keyboard))

    # Обробка вибору міста
    elif data.startswith("city_"):
        user_data[user_id]['city'] = data.split("_")[1]
        

        price_text = (
            "💰 Орієнтовна вартість:\n"
            "від 2500 до 8000 грн\n\n"
            "Точну ціну скаже наш фахівець після уточнення деталей об'єкту."
        )
        
   
        contact_keyboard = [[KeyboardButton("📞 Поділитися номером", request_contact=True)]]
        contact_markup = ReplyKeyboardMarkup(contact_keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await query.edit_message_text(price_text)
        await context.bot.send_message(
            chat_id=user_id, 
            text="Натисніть кнопку нижче, щоб ми могли зв'язатися з вами:", 
            reply_markup=contact_markup
        )

async def contact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    contact = update.message.contact
    phone = contact.phone_number
    
    if user_id in user_data:
       
        summary = (
            f"🚀 НОВА ЗАЯВКА!\n"
            f"👤 Клієнт: {update.effective_user.first_name}\n"
            f"📞 Тел: {phone}\n"
            f"🛠 Послуга: {user_data[user_id].get('service')}\n"
            f"🏠 Об'єкт: {user_data[user_id].get('realty_type')}\n"
            f"📍 Місто: {user_data[user_id].get('city')}\n"
            f"🔗 ТГ: @{update.effective_user.username if update.effective_user.username else 'немає'}"
        )
        
        try:
            await context.bot.send_message(chat_id=MY_ID, text=summary)
        except Exception as e:
            print(f"Помилка надсилання: {e}")

        await update.message.reply_text(
            "Дякуємо! 👍\nМи отримали вашу заявку. Наш менеджер зв'яжеться з вами протягом 15 хвилин.",
            reply_markup=ReplyKeyboardRemove()
        )
        del user_data[user_id]

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_tap)) # Обробка натискань Inline кнопок
    app.add_handler(MessageHandler(filters.CONTACT, contact_callback)) # Обробка кнопки контакту
    
    print("Бот з новим сценарієм запущений...")
    app.run_polling()
