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
SYMBOL_MAP = {
    "А": ["∀", "/-\\"],
    "Б": ["Ƃ", "ɓ"],
    "В": ["Ᏼ", "ᗷ", "|3"],
    "Г": ["⎾", "┌"],
    "Д": ["⍙", "⌂"],
    "Е": ["⋿", "≡"],
    "Ё": ["Ë"],
    "Ж": ["⋈", "⌘"],
    "З": ["Ʒ", "Ȝ"],
    "И": ["Ͷ", "|/|"],
    "Й": ["Ͷ̆"],
    "К": ["ᛕ", "|{"],
    "Л": ["ᐱ", "⩘", "/\\"],
    "М": ["ᛖ", "ᗰ", "|V|"],
    "Н": ["ዘ", "Ꮋ", "|-|"],
    "О": ["⭘", "◯", "()"],
    "П": ["∏", "⊓", "┌┐", "∩"],
    "Р": ["Р", "|°"],
    "С": ["Ϲ", "(", "⊂"],
    "Т": ["⊤", "Τ", "┬"],
    "У": ["Ү", "λ"],
    "Ф": ["⌀", "Φ"],
    "Х": ["✕", "᙭", "×"],
    "Ц": ["∪̩"],
    "Ч": ["Ћ", "Ҹ"],
    "Ш": ["III", "|||"],
    "Щ": ["⫴̩"],
    "Ъ": ["Ƅ"],
    "Ы": ["bI", "Ƅ|"],
    "Ь": ["Ƅ"],
    "Э": ["∃", "Ǝ"],
    "Ю": ["ІО", "IO", "I-O", "І-О"],
    "Я": ["Ʀ", "R"],
}

BOT_SIGNATURE = " @MasktextBot"


def mask_text(text: str) -> str:
    result_chars = []
    for char in text:
        upper_char = char.upper()
        if upper_char in SYMBOL_MAP:
            variant = random.choice(SYMBOL_MAP[upper_char])
            result_chars.append(variant)
        else:
            # Not a mapped Cyrillic letter (spaces, punctuation, digits, Latin letters, etc.)
            # Left unchanged.
            result_chars.append(char)
    return "".join(result_chars) + BOT_SIGNATURE


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
