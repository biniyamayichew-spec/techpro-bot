from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

keep_alive()
import telebot
from telebot import types
import requests
import json
import os

# --- Configurations ---
BOT_TOKEN = "8999505407:AAG7ZPbLcLImO_yU2oDz8twH4gYlMPnI-wg"
ADMIN_ID = "7784016689"
ADMIN_USERNAME = "techpro_et"
TELEBIRR_PHONE = "0944905958"
ACCOUNT_NAME = "Biniyam Ayichew"

# Hubex Reseller API Config
HUBEX_API_KEY = "rsk_live_f24928ff138b57ded652ceacb8cb233ba20e93a922b6b975"
HUBEX_BASE_URL = "https://open-greeting-glow-production.up.railway.app/api/public/reseller/v1"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

DATA_FILE = "database.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "pending_orders": {}}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "pending_orders": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# እቃዎች ዝርዝር
PRODUCTS = {
    "gemini_18m": {"name": "Gemini AI Pro 18m", "price": 599, "hubex_id": "gemini_18m"},
    "duolingo_12m": {"name": "Duolingo Super 12m", "price": 760, "hubex_id": "e648ed65-b9d5-4c25-b183-16cdd6b168b2"},
    "quillbot_1m": {"name": "QuillBot Premium 1m", "price": 950, "hubex_id": "quillbot_1m"},
    "notion_3m": {"name": "Notion Business 3m", "price": 1520, "hubex_id": "notion_3m"},
    "nordvpn_3m": {"name": "Nord VPN 3m", "price": 1710, "hubex_id": "nordvpn_3m"},
    "google_ai_12m": {"name": "Google AI Pro 12m", "price": 5700, "hubex_id": "9d538ade-bc2e-4bf1-842a-126a2b1be193"},
    "github_pack": {"name": "Github Developer Pack (2y)", "price": 7600, "hubex_id": "5ed27b42-73fb-4b1d-861f-79b390702d3e"},
    "elevenlabs_12m": {"name": "ElevenLabs Creator 12m", "price": 11400, "hubex_id": "elevenlabs_12m"},
}

def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🛍 Shop", callback_data="shop"))
    markup.add(types.InlineKeyboardButton("👤 My Profile", callback_data="profile"),
               types.InlineKeyboardButton("🎉 Refer & Earn", callback_data="refer"))
    markup.add(types.InlineKeyboardButton("🤝 Support", callback_data="support"))
    return markup

@bot.message_handler(commands=['start'])
def start_handler(message):
    data = load_data()
    user_id = str(message.chat.id)
    text_args = message.text.split()

    if user_id not in data["users"]:
        referrer_id = None
        if len(text_args) > 1:
            ref_candidate = text_args[1]
            if ref_candidate in data["users"] and ref_candidate != user_id:
                referrer_id = ref_candidate

        data["users"][user_id] = {
            "first_name": message.from_user.first_name,
            "username": message.from_user.username or "",
            "referrals": 0,
            "invited_by": referrer_id,
            "selected_product": None
        }

        if referrer_id:
            data["users"][referrer_id]["referrals"] += 1
            ref_count = data["users"][referrer_id]["referrals"]
            save_data(data)
            try:
                bot.send_message(
                    referrer_id,
                    f"🎉 አዲስ ሰው በእርስዎ ሊንክ ተቀላቅሏል!\n👥 ጠቅላላ የጋበዟቸው፦ <b>{ref_count}/50</b>"
                )
                if ref_count == 50:
                    bot.send_message(
                        referrer_id,
                        "🎊 <b>እንኳን ደስ አለዎት!</b> 50 ሰዎችን ጋብዘው ጨርሰዋል።\n"
                        f"ነፃ የ <b>Gemini AI Pro</b> አካውንትዎን ለመቀበል የደንበኞች ድጋፍን ያነጋግሩ፦ @{ADMIN_USERNAME}"
                    )
                    bot.send_message(
                        ADMIN_ID,
                        f"🚨 <b>ተጠቃሚ 50 ሰዎችን ጋብዟል!</b>\n"
                        f"User: @{data['users'][referrer_id]['username']} (ID: <code>{referrer_id}</code>)\n"
                        f"እባክዎ ነፃ የ Gemini AI Pro አካውንት ይስጡት።"
                    )
            except Exception:
                pass
        else:
            save_data(data)

    welcome_text = (
        "🛍 <b>ወደ ፕሪሚየም ዲጂታል መደብር እንኳን በደህና መጡ!</b>\n\n"
        "የምንሰጣቸው አገልግሎቶች፦\n"
        "• ፕሪሚየም AI አካውንቶች (Gemini Pro፣ ChatGPT...)\n"
        "• የመዝናኛ እና የሶፍትዌር አካውንቶች\n"
        "• ፈጣንና አስተማማኝ አቅርቦት\n\n"
        "👇 ለመቀጠል ከታች ካሉት አማራጮች አንዱን ይምረጡ፦"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = load_data()
    user_id = str(call.message.chat.id)

    if call.data == "main_menu":
        bot.edit_message_text(
            "👇 ለመቀጠል ከታች ካሉት አማራጮች አንዱን ይምረጡ፦",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_main_menu()
        )

    elif call.data == "shop":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, item in PRODUCTS.items():
            markup.add(types.InlineKeyboardButton(f"{item['name']} — {item['price']} ETB", callback_data=f"buy_{key}"))
        markup.add(types.InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu"))

        bot.edit_message_text(
            "🛍 <b>የእቃዎች መደብር (Shop Deals)</b>\n\nየሚፈልጉትን እቃ ይምረጡ፦",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    elif call.data.startswith("buy_"):
        product_key = call.data.replace("buy_", "")
        product = PRODUCTS.get(product_key)
        if product:
            if user_id in data["users"]:
                data["users"][user_id]["selected_product"] = product_key
                save_data(data)

            text = (
                f"🛒 <b>የተመረጠው እቃ፦</b> {product['name']}\n"
                f"💵 <b>ዋጋ፦</b> {product['price']} ETB\n\n"
                "📌 <b>የቴሌብር ክፍያ መመሪያ፦</b>\n"
                "የቴሌብር ስልክ ቁጥሩን በመጫን ኮፒ ያድርጉ፦\n"
                f"👉 <code>{TELEBIRR_PHONE}</code>\n"
                f"👤 <b>ስም፦</b> {ACCOUNT_NAME}\n\n"
                "✅ <b>ማስታወሻ፦</b> ክፍያውን እንደፈጸሙ የከፈሉበትን <b>ደረሰኝ (Screenshot ወይም SMS)</b> እዚህ ቦቱ ላይ በቀጥታ ይላኩ። እንዳረጋገጥን እቃዎ ወዲያውኑ ይላክልዎታ።\n\n"
                "⏰ <b>የማረጋገጫና ርክክብ ሰዓታት (የኢትዮጵያ ሰዓት)፦</b>\n"
                "• ጥዋት፦ 12:00 – 1:10 ሰዓት\n"
                "• ከሰዓትና ማታ፦ 10:00 – 4:00 ሰዓት"
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("◀️ Back to Shop", callback_data="shop"))
            bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

    # --- ADMIN APPROVAL HANDLERS ---
    elif call.data.startswith("appr_"):
        order_id = call.data.replace("appr_", "")
        order = data.get("pending_orders", {}).get(order_id)

        if not order:
            bot.answer_callback_query(call.id, "ይህ ትዕዛዝ አልተገኘም ወይም ተሰርቷል!", show_alert=True)
            return

        target_user_id = order["user_id"]
        product_key = order["product_key"]
        product = PRODUCTS.get(product_key)

        bot.answer_callback_query(call.id, "እቃው ከሰርቨር እየተገዛ ነው...")

        if call.message.caption:
            bot.edit_message_caption(
                caption=call.message.caption + "\n\n⏳ <b>እቃው እየተገዛ ነው...</b>",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
        else:
            bot.edit_message_text(
                text=call.message.text + "\n\n⏳ <b>እቃው እየተገዛ ነው...</b>",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )

        # Hubex API Call
        headers = {
            "Authorization": f"Bearer {HUBEX_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "product_id": product["hubex_id"],
            "quantity": 1
        }

        try:
            res = requests.post(f"{HUBEX_BASE_URL}/orders", json=payload, headers=headers, timeout=15)
            hubex_data = res.json()

            if res.status_code in [200, 201] and (hubex_data.get("ok") is True or hubex_data.get("success")):
                order_info = hubex_data.get("order", {}) or hubex_data.get("data", {})
                item_details = (
                    order_info.get("accountDetails") 
                    or order_info.get("licenseKey") 
                    or order_info.get("delivered_data") 
                    or hubex_data.get("delivered_data")
                    or "ፕሪሚየም አገልግሎትዎ በተሳካ ሁኔታ ነቅቷል!"
                )

                customer_msg = (
                    "🎉 <b>ክፍያዎ ተረጋግጧል!</b>\n\n"
                    f"📦 <b>የተገዛው እቃ፦</b> {product['name']}\n"
                    f"🔑 <b>የአካውንት መረጃ፦</b>\n"
                    f"<code>{item_details}</code>\n\n"
                    "ስለገዙ እናመሰግናለን! ጥያቄ ካለዎት ድጋፍን ያነጋግሩ።"
                )
                bot.send_message(target_user_id, customer_msg)

                fin_text = f"\n\n✅ <b>በትክክል ተልኳል (Delivered)</b>\n🆔 User ID: <code>{target_user_id}</code>"
                if call.message.caption:
                    bot.edit_message_caption(caption=call.message.caption + fin_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
                else:
                    bot.edit_message_text(text=call.message.text + fin_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

                del data["pending_orders"][order_id]
                save_data(data)

            else:
                err_msg = hubex_data.get("error") or hubex_data.get("message", "በሰርቨር በኩል ችግር አጋጥሟል")
                bot.send_message(ADMIN_ID, f"⚠️ <b>Hubex Error:</b> {err_msg}")

        except Exception as e:
            bot.send_message(ADMIN_ID, f"❌ Request Error: {e}")

    elif call.data.startswith("rejc_"):
        order_id = call.data.replace("rejc_", "")
        order = data.get("pending_orders", {}).get(order_id)
        if order:
            target_user_id = order["user_id"]
            bot.send_message(
                target_user_id,
                f"❌ <b>ክፍያዎ ውድቅ ተደርጓል!</b>\n"
                f"የላኩት ደረሰኝ አልተረጋገጠም። እባክዎ ትክክለኛውን ደረሰኝ ይላኩ ወይም የደንበኞች ድጋፍን ያነጋግሩ፦ @{ADMIN_USERNAME}"
            )
            rej_text = f"\n\n❌ <b>ውድቅ ተደርጓል (Rejected)</b>\n🆔 User ID: <code>{target_user_id}</code>"
            if call.message.caption:
                bot.edit_message_caption(caption=call.message.caption + rej_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            else:
                bot.edit_message_text(text=call.message.text + rej_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

            del data["pending_orders"][order_id]
            save_data(data)

    elif call.data == "profile":
        user_info = data["users"].get(user_id, {"referrals": 0})
        text = (
            "👤 <b>የእኔ መረጃ (My Profile)</b>\n\n"
            f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
            f"👥 <b>የጋበዟቸው ሰዎች ብዛት:</b> {user_info.get('referrals', 0)} / 50\n"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("◀️ Back", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

    elif call.data == "refer":
        bot_username = bot.get_me().username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        user_info = data["users"].get(user_id, {"referrals": 0})
        ref_count = user_info.get("referrals", 0)

        text = (
            "🎉 <b>ጓደኞችዎን ይጋብዙ — ነፃ Gemini AI Pro ያሸንፉ!</b>\n\n"
            "የራስዎን መጋበዣ ሊንክ ለጓደኞችዎ ያጋሩ። 50 ሰው በእርስዎ ሊንክ ቦቱን ሲቀላቀል፣ 1 ነፃ Gemini AI Pro አካውንት በራስ-ሰር ይሸለማሉ!\n\n"
            f"🔗 <b>የእርስዎ መጋበዣ ሊንክ፦</b>\n<code>{ref_link}</code>\n\n"
            f"👥 <b>የጋበዟቸው ሰዎች ብዛት፦</b> {ref_count} / 50"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("◀️ Back", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

    elif call.data == "support":
        text = (
            "🤝 <b>የደንበኞች ድጋፍ (Support)</b>\n\n"
            f"💬 <b>አግኙን፦</b> @{ADMIN_USERNAME}\n\n"
            "⏱ <b>የምላሽ ሰዓት፦</b> በአጭር ጊዜ ውስጥ ምላሽ እንሰጣለን።"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("◀️ Back", callback_data="main_menu"))
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.message_handler(content_types=['photo', 'text'])
def forward_receipt(message):
    if str(message.chat.id) == ADMIN_ID:
        return

    data = load_data()
    user_id = str(message.chat.id)
    selected_prod_key = data.get("users", {}).get(user_id, {}).get("selected_product", "gemini_18m")
    product = PRODUCTS.get(selected_prod_key, PRODUCTS["gemini_18m"])

    order_id = f"{message.message_id}_{user_id[-4:]}"
    if "pending_orders" not in data:
        data["pending_orders"] = {}

    data["pending_orders"][order_id] = {
        "user_id": user_id,
        "product_key": selected_prod_key
    }
    save_data(data)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Approve & Send", callback_data=f"appr_{order_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"rejc_{order_id}")
    )

    sender = message.from_user
    info_header = (
        f"📩 <b>አዲስ የቴሌብር ደረሰኝ ደርሷል!</b>\n\n"
        f"🆔 <b>Order ID:</b> <code>{order_id}</code>\n"
        f"👤 <b>ደንበኛ:</b> {sender.first_name} (@{sender.username or 'No Username'})\n"
        f"🔢 <b>User ID:</b> <code>{sender.id}</code>\n"
        f"📦 <b>የጠየቀው እቃ:</b> {product['name']}\n"
        f"💵 <b>ዋጋ:</b> {product['price']} ETB\n"
        "──────────────────"
    )

    if message.content_type == 'photo':
        photo_id = message.photo[-1].file_id
        bot.send_photo(ADMIN_ID, photo_id, caption=info_header, reply_markup=markup)
    else:
        bot.send_message(ADMIN_ID, f"{info_header}\n📝 <b>የላከው ጽሑፍ፦</b>\n{message.text}", reply_markup=markup)

    client_reply = (
        "✅ <b>ደረሰኝዎ በተሳካ ሁኔታ ደርሶናል!</b>\n\n"
        "📌 <b>የትዕዛዝ ማረጋገጫ እና ርክክብ ሰዓታት (የኢትዮጵያ ሰዓት አቆጣጠር)፦</b>\n"
        "• <b>ጥዋት፦</b> ከ 12:00 ሰዓት እስከ 1:10 ሰዓት\n"
        "• <b>ከሰዓት እና ማታ፦</b> ከ 10:00 ሰዓት እስከ 4:00 ሰዓት\n\n"
        "⏳ በእነዚህ የስራ ሰዓታት ውስጥ ክፍያዎ ተረጋግጦ እቃዎ ወዲያውኑ ይላክልዎታል። በትዕግስት ስለሚጠብቁን እናመሰግናለን!"
    )
    bot.reply_to(message, client_reply)

print("Bot is up and running...")
@bot.message_handler(commands=['stats'])
def get_stats(message):
    if str(message.chat.id) != ADMIN_ID:
        return
    data = load_data()
    total_users = len(data.get("users", {}))
    pending_count = len(data.get("pending_orders", {}))
    
    bot.send_message(
        ADMIN_ID,
        f"📊 <b>የቦቱ አጠቃላይ መረጃ (Stats)፦</b>\n\n"
        f"👥 <b>ቦቱን የጀመሩ ተጠቃሚዎች፦</b> {total_users} ሰው\n"
        f"⏳ <b>ያልተፈጸሙ ትዕዛዞች፦</b> {pending_count} እቃ"
    )
    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
