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
# Vocabulary contains no RTL, Arabic-joining, Mongolian, N'Ko, Syriac, or
# Hangul-jamo characters, no Indic dependent vowel signs / combining marks,
# and no supplementary-plane (surrogate-pair) characters -- all removed as
# potential sources of broken rendering around the ZWJ joiners.
SYMBOL_MAP = {
    'А': ['Å', 'ᴀ', '⍺', 'Ꭺ', 'Ꭿ', 'ᗅ', 'Ⲁ', 'ꓮ'],
    'Б': ['Ƃ'],
    'В': ['ᴃ', 'ც', 'ჩ', 'Ᏸ', 'Ᏼ', 'β', 'ᗷ', 'ᗸ', 'ᗹ', 'ᗽ', 'ᗾ', 'ᗿ', 'Ⲃ', 'ꓐ', 'ᛒ', 'ᛔ', '฿'],
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
