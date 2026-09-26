import os
import json
import requests
import telebot
from telebot import types
from threading import Thread
from flask import Flask

# --- Render/Railway Keep-Alive Web Server ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running perfectly 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web).start()

# --- Configs ---
BOT_TOKEN = "8999505407:AAG7ZPbLcLImO_yU2oDz8twH4gYlMPnI-wg"
ADMIN_ID = "7784016689"
ADMIN_USERNAME = "techpro_et"
TELEBIRR_PHONE = "0944905958"
ACCOUNT_NAME = "Biniyam Ayichew"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Webhook ግጭት እንዳይፈጥር ማጥፊያ
try:
    bot.remove_webhook()
except Exception:
    pass

DB_FILE = "database.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "orders": {}, "pending_orders": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "orders": {}, "pending_orders": {}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- ዋና ሜኑ ማሳያ ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🛍 እቃዎች ዝርዝር")
    btn2 = types.KeyboardButton("📦 የኔ ትዕዛዞች")
    btn3 = types.KeyboardButton("📞 ድጋፍ (Support)")
    markup.add(btn1, btn2, btn3)
    return markup

# --- የ Start ትዕዛዝ (ተጠቃሚን በዳታቤዝ ውስጥ መመዝገቢያ) ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = str(message.chat.id)
    username = message.from_user.username or "NoUsername"
    first_name = message.from_user.first_name or "User"

    data = load_data()
    if "users" not in data:
        data["users"] = {}
    
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "username": username,
            "first_name": first_name,
            "joined_at": str(message.date)
        }
        save_data(data)

    welcome_text = (
        f"🛍 <b>እንኳን ወደ TechPro Digital Store በደህና መጡ!</b>\n\n"
        f"እዚህ የተለያዩ ፕሪሚየም የዲጂታል አገልግሎቶችን በታላቅ ቅናሽ በቴሌብር ማግኘት ይችላሉ።\n\n"
        f"✨ <b>ፕሪሚየም AI አካውንቶች</b> (Gemini Pro, ChatGPT...)\n"
        f"📚 <b>ትምህርታዊ መተግበሪያዎች</b> (Duolingo, Canva...)\n"
        f"🛡 <b>ፕሪሚየም VPN እና ሌሎችም</b>\n\n"
        f"⚡ <i>ፈጣን እና አስተማማኝ አቅርቦት!</i>\n"
        f"ለመጀመር ከታች ያሉትን ምርጫዎች ይጠቀሙ።"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# --- ለአንተ ብቻ የተጠቃሚዎችን ቁጥር ማሳያ (/stats) ---
@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if str(message.chat.id) != ADMIN_ID:
        return

    data = load_data()
    users = data.get("users", {})
    total_users = len(users)
    pending_orders = len(data.get("pending_orders", {}))

    text = (
        f"📊 <b>የ TechPro Bot አጠቃላይ ስታቲስቲክስ፦</b>\n\n"
        f"👥 <b>ጠቅላላ የተመዘገቡ ተጠቃሚዎች፦</b> {total_users} ሰው\n"
        f"⏳ <b>ያልተፈጸሙ ክፍያዎች/ትዕዛዞች፦</b> {pending_orders} እቃ\n\n"
        f"<i>ማስታወሻ፦ ይህ መረጃ ለአንተ ብቻ የሚታይ ሚስጥራዊ ዳሽቦርድ ነው!</i>"
    )
    bot.send_message(message.chat.id, text)

# --- የእቃዎች ዝርዝር ---
@bot.message_handler(func=lambda msg: msg.text == "🛍 እቃዎች ዝርዝር")
def show_products(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_gemini = types.InlineKeyboardButton("✨ Gemini Pro 1 Month - 350 ETB", callback_data="buy_gemini")
    btn_chatgpt = types.InlineKeyboardButton("🤖 ChatGPT Plus 1 Month - 450 ETB", callback_data="buy_chatgpt")
    btn_canva = types.InlineKeyboardButton("🎨 Canva Pro 1 Year - 250 ETB", callback_data="buy_canva")
    markup.add(btn_gemini, btn_chatgpt, btn_canva)
    bot.send_message(message.chat.id, "🛒 <b>የሚፈልጉትን አገልግሎት ይምረጡ፦</b>", reply_markup=markup)

# --- የግዢ ሂደት (ክፍያ ማሳያ) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def process_buy(call):
    products = {
        "buy_gemini": ("Gemini Pro (1 Month)", 350),
        "buy_chatgpt": ("ChatGPT Plus (1 Month)", 450),
        "buy_canva": ("Canva Pro (1 Year)", 250)
    }
    item, price = products[call.data]
    user_id = str(call.message.chat.id)

    data = load_data()
    if "pending_orders" not in data:
        data["pending_orders"] = {}
    
    data["pending_orders"][user_id] = {"item": item, "price": price}
    save_data(data)

    payment_info = (
        f"📦 <b>ትዕዛዝ፦</b> {item}\n"
        f"💰 <b>ዋጋ፦</b> {price} ብር\n\n"
        f"💳 <b>የቴሌብር መክፈያ ቁጥር፦</b>\n"
        f"📱 <code>{TELEBIRR_PHONE}</code>\n"
        f"👤 <b>ስም፦</b> {ACCOUNT_NAME}\n\n"
        f"⚠️ <b>ክፍያውን ከፈጸሙ በኋላ፦</b>\n"
        f"የከፈሉበትን የቴሌብር ደረሰኝ (Screenshot ወይም SMS መልእክት) እዚህ ቻት ላይ ይላኩ።"
    )
    bot.send_message(call.message.chat.id, payment_info)

# --- ደረሰኝ ሲላክ ወደ አድሚን መላኪያ ---
@bot.message_handler(content_types=['photo', 'text'])
def handle_receipt(message):
    user_id = str(message.chat.id)
    data = load_data()
    pending = data.get("pending_orders", {}).get(user_id)

    if not pending:
        if message.text == "📦 የኔ ትዕዛዞች":
            bot.send_message(message.chat.id, "📦 እስካሁን የፈጸሙት የተጠናቀቀ ትዕዛዝ የለም።")
            return
        elif message.text == "📞 ድጋፍ (Support)":
            bot.send_message(message.chat.id, f"ለማንኛውም ጥያቄ አድሚናችንን ያነጋግሩ፦ @{ADMIN_USERNAME}")
            return
        return

    item = pending["item"]
    price = pending["price"]

    # ለአድሚን ማሳወቂያ መላክ
    admin_markup = types.InlineKeyboardMarkup()
    btn_approve = types.InlineKeyboardButton("✅ ፍቀድ (Approve)", callback_data=f"app_{user_id}")
    btn_reject = types.InlineKeyboardButton("❌ ውድቅ አድርግ", callback_data=f"rej_{user_id}")
    admin_markup.add(btn_approve, btn_reject)

    admin_caption = (
        f"🔔 <b>አዲስ የክፍያ ደረሰኝ ደርሷል!</b>\n\n"
        f"👤 <b>ተጠቃሚ፦</b> @{message.from_user.username or 'NoUsername'} (<code>{user_id}</code>)\n"
        f"🛍 <b>እቃ፦</b> {item}\n"
        f"💰 <b>ዋጋ፦</b> {price} ብር"
    )

    if message.content_type == 'photo':
        photo_id = message.photo[-1].file_id
        bot.send_photo(ADMIN_ID, photo_id, caption=admin_caption, reply_markup=admin_markup)
    else:
        bot.send_message(ADMIN_ID, f"{admin_caption}\n\n📝 <b>ደረሰኝ ጽሁፍ፦</b>\n{message.text}", reply_markup=admin_markup)

    bot.reply_to(message, "✅ <b>ደረሰኝዎ ደርሶናል!</b> ክፍያዎ ተረጋግጦ እቃዎ በደቂቃዎች ውስጥ ይላክልዎታል።")

# --- የአድሚን ማረጋገጫ (Approve / Reject) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("app_") or call.data.startswith("rej_"))
def admin_action(call):
    action, user_id = call.data.split("_")
    data = load_data()
    order_info = data.get("pending_orders", {}).pop(user_id, None)
    save_data(data)

    if action == "app":
        bot.edit_message_caption("✅ ይህ ትዕዛዝ ጸድቆ እቃው እንዲላክ ተደርጓል።", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(
            user_id,
            f"🎉 <b>እንኳን ደስ አለዎት! ክፍያዎ ተረጋግጧል።</b>\n\n"
            f"እቃዎ ዝግጁ ነው! ለዝርዝር መመሪያና አጠቃቀም ድጋፍ ሰጪያችንን ያነጋግሩ፦ @{ADMIN_USERNAME}"
        )
    else:
        bot.edit_message_caption("❌ ይህ ትዕዛዝ ውድቅ ተደርጓል።", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(user_id, f"❌ <b>ክፍያዎ አልተረጋገጠም</b>። እባክዎ ትክክለኛውን ደረሰኝ ያያይዙ ወይም አድሚኑን ያነጋግሩ፦ @{ADMIN_USERNAME}")

# --- ቦቱን ማስነሳት ---
bot.infinity_polling(skip_pending=True)
