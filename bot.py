# -*- coding: utf-8 -*-
import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "No token found. Set the BOT_TOKEN environment variable before running this script."
    )

# Cyrillic letter -> list of possible substitution symbols.
# One variant is picked at random for every single occurrence of a letter.
# This vocabulary is curated to avoid characters whose script shaping breaks
# when a ZWJ sits between two adjacent symbols (e.g. complex-script ligatures).
SYMBOL_MAP = {
    'А': ['Å', 'ᴀ', '⍺', 'Ꭺ', 'Ꭿ', 'ᗅ', '𐊠', '𐋎', 'Ⲁ', 'ꓮ', '𐌀', 'ᚤ'],
    'Б': ['Ƃ', 'ธ', 'ㄪ', '𐋉'],
    'В': ['ᴃ', 'ც', 'ჩ', 'Ᏸ', 'Ᏼ', 'β', 'ᗷ', 'ᗸ', 'ᗹ', 'ᗽ', 'ᗾ', 'ᗿ', '𐊡', 'Ⲃ', '𐐚', 'ꓐ', '𐊂', '𐌁', '𐰝', 'ᛒ', 'ᛔ', '฿', 'ꕗ'],
    'Г': ['┌', 'ᴤ', 'ᴦ', 'Ր', 'ⵤ', 'Ꮁ', 'ㄏ', 'ᒥ', '𐐊', '𐌲', '𐊓', '𐌐', '𐑝'],
    'Д': ['⍙', '⌂', '⊿', 'ց', 'ⵠ', 'ᗝ', '𐊣', 'ロ', '𐊅', 'ꕔ', 'ꗇ'],
    'Е': ['⋿', '℮', '∈', '⋲', 'ᴇ', 'Ꭼ', 'Ꮛ', 'દ', 'ⴹ', 'ᗴ', '𐊤', 'Ⲉ', '𐌴', 'ㅌ', 'ꓰ', '𐊆', 'ᦷ', '𐌄', '𐰏'],
    'Ё': ['Ë', '⋵', 'ݝ', 'ݞ', 'ݟ', 'ē', 'ᣯ'],
    'Ж': ['ⵣ', 'ⵥ', '𐊌', '𐋅', '𐠀', 'ᛤ', 'ᛯ', 'ꁘ', 'ꑕ'],
    'З': ['Ʒ', 'Ȝ', 'ᴈ', 'Յ', 'ჳ', 'ဒ', 'ᗱ', 'ⳅ', 'Ⳍ', 'ⳍ', 'ᦡ'],
    'И': ['ᴎ', 'ս', 'Ͷ', '𐐥', '𐑍'],
    'Й': ['й'],
    'К': ['ᛕ', 'K', 'ᴋ', 'ⴽ', 'Ꮶ', 'Ⲕ', 'ⲕ', 'ꓗ', '𐊋', '𐌊', 'ꗣ', 'ꗪ'],
    'Л': ['ᐱ', '⩘', 'ᴧ', '人', 'Ꮑ', 'Ⲗ', '𐌡', '𐌻', 'ꓥ', 'ⴷ', '𐦪', '𐊍', 'ㅅ', '𐑵'],
    'М': ['Ⅿ', 'Ꮇ', 'ꮇ', 'ᗰ', 'ᙏ', '𐊰', 'Ⱞ', '𐌼', 'ꓟ', '𐊎', '𐌑', 'ᛖ'],
    'Н': ['ዘ', 'Ꮋ', 'ਮ', 'ዞ', 'ᕼ', '𐋏', 'Ⲏ', 'ⲏ', 'ꓧ', 'ꔠ', 'ꖾ', 'ꎝ'],
    'О': ['⭘', '◯', 'ᴑ', 'ⵔ', '𐊫', '𐐄', 'ㅇ', 'ꓳ', '𐊒', '߀'],
    'П': ['∏', '⊓', '∩', 'ⲡ', 'ᴨ', 'Ⲡ', 'ᥒ'],
    'Р': ['ᴩ', '⍴', 'թ', 'ꮲ', 'ꮅ', 'ㄗ', 'ᑭ', 'ᕈ', 'Ⲣ', 'ⲣ', 'ꓑ', '𐊕', '𐌓', '𐌛'],
    'С': ['Ϲ', 'Ⅽ', '∁', 'ᴄ', 'Ⴚ', 'ꮯ', 'ꮳ', 'ꉔ', 'ㄈ', 'ᘳ', 'ᙅ', '𐊢', 'Ⲥ', 'ⲥ', 'ꓚ', '𐌂', '𐒨', '𐑤', 'ⵎ', 'ⵛ'],
    'Т': ['⊤', 'Τ', '┬', 'ᴛ', '⊺', 'ⴶ', 'ꭲ', 'ㄒ', '𐊱', 'Ꭲ', '𐏕', 'ͳ', '𐌕', 'Ͳ', 'ꓔ', '𐊗', '𐍄'],
    'У': ['Ⴘ', 'ყ', 'Ꭹ', 'Ꮍ', '𐒋'],
    'Ф': ['⌀', 'Φ', 'Փ', 'Ⴔ', 'ჶ', 'ⵀ', 'Ⲫ', 'ⲫ', '𐠗', 'Ⱇ', '𐌸', '𐌘'],
    'Х': ['✕', '✗', 'ㄨ', '𐊐', '𐌗', '᙭', '𐊴', '𐋂', 'Ⲭ', '𐰓', 'ⲭ', 'ⵝ', 'ꓫ', '𐊉', 'ᚷ', '𐍇', '𐌢'],
    'Ц': ['∪̩', 'և', 'பூ'],
    'Ч': ['Ҹ', 'Կ', 'կ', 'ㄐ', '𐋌', '𐍁'],
    'Ш': ['ա', 'Ⱎ', 'ꔗ'],
    'Щ': ['պ', '山', 'બ'],
    'Ъ': ['Ƅ', 'Ⴆ', 'Ⴊ', 'ⵒ', 'ᕹ'],
    'Ы': ['bI', 'ƄI', 'ꮟI'],
    'Ь': ['Ƅ', 'b', 'ꮟ', 'Ⱃ', 'ߕ'],
    'Э': ['℈', 'ͽ'],
    'Ю': ['ІО', 'IO', 'Iⵔ', 'Ꮊ'],
    'Я': ['ᴙ', 'ᖆ'],
}
BOT_SIGNATURE = " @MasktextBot"

# Real invisible characters (not literal escape text):
NBSP = "\u00A0"   # non-breaking space  (&nbsp;)
ZWJ = "\u200D"    # zero-width joiner   (&#8205;)


def mask_text(text: str) -> str:
    # Each item is (kind, string). kind is "vocab" for a substituted letter
    # (which may itself be a multi-character variant, e.g. "IO" or "bI" —
    # treated as one atomic unit so ZWJ is never inserted inside it),
    # or "other" for anything else (spaces, punctuation, digits, Latin letters...).
    tokens = []
    for char in text:
        if char == " ":
            # Rule: every space becomes a non-breaking space + a regular space.
            tokens.append(("other", NBSP + " "))
        else:
            upper_char = char.upper()
            if upper_char in SYMBOL_MAP:
                variant = random.choice(SYMBOL_MAP[upper_char])
                tokens.append(("vocab", variant))
            else:
                # Not a mapped Cyrillic letter -> left unchanged.
                tokens.append(("other", char))

    pieces = []
    prev_kind = None
    for kind, s in tokens:
        if prev_kind == "vocab" and kind == "vocab":
            # Rule: insert a ZWJ between two neighboring substituted symbols.
            pieces.append(ZWJ)
        pieces.append(s)
        prev_kind = kind

    pieces.append(BOT_SIGNATURE)
    return "".join(pieces)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me any text and I'll mask it with symbols! 🔒"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original_text = update.message.text
    masked = mask_text(original_text)
    await update.message.reply_text(masked)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("MasktextBot is starting...")
    app.run_polling()
