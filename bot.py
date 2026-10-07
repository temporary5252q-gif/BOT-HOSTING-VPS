import os
import sqlite3
import telebot
from telebot import types
import psutil
import datetime
import os
BOT_TOKEN = os.getenv("BOT_TOKEN", "8725316740:AAExIlgkDYgAM5fAKHwHl5LSCdKW3M8d4sk")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8600343127")
()
OWNER_USERNAME = "@KRUTIKCYBER_DEVELOPER_4"
BRAND_NAME = "KRUTIK CYBER DEVELOPER"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- DATABASE SETUP ---
DB_FILE = "master_network.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Plans Table
    c.execute('''CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specs TEXT,
        validity_days INTEGER
    )''')
    # Users & Provisioning Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        banned INTEGER DEFAULT 0,
        active_plan TEXT,
        node_id TEXT,
        server_power INTEGER DEFAULT 1,
        expiry_date TEXT
    )''')
    # Tickets Table
    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        plan_id INTEGER,
        details TEXT,
        status TEXT DEFAULT 'PENDING'
    )''')
    conn.commit()
    conn.close()

init_db()

# --- HELPER FUNCTIONS ---
def is_banned(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT banned FROM users WHERE user_id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    return res and res[0] == 1

def is_admin(user_id):
    return user_id == ADMIN_ID

# --- USER MENUS ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton("📦 View Plans", callback_data="u_plans")
    b2 = types.InlineKeyboardButton("🎟 My Tickets", callback_data="u_tickets")
    b3 = types.InlineKeyboardButton("🖥 Buy Custom VPS", callback_data="u_custom_vps")
    b4 = types.InlineKeyboardButton("📊 System Status", callback_data="u_status")
    b5 = types.InlineKeyboardButton("👨‍💻 Contact Owner", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}")
    markup.add(b1, b2)
    markup.add(b3, b4)
    markup.add(b5)
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = message.from_user.id
    if is_banned(uid):
        bot.reply_to(message, f"<b>[{BRAND_NAME}]</b>\n🚫 Your access has been restricted by Admin Desk.")
        return

    uname = message.from_user.username or "Anonymous"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (uid, uname))
    conn.commit()
    conn.close()

    text = (
        f"<b>⚡ {BRAND_NAME} | CLOUD HOSTING DESK</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Dedicated 24/7 Telegram Bot Hosting engine par aapka swagat hai.\n"
        f"High-Speed Isolated VPS aur Zero Downtime.\n\n"
        f"Neeche diye gaye options se navigate karein:"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("u_"))
def handle_user_callbacks(call):
    uid = call.from_user.id
    if is_banned(uid):
        bot.answer_callback_query(call.id, "Account Suspended.", show_alert=True)
        return

    data = call.data

    if data == "u_main":
        bot.edit_message_text(
            f"<b>⚡ {BRAND_NAME} | CLOUD HOSTING DESK</b>\n━━━━━━━━━━━━━━━━━━━━━━\nNeeche diye gaye options se navigate karein:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )

    elif data == "u_plans":
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, name, specs, validity_days FROM plans")
        plans = c.fetchall()
        conn.close()

        if not plans:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="u_main"))
            bot.edit_message_text("Abhi koi active plans uplabdh nahi hain. Kripya thodi der baad dekhein.", call.message.chat.id, call.message.message_id, reply_markup=markup)
            return

        markup = types.InlineKeyboardMarkup()
        for p in plans:
            markup.add(types.InlineKeyboardButton(f"🎟 {p[1]} ({p[3]} Days)", callback_data=f"book_{p[0]}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="u_main"))

        bot.edit_message_text(
            f"<b>📦 {BRAND_NAME} AVAILABLE PLANS</b>\n━━━━━━━━━━━━━━━━━━━━━━\nApna preferred plan select karein ticket raise karne ke liye:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    elif data == "u_custom_vps":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 Direct Deal with Owner", url=f"https://t.me/{OWNER_USERNAME.replace('@', '')}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="u_main"))
        text = (
            f"<b>🖥 {BRAND_NAME} | CUSTOM DEDICATED VPS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Agar aapko:\n"
            f"• Full Root SSH & Dedicated Resources chahiye\n"
            f"• Custom RAM, Cores aur Locations pasand hain\n"
            f"• Heavy production scraping ya bots chalane hain\n\n"
            f"Toh direct hamare Founder se connect karein:\n"
            f"👉 <b>{OWNER_USERNAME}</b>"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data == "u_status":
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="u_main"))
        text = (
            f"<b>📊 {BRAND_NAME} | NETWORK METRICS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 Network Status: <b>OPTIMAL (100% UP)</b>\n"
            f"⚙️ Central Core Load: <b>{cpu}%</b>\n"
            f"🧠 RAM Allocation: <b>{ram.percent}% Used</b>\n"
            f"🔒 Sandboxing Engine: <b>ACTIVE (Isolated)</b>"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data == "u_tickets":
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, plan_id, status FROM tickets WHERE user_id = ?", (uid,))
        ticks = c.fetchall()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="u_main"))
        if not ticks:
            bot.edit_message_text("Aapki koi active ticket nahi hai.", call.message.chat.id, call.message.message_id, reply_markup=markup)
            return

        msg_body = f"<b>🎟 YOUR TICKETS ({BRAND_NAME})</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
        for t in ticks:
            msg_body += f"• Ticket #{t[0]} | Plan ID: {t[1]} | Status: <b>{t[2]}</b>\n"
        bot.edit_message_text(msg_body, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("book_"))
def handle_ticket_create(call):
    plan_id = int(call.data.split("_")[1])
    uid = call.from_user.id
    uname = call.from_user.username or "Anonymous"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tickets (user_id, username, plan_id, details) VALUES (?, ?, ?, ?)",
              (uid, uname, plan_id, "User requested via Plan Desk"))
    tid = c.lastrowid
    conn.commit()
    conn.close()

    bot.answer_callback_query(call.id, f"Ticket #{tid} generated!")
    bot.edit_message_text(
        f"✅ <b>Ticket #{tid} Created Successfully!</b>\n\n"
        f"Aapki request review desk par bhej di gayi hai. Admin approval milte hi aapko server access assign ho jayega.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=main_menu()
    )

    # Admin Alert
    adm_text = (
        f"🚨 <b>NEW TICKET RECEIVED (#{tid})</b>\n"
        f"User: @{uname} (ID: <code>{uid}</code>)\n"
        f"Plan ID: {plan_id}\n"
    )
    adm_markup = types.InlineKeyboardMarkup()
    adm_markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"adm_app_{tid}_{uid}_{plan_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"adm_rej_{tid}_{uid}")
    )
    bot.send_message(ADMIN_ID, adm_text, reply_markup=adm_markup)

# --- ADMIN PANEL & COMMANDS ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id):
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton("➕ Add Plan", callback_data="adm_plan_add")
    b2 = types.InlineKeyboardButton("❌ Remove Plan", callback_data="adm_plan_rem")
    b3 = types.InlineKeyboardButton("⚡ User Control (ON/OFF/BAN)", callback_data="adm_user_ctrl")
    b4 = types.InlineKeyboardButton("📊 System Metrics", callback_data="adm_metrics")
    markup.add(b1, b2)
    markup.add(b3, b4)

    bot.reply_to(message, f"<b>⚡ {BRAND_NAME} | ADMIN DESK</b>\nChoose an administrative action:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin_callbacks(call):
    if not is_admin(call.from_user.id):
        return

    data = call.data

    if data.startswith("adm_app_"):
        parts = data.split("_")
        tid, uid, pid = parts[2], int(parts[3]), int(parts[4])

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE tickets SET status = 'APPROVED' WHERE id = ?", (tid,))
        exp = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        c.execute("UPDATE users SET active_plan = ?, server_power = 1, expiry_date = ? WHERE user_id = ?", (f"Plan-{pid}", exp, uid))
        conn.commit()
        conn.close()

        bot.answer_callback_query(call.id, f"Ticket #{tid} Approved!")
        bot.send_message(uid, f"🎉 <b>Ticket #{tid} APPROVED!</b>\nYour Dedicated Server slot is active. Contact Admin for Bot Link.")
        bot.edit_message_text(f"✅ Ticket #{tid} approved for User {uid}", call.message.chat.id, call.message.message_id)

    elif data.startswith("adm_rej_"):
        parts = data.split("_")
        tid, uid = parts[2], int(parts[3])

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE tickets SET status = 'REJECTED' WHERE id = ?", (tid,))
        conn.commit()
        conn.close()

        bot.answer_callback_query(call.id, f"Ticket #{tid} Rejected!")
        bot.send_message(uid, f"❌ <b>Ticket #{tid} was rejected by Admin Desk.</b>")
        bot.edit_message_text(f"❌ Ticket #{tid} rejected.", call.message.chat.id, call.message.message_id)

    elif data == "adm_plan_add":
        msg = bot.send_message(call.message.chat.id, "Send plan details in format:\n<code>Name|Specs|ValidityDays</code>\nExample: <code>Turbo Node|2GB Dedicated RAM|30</code>")
        bot.register_next_step_handler(msg, process_add_plan)

    elif data == "adm_plan_rem":
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, name FROM plans")
        plans = c.fetchall()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        for p in plans:
            markup.add(types.InlineKeyboardButton(f"🗑 {p[1]}", callback_data=f"delplan_{p[0]}"))
        bot.edit_message_text("Select plan to delete:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data == "adm_user_ctrl":
        msg = bot.send_message(call.message.chat.id, "Enter target Telegram User ID:")
        bot.register_next_step_handler(msg, process_user_query)

    elif data == "adm_metrics":
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        bot.send_message(
            call.message.chat.id,
            f"<b>📊 FULL ADMIN SYSTEM METRICS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"CPU Utilization: {cpu}%\n"
            f"RAM Usage: {ram.used // (1024*1024)}MB / {ram.total // (1024*1024)}MB ({ram.percent}%)\n"
            f"Disk Space: {disk.free // (1024*1024*1024)}GB Free out of {disk.total // (1024*1024*1024)}GB\n"
        )

def process_add_plan(message):
    try:
        parts = message.text.split("|")
        name = parts[0].strip()
        specs = parts[1].strip()
        days = int(parts[2].strip())
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO plans (name, specs, validity_days) VALUES (?, ?, ?)", (name, specs, days))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"✅ Plan '{name}' added successfully!")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to parse: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("delplan_"))
def delete_plan_cb(call):
    pid = int(call.data.split("_")[1])
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM plans WHERE id = ?", (pid,))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, "Plan deleted!")
    bot.edit_message_text("Plan successfully removed.", call.message.chat.id, call.message.message_id)

def process_user_query(message):
    try:
        t_uid = int(message.text.strip())
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT user_id, username, banned, server_power, active_plan FROM users WHERE user_id = ?", (t_uid,))
        u = c.fetchone()
        conn.close()

        if not u:
            bot.reply_to(message, "User not found in system.")
            return

        markup = types.InlineKeyboardMarkup(row_width=2)
        power_btn = types.InlineKeyboardButton("🔴 Turn OFF Server" if u[3] == 1 else "🟢 Turn ON Server", callback_data=f"togg_pow_{t_uid}_{u[3]}")
        ban_btn = types.InlineKeyboardButton("🚫 Ban User" if u[2] == 0 else "🟢 Unban User", callback_data=f"togg_ban_{t_uid}_{u[2]}")
        markup.add(power_btn, ban_btn)

        bot.reply_to(
            message,
            f"<b>User Control Panel</b>\n"
            f"User ID: <code>{u[0]}</code>\n"
            f"Username: @{u[1]}\n"
            f"Plan: {u[4] or 'None'}\n"
            f"Power State: {'🟢 ON' if u[3] == 1 else '🔴 OFF'}\n"
            f"Ban Status: {'🚫 Banned' if u[2] == 1 else '🟢 Active'}",
            reply_markup=markup
        )
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("togg_"))
def handle_user_toggles(call):
    parts = call.data.split("_")
    action, t_uid, curr_val = parts[1], int(parts[2]), int(parts[3])
    new_val = 0 if curr_val == 1 else 1

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if action == "pow":
        c.execute("UPDATE users SET server_power = ? WHERE user_id = ?", (new_val, t_uid))
        conn.commit()
        bot.answer_callback_query(call.id, f"Server Power set to {'ON' if new_val == 1 else 'OFF'}")
        if new_val == 0:
            bot.send_message(t_uid, f"<b>[{BRAND_NAME}]</b>\n⚠️ Your dedicated hosting server has been temporarily paused by Admin Desk.")
        else:
            bot.send_message(t_uid, f"<b>[{BRAND_NAME}]</b>\n✅ Your dedicated hosting server has been resumed.")
    elif action == "ban":
        c.execute("UPDATE users SET banned = ? WHERE user_id = ?", (new_val, t_uid))
        conn.commit()
        bot.answer_callback_query(call.id, f"User {'Banned' if new_val == 1 else 'Unbanned'}")
    conn.close()
    bot.edit_message_text("User configuration state updated successfully.", call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    print(f"[{BRAND_NAME}] Master Bot Started Successfully.")
    bot.infinity_polling(skip_pending=True)
