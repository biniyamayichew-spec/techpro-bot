import os
import json
import telebot
from telebot import types
from threading import Thread
from flask import Flask

# --- Keep-Alive Web Server (ለ Railway 24/7 እንዳይቋረጥ) ---
app = Flask('')

@app.route('/')
def home():
    return "TechPro Bot is 100% active and running fast!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()

# --- Configs ---
BOT_TOKEN = "8999505407:AAG7ZPbLcLImO_yU2oDz8twH4gYlMPnI-wg"
ADMIN_ID = "7784016689"
ADMIN_USERNAME = "techpro_et"
TELEBIRR_PHONE = "0944905958"
ACCOUNT_NAME = "Biniyam Ayichew"

# threaded=True እያንዳንዱን ትዕዛዝ በቅጽበት ለማስተናገድ ይረዳል
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", threaded=True)

# የቀረ Webhook ካለ በቅጽበት ማጥፊያ
try:
    bot.remove_webhook()
except Exception:
    pass

DB_FILE = "database.json"

# --- ፍጥነትን ለመጨመር መረጃውን በ RAM Memory መያዝ ---
def load_data():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "pending_orders": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "pending_orders": {}}

db_data = load_data()

def save_data_async():
    # ፋይል መጻፍ የቦቱን ፍጥነት እንዳያዘገየው በጀርባ (Thread) እንዲሰራ ማድረግ
    def _save():
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    Thread(target=_save, daemon=True).start()

# --- ኪቦርድ ሜኑ ---
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🛍 እቃዎች ዝርዝር"),
        types.KeyboardButton("📦 የኔ ትዕዛዞች"),
        types.KeyboardButton("📞 ድጋፍ (Support)")
    )
    return markup

# --- የ Start ትዕዛዝ (በቅጽበት ምላሽ የሚሰጥ) ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = str(message.chat.id)
    username = message.from_user.username or "NoUsername"
    first_name = message.from_user.first_name or "Customer"

    if "users" not in db_data:
        db_data["users"] = {}

    if user_id not in db_data["users"]:
        db_data["users"][user_id] = {
            "username": username,
            "first_name": first_name,
            "joined_at": str(message.date)
        }
        save_data_async()

    welcome_text = (
        f"🛍 <b>እንኳን ወደ TechPro Digital Store በደህና መጡ!</b>\n\n"
        f"እዚህ የተለያዩ ፕሪሚየም የዲጂታል አገልግሎቶችን በታላቅ ቅናሽ በቴሌብር ማግኘት ይችላሉ።\n\n"
        f"✨ <b>ፕሪሚየም AI አካውንቶች</b> (Gemini Pro, ChatGPT...)\n"
        f"📚 <b>ትምህርታዊ መተግበሪያዎች</b> (Duolingo, Canva...)\n"
        f"🛡 <b>ፕሪሚየም VPN እና ሌሎችም</b>\n\n"
        f"⚡ <i>ፈጣን እና አስተማማኝ አቅርቦት!</i>\n"
        f"ለመጀመር ከታች ያሉትን ምርጫዎች ይጠቀሙ።"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# --- ለአንተ ብቻ የሚታይ ስታቲስቲክስ (/stats) ---
@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if str(message.chat.id) != ADMIN_ID:
        return

    total_users = len(db_data.get("users", {}))
    pending_orders = len(db_data.get("pending_orders", {}))

    text = (
        f"📊 <b>የ TechPro Bot አጠቃላይ ስታቲስቲክስ፦</b>\n\n"
        f"👥 <b>ጠቅላላ የተመዘገቡ ተጠቃሚዎች፦</b> {total_users} ሰው\n"
        f"⏳ <b>ያልተፈጸሙ ክፍያዎች/ትዕዛዞች፦</b> {pending_orders} እቃ\n\n"
        f"⚡ <i>ቦቱ 24 ሰዓት በከፍተኛ ፍጥነት እየሰራ ነው!</i>"
    )
    bot.send_message(message.chat.id, text)

# --- የእቃዎች ዝርዝር (ፈጣን Inline Keyboard) ---
@bot.message_handler(func=lambda msg: msg.text == "🛍 እቃዎች ዝርዝር")
def show_products(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("✨ Gemini Pro 1 Month - 350 ETB", callback_data="buy_gemini"),
        types.InlineKeyboardButton("🤖 ChatGPT Plus 1 Month - 450 ETB", callback_data="buy_chatgpt"),
        types.InlineKeyboardButton("🎨 Canva Pro 1 Year - 250 ETB", callback_data="buy_canva")
    )
    bot.send_message(message.chat.id, "🛒 <b>የሚፈልጉትን አገልግሎት ይምረጡ፦</b>", reply_markup=markup)

# --- የግዢ ሂደት (Inline Button እንደተነካ በሰከንድ እውቅና ሰጥቶ መልእክት ይልካል) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def process_buy(call):
    # ቴሌግራም እንዳይዘገይ እና ስፒነሩ ወዲያው እንዲጠፋ
    bot.answer_callback_query(call.id)

    products = {
        "buy_gemini": ("Gemini Pro (1 Month)", 350),
        "buy_chatgpt": ("ChatGPT Plus (1 Month)", 450),
        "buy_canva": ("Canva Pro (1 Year)", 250)
    }
    item, price = products[call.data]
    user_id = str(call.message.chat.id)

    if "pending_orders" not in db_data:
        db_data["pending_orders"] = {}

    db_data["pending_orders"][user_id] = {"item": item, "price": price}
    save_data_async()

    payment_info = (
        f"📦 <b>ትዕዛዝ፦</b> {item}\n"
        f"💰 <b>ዋጋ፦</b> {price} ብር\n\n"
        f"💳 <b>የቴሌብር መክፈያ ቁጥር፦</b>\n"
        f"📱 <code>{TELEBIRR_PHONE}</code>\n"
        f"👤 <b>ስም፦</b> {ACCOUNT_NAME}\n\n"
        f"⚠️ <b>ክፍያውን ከፈጸሙ በኋላ፦</b>\n"
        f"የከፈሉበትን የቴሌብር ደረሰኝ (Screenshot ወይም የቴሌብር SMS ጽሑፍ) እዚህ ቻት ላይ ይላኩ።"
    )
    bot.send_message(call.message.chat.id, payment_info)

# --- ደረሰኝ መቀበያና ለአድሚን መላኪያ ---
@bot.message_handler(content_types=['photo', 'text'])
def handle_receipt(message):
    user_id = str(message.chat.id)
    pending = db_data.get("pending_orders", {}).get(user_id)

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

    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(
        types.InlineKeyboardButton("✅ ፍቀድ (Approve)", callback_data=f"app_{user_id}"),
        types.InlineKeyboardButton("❌ ውድቅ አድርግ", callback_data=f"rej_{user_id}")
    )

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
    bot.answer_callback_query(call.id)
    action, user_id = call.data.split("_")

    if "pending_orders" in db_data:
        db_data["pending_orders"].pop(user_id, None)
        save_data_async()

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

# --- ቦቱን ያለ ምንም መዘግየት በቅጽበት ማስነሳት ---
bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=10)
