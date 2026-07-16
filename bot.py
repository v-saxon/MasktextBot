# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

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
NBSP = "\u00A0"
ZWJ = "\u200D"   # zero-width joiner
WJ = "\u2060"    # word joiner
CGJ = "\u034F"   # combining grapheme joiner

LOGS = {}

def log_message(user_id, username, user_input, bot_output):
    if user_id not in LOGS:
        LOGS[user_id] = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] @{username}\nInput:  {user_input}\nOutput: {bot_output}\n"
    LOGS[user_id].append(log_entry)

def _random_separator():
    """
    Randomly choose one of four separator combinations:
    1. WJ + ZWJ + WJ
    2. WJ
    3. WJ + CGJ + WJ
    4. WJ + CGJ + ZWJ + WJ
    """
    choice = random.randint(1, 4)
    if choice == 1:
        return WJ + ZWJ + WJ
    elif choice == 2:
        return WJ
    elif choice == 3:
        return WJ + CGJ + WJ
    else:  # choice == 4
        return WJ + CGJ + ZWJ + WJ

def _add_separators_inside_variant(variant):
    """
    If variant has 2+ characters, add invisible separators between them.
    Example: "bI" -> "b<SEP>I"
    """
    if len(variant) < 2:
        return variant
    
    chars = list(variant)
    result = [chars[0]]
    for char in chars[1:]:
        result.append(_random_separator())
        result.append(char)
    return "".join(result)

def _make_variant_picker():
    pools = {}
    last_used = {}
    def next_variant(letter):
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
        # Add separators inside multi-character variants
        variant = _add_separators_inside_variant(variant)
        return variant
    return next_variant

def mask_text(text):
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
    await update.message.reply_text("Send me any text to mask it! 🔒\n/logs - see your logs\n/clear - clear logs")

async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in LOGS or not LOGS[user_id]:
        await update.message.reply_text("No logs yet.")
        return
    all_logs = "\n".join(LOGS[user_id])
    if len(all_logs) > 4000:
        for i in range(0, len(all_logs), 4000):
            await update.message.reply_text(all_logs[i:i+4000])
    else:
        await update.message.reply_text(all_logs)

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in LOGS:
        LOGS[user_id] = []
    await update.message.reply_text("Logs cleared.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        original_text = update.message.text
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or "unknown"
        masked = mask_text(original_text)
        log_message(user_id, username, original_text, masked)
        await update.message.reply_text(masked)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Error processing message")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("MasktextBot is running...")
    app.run_polling()
