# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "No token found. Set the BOT_TOKEN environment variable before running this script."
    )

# Cyrillic letter -> list of possible substitution symbols.
SYMBOL_MAP = {
    'А': ['Å', 'ᴀ', '⍺', 'Ꭺ', 'Ꭿ', 'ᗅ', 'Ⲁ', 'ꓮ'],
    'Б': ['Ƃ'],
    'В': ['ᴃ', 'ች', 'ჩ', 'Ᏸ', 'Ᏼ', 'β', 'ᗷ', 'ᗸ', 'ᗹ', 'ᗽ', 'ᗾ', 'ᗿ', 'Ⲃ', 'ꓐ', 'ᛒ', 'ᛔ', '฿'],
    'Г': ['┌', 'ᴤ', 'ᴦ', 'Ր', 'ⵤ', 'Ꮁ', 'ㄏ', 'ᒥ'],
    'Д': ['⍙', '⌂', '⊿', 'ց', 'ⵠ', 'ᗝ', 'ロ'],
    'Е': ['⋿', '℮', '∈', '⋲', 'ᴇ', 'Ꭼ', 'Ꮛ', 'દ', 'ⴹ', 'ᗴ', 'Ⲉ', 'ㅌ', 'ꓰ', 'ᦷ'],
    'Ё': ['Ë', '⋵', 'ē', 'ᣯ'],
    'Ж': ['ⵣ', 'ⵥ', 'ᛤ', 'ᛯ', 'ꁘ'],
    'З': ['Ʒ', 'Ȝ', 'ᴈ', 'Յ', 'ჳ', 'ဒ', 'ᗱ', 'ⳅ', 'Ⳍ', 'ⳍ', 'ᦡ'],
    'И': ['ᴎ', 'ս', 'Ͷ'],
    'Й': ['й'],
    'К': ['ᛕ', 'K', 'ᴋ', 'ⴽ', 'Ꮶ', 'Ⲕ', 'ⲕ', 'ꓗ', 'ꗣ'],
    'Л': ['ᐱ', '⩘', 'ᴧ', '人', 'Ꮑ', 'Ⲗ', 'ꓥ', 'ⴷ', 'ㅅ'],
    'М': ['Ⅿ', 'Ꮇ', 'ꮇ', 'ᗰ', 'ᙏ', 'Ⱞ', 'ꓟ', 'ᛖ'],
    'Н': ['ዘ', 'Ꮋ', 'ਮ', 'ዞ', 'ᕼ', 'Ⲏ', 'ⲏ', 'ꓧ', 'ꔠ', 'ꖾ'],
    'О': ['⭘', 'ᴑ', 'ⵔ', 'ㅇ'],
    'П': ['∏', '⊓', '∩', 'ⲡ', 'ᴨ', 'Ⲡ', 'ᥒ'],
    'Р': ['ᴩ', '⍴', 'թ', 'ꮲ', 'ꮅ', 'ㄗ', 'ᑭ', 'ᕈ', 'Ⲣ', 'ⲣ', 'ꓑ'],
    'С': ['Ϲ', 'Ⅽ', '∁', 'ᴄ', 'Ⴚ', 'ꮯ', 'ꮳ', 'ꉔ', 'ㄈ', 'ᘳ', 'ᙅ', 'Ⲥ', 'ⲥ', 'ꓚ', 'ⵎ', 'ⵛ'],
    'Т': ['⊤', '┬', 'ᴛ', 'ⴶ', 'ꭲ', 'ㄒ', 'ͳ', 'ꓔ'],
    'У': ['ყ', 'Ꭹ', 'Ꮍ'],
    'Ф': ['⌀', 'Φ', 'Փ', 'Ⴔ', 'ჶ', 'ⵀ', 'Ⲫ', 'ⲫ', 'Ⱇ'],
    'Х': ['✕', '✗', 'ㄨ', '᙭', 'Ⲭ', 'ⲭ', 'ⵝ', 'ꓫ', 'ᚷ'],
    'Ц': ['և'],
    'Ч': ['Ҹ', 'Կ', 'կ', 'ㄐ'],
    'Ш': ['ա', 'Ⱎ', 'ꔗ'],
    'Щ': ['պ', '山', 'બ'],
    'Ъ': ['Ƅ', 'Ⴆ', 'Ⴊ', 'ⵒ', 'ᕹ'],
    'Ы': ['bI', 'ƄI', 'ꮟI'],
    'Ь': ['Ƅ', 'b', 'ꮟ', 'Ⱃ'],
    'Э': ['℈', 'ͽ'],
    'Ю': ['ІО', 'IO', 'Iⵔ', 'Ꮊ'],
    'Я': ['ᴙ', 'ᖆ'],
}

BOT_SIGNATURE = " @MasktextBot"

# Real invisible characters (not literal escape text):
NBSP = "\u00A0"   # non-breaking space   (&nbsp;)
ZWJ = "\u200D"    # zero-width joiner    (&#8205;)
WJ = "\u2060"     # word joiner

# Logs in memory: {user_id: [log entries]}
LOGS = {}

def log_message(user_id: str, username: str, user_input: str, bot_output: str):
    """Log user input and bot output to memory."""
    if user_id not in LOGS:
        LOGS[user_id] = []
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] @{username}\nInput:  {user_input}\nOutput: {bot_output}\n"
    LOGS[user_id].append(log_entry)


def _random_separator() -> str:
    if random.random() < 0.5:
        return ZWJ
    if random.random() < 0.5:
        return WJ + ZWJ
    return ZWJ + WJ


def _make_variant_picker():
    pools = {}
    last_used = {}

    def next_variant(letter: str) -> str:
        variants = SYMBOL_MAP[letter]
        pool = pools.get(letter)

        if not pool:
            pool = variants[:]
            random.shuffle(pool)
            if len(pool) > 1 and pool[0] == last_used.get(letter):
                swap_idx = random.randint(1, len(pool) - 1)
                pool[0], pool[swap_idx] = pool[swap_idx], pool[0]
            pools[letter] = pool

        variant = pool.pop(0)
        last_used[letter] = variant
        return variant

    return next_variant


def mask_text(text: str) -> str:
    next_variant = _make_variant_picker()

    tokens = []
    for char in text:
        if char == " ":
            tokens.append(("other", NBSP + " "))
        else:
            upper_char = char.upper()
            if upper_char in SYMBOL_MAP:
                variant = next_variant(upper_char)
                tokens.append(("vocab", variant))
            else:
                tokens.append(("other", char))

    pieces = []
    prev_kind = None
    for kind, s in tokens:
        if prev_kind == "vocab" and kind == "vocab":
            pieces.append(_random_separator())
        pieces.append(s)
        prev_kind = kind

    pieces.append(BOT_SIGNATURE)
    return "".join(pieces)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me any text and I'll mask it with symbols! 🔒\n\n"
        "Commands:\n"
        "/logs - see your conversation history\n"
        "/clear - delete your logs"
    )


async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send user their logs."""
    user_id = str(update.effective_user.id)
    
    if user_id not in LOGS or not LOGS[user_id]:
        await update.message.reply_text("No logs yet.")
        return
    
    # Combine all logs into one message
    all_logs = "\n".join(LOGS[user_id])
    
    # If too long, send in chunks
    if len(all_logs) > 4000:
        # Send in multiple messages
        for i in range(0, len(all_logs), 4000):
            chunk = all_logs[i:i+4000]
            await update.message.reply_text(f"```\n{chunk}\n```", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"```\n{all_logs}\n```", parse_mode="Markdown")


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear user's logs."""
    user_id = str(update.effective_user.id)
    
    if user_id in LOGS:
        LOGS[user_id] = []
    
    await update.message.reply_text("Your logs have been cleared.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original_text = update.message.text
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "unknown"
    
    masked = mask_text(original_text)
    
    # Log to memory
    log_message(user_id, username, original_text, masked)
    
    await update.message.reply_text(masked)


def run_http_server():
    """Run a simple Flask server for health check."""
    app = Flask(__name__)
    
    port = int(os.environ.get("PORT", 8080))

    @app.route("/health")
    def health():
        return "OK", 200

    print(f"Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)


def run_telegram_bot():
    """Run the Telegram bot in a background thread."""
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("MasktextBot is starting...")
    app.run_polling()


if __name__ == "__main__":
    # Start Telegram bot in a background thread
    telegram_thread = Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    print("Telegram bot started in background")
    
    # Run Flask on main thread (Railway requires this)
    run_http_server()
