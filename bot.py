# -*- coding: utf-8 -*-
import os
import random
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, InlineQueryHandler, filters

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
WJ = "\u2060"

# Public URL to the avatar image used as the inline-result thumbnail.
# Telegram requires a publicly reachable URL here (a file_id does NOT work).
# On Railway a public domain is exposed via RAILWAY_PUBLIC_DOMAIN; we serve
# avatar.png ourselves (see serve_avatar) and build the URL from that domain.
# Both the URL and the listening port can be overridden via env vars.
AVATAR_FILENAME = "avatar.png"
PORT = int(os.environ.get("PORT", "8080"))
_RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN")

AVATAR_URL = os.environ.get("AVATAR_URL") or (
    f"https://{_RAILWAY_DOMAIN}/{AVATAR_FILENAME}" if _RAILWAY_DOMAIN else None
)

LOGS = {}

def log_message(user_id, username, user_input, bot_output):
    if user_id not in LOGS:
        LOGS[user_id] = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] @{username}\nInput:  {user_input}\nOutput: {bot_output}\n"
    LOGS[user_id].append(log_entry)

def split_message(text, max_chars=4000):
    """
    Split text into chunks that fit Telegram's 4096 char limit.
    Returns list of message chunks.
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Try splitting by newlines first
    if "\n" in text:
        for line in text.split("\n"):
            if len(current_chunk) + len(line) + 1 <= max_chars:
                current_chunk += line + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip())
                current_chunk = line + "\n"
    else:
        # No newlines, split character by character while respecting max_chars
        for char in text:
            if len(current_chunk) + len(char) <= max_chars:
                current_chunk += char
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = char
    
    if current_chunk:
        chunks.append(current_chunk.rstrip())
    
    return chunks if chunks else [text]

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
            pieces.append(WJ)
        pieces.append(s)
        prev_kind = kind
    pieces.append(BOT_SIGNATURE)
    return "".join(pieces)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 Masktext\n\n"
        "How to use:\n"
        "1. In any chat, type: @masktextbot your text\n"
        "2. Select masked result from dropdown\n"
        "3. Masked text will be sent!\n\n"
        "Commands:\n"
        "/direct <text> - mask text directly\n"
        "/logs - see your conversation history\n"
        "/clear - delete your logs"
    )

async def direct_mask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct masking - /direct <text>"""
    if not context.args:
        await update.message.reply_text("Usage: /direct <text to mask>")
        return
    text = " ".join(context.args)
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "unknown"
    masked = mask_text(text)
    log_message(user_id, username, text, masked)
    
    # Split if too long
    chunks = split_message(masked)
    for chunk in chunks:
        await update.message.reply_text(chunk)

async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent logs that fit in one message"""
    user_id = str(update.effective_user.id)
    if user_id not in LOGS or not LOGS[user_id]:
        await update.message.reply_text("No logs yet.")
        return
    
    # Show only recent logs that fit in 3500 chars (safe margin for 4096 limit)
    max_chars = 3500
    logs = LOGS[user_id]
    
    # Start from the end (most recent) and build backwards
    result = []
    total_len = 0
    
    for entry in reversed(logs):
        if total_len + len(entry) + 1 <= max_chars:
            result.insert(0, entry)
            total_len += len(entry) + 1
        else:
            break
    
    if not result:
        # Even one entry is too long, just take the most recent
        result = [logs[-1]]
    
    output = "".join(result)
    if len(logs) > len(result):
        output += f"\n... (showing last {len(result)} of {len(logs)} entries)"
    
    await update.message.reply_text(output)

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear user's logs"""
    user_id = str(update.effective_user.id)
    if user_id in LOGS:
        LOGS[user_id] = []
    await update.message.reply_text("Logs cleared.")

class _AvatarHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler that serves only avatar.png (plus a health check)."""

    def do_GET(self):
        if self.path in ("/", "/health", "/healthz"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        if self.path.split("?", 1)[0] == f"/{AVATAR_FILENAME}":
            try:
                with open(AVATAR_FILENAME, "rb") as f:
                    data = f.read()
            except OSError:
                self.send_error(404, "avatar not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_error(404, "not found")

    def log_message(self, *args):
        pass  # silence per-request stderr logging

def serve_avatar():
    """Start a background HTTP server that exposes avatar.png publicly."""
    server = ThreadingHTTPServer(("0.0.0.0", PORT), _AvatarHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"🖼️ Avatar server listening on port {PORT}")

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline queries: @masktextbot query"""
    query = update.inline_query.query
    
    if not query:
        return
    
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "unknown"
    masked = mask_text(query)
    log_message(user_id, username, query, masked)
    
    # Split if too long
    chunks = split_message(masked)
    results = []
    
    for i, chunk in enumerate(chunks):
        result = InlineQueryResultArticle(
            id=f"masked_{i}",
            title="🔐 Press to send",
            description=f"{chunk[:80]}{'...' if len(chunk) > 80 else ''}" + 
                       (f" ({i+1}/{len(chunks)})" if len(chunks) > 1 else ""),
            input_message_content=InputTextMessageContent(chunk),
            thumbnail_url=AVATAR_URL
        )
        results.append(result)
    
    await update.inline_query.answer(results, cache_time=0)

if __name__ == "__main__":
    serve_avatar()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("direct", direct_mask))
    app.add_handler(CommandHandler("logs", cmd_logs))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(InlineQueryHandler(inline_query))
    print("🔐 Masktext Bot is running...")
    app.run_polling()
