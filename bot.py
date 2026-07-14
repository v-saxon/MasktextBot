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
    'А': ['Å', 'ᴀ', '⍺', 'Ꭺ', 'Ꭿ', 'ᗅ', '𐊠', '𐋎', 'Ⲁ', 'ꓮ', '𐌀', 'ᚤ', 'ᥑ'],
    'Б': ['Ƃ', 'ɓ', 'ธ', 'ㄪ', '𐋉', '𐐞'],
    'В': ['ᴃ', 'ც', 'ჩ', 'Ᏸ', 'Ᏼ', 'ദ', 'ഭ', 'β', 'ᗷ', 'ᗸ', 'ᗹ', 'ᗽ', 'ᗾ', 'ᗿ', '𐊡', 'Ⲃ', '𐐚', 'ꓐ', '𐊂', '𐌁', '𐰝', 'ଓ', 'ᛒ', 'ᛔ', '฿', 'ꕗ'],
    'Г': ['┌', 'ᴤ', 'ᴦ', 'Ր', 'ⵤ', 'Ꮁ', 'ㄏ', 'ᒥ', '𐐊', '𐌲', '𐊓', '𐌐', '୮', '𐑝', 'ᥬ'],
    'Д': ['⍙', '⌂', '⊿', 'ց', 'ⵠ', 'ᗝ', '𐊣', 'ロ', '𐊅', 'ꕔ', 'ꗇ'],
    'Е': ['⋿', '℮', '∈', '⋲', 'ᴇ', 'Ꭼ', 'Ꮛ', 'દ', '𑀚', '𑁗', 'ⴹ', 'ᗴ', '𐊤', 'Ⲉ', '𐌴', 'ㅌ', 'ꓰ', '𐊆', 'ᦷ', '𐌄', '𐰏', '𐒢', 'ᛊ', 'ᥱ', 'ⵉ', 'ꗋ', 'ꗨ', 'ꘓ', 'ꏂ', 'ꑿ'],
    'Ё': ['Ë', '⋵', 'ݝ', 'ݞ', 'ݟ', 'ē', 'ᣯ'],
    'Ж': ['ⵣ', 'ⵥ', '𐊌', '𐋅', '𐠀', 'ᛤ', 'ᛯ', 'ꁘ', 'ꑕ'],
    'З': ['Ʒ', 'Ȝ', 'ᴈ', 'Յ', 'ჳ', 'ဒ', 'ᗱ', 'ⳅ', 'Ⳍ', 'ⳍ', 'ᦡ'],
    'И': ['ᴎ', 'ս', 'Ͷ', 'ͷ', '𐐥', '𐑍', 'ᱢ', 'ଥ', '𐒜', 'ᥙ', 'ᥢ'],
    'Й': ['ท', 'ห'],
    'К': ['ᛕ', 'K', 'ᴋ', 'ⴽ', 'Ꮶ', 'Ⲕ', 'ⲕ', 'ꓗ', '𐊋', '𐌊', 'ꗣ', 'ꗪ'],
    'Л': ['ᐱ', '⩘', 'ᴧ', '人', 'Ꮑ', 'ለ', '𑀕', 'Ⲗ', '𐌡', '𐌻', 'ꓥ', 'ⴷ', '𐦪', '𐊍', 'ㅅ', '𐑵', '᧘', 'ߍ'],
    'М': ['Ⅿ', 'ო', 'Ꮇ', 'ꮇ', 'က', 'ന', 'ෆ', 'ጠ', 'ᗰ', 'ᙏ', '𐊰', 'Ⱞ', '𐌼', 'ꓟ', '𐊎', 'ᱬ', '𐌑', '𐰡', 'ᛖ'],
    'Н': ['ዘ', 'Ꮋ', 'ⴼ', 'ਮ', 'ዞ', 'ᕼ', '𐋏', 'Ⲏ', 'ⲏ', 'ꓧ', 'ꔠ', 'ꖾ', 'ꎝ'],
    'О': ['⭘', '◯', 'ᴑ', 'ⵔ', 'ଠ', 'ഠ', 'ዐ', '০', '𑀞', '𐊫', 'Ⲟ', '𐐄', '០', '੦', '໐', 'ㅇ', 'ꓳ', '𐊒', 'ဝ', '႐', 'ᦞ', '߀', 'ߋ', '᱐', 'ᱛ', '𐌏', '𐰗', '୦', '𐒆', '𐑴', '౦', '๐', '࿀', 'ꄲ'],
    'П': ['∏', '⊓', '∩', 'ⲡ', 'ᴨ', 'ก', 'ㄇ', 'ᥰ', 'ㄫ', 'Ⲡ', 'ᥒ', '𐌿', '𐍀', 'ग', 'ꡫ', 'ᚢ'],
    'Р': ['ᴩ', '⍴', 'թ', 'ꮲ', 'የ', 'ꮅ', 'ㄗ', 'ᑭ', 'ᕈ', 'Ⲣ', 'ⲣ', 'ꓑ', '𐊕', 'ᱞ', '𐌓', '𐌛', '𐰙', '𐑜'],
    'С': ['Ϲ', 'Ⅽ', '∁', 'ᴄ', 'Ⴚ', 'ꮯ', 'ꮳ', 'ꉔ', 'ㄈ', '𑀗', '𑀝', 'ᘳ', 'ᙅ', '𐊢', 'Ⲥ', 'ⲥ', 'ꓚ', 'င', '𐌂', '𐒨', '𐑤', 'ᥴ', 'ⵎ', 'ⵛ'],
    'Т': ['⊤', 'Τ', '┬', 'ᴛ', '⊺', 'ⴶ', 'ꭲ', 'ፐ', 'ፕ', 'ㄒ', '𐰼', '𐊱', 'Ꭲ', '𐏕', 'ꔋ', 'ͳ', '𐌕', 'Ͳ', 'ꓔ', '𐊗', '𐍄'],
    'У': ['Ⴘ', 'ყ', 'Ꭹ', 'ឫ', 'ឬ', '𐒦', 'Ꮍ', '𐒋'],
    'Ф': ['⌀', 'Φ', 'Փ', 'Ⴔ', 'ჶ', 'ⵀ', 'क', 'ቀ', 'ዋ', 'ዎ', '𑁢', '𐊳', '𐊸', 'ᛰ', 'Ⲫ', 'ⲫ', '𐠗', 'Ⱇ', '𐌸', '𐌘'],
    'Х': ['✕', '✗', 'ㄨ', '𑀋', '𐊐', '𐌗', '᙭', '𐊴', '𐋂', 'Ⲭ', '𐰓', 'ⲭ', 'ⵝ', '𐰂', 'ꓫ', '𐊉', 'ᚷ', '𐍇', '𐌢'],
    'Ц': ['∪̩', 'և', 'பூ'],
    'Ч': ['Ҹ', 'Կ', 'կ', 'Ⴏ', 'Ⴗ', 'பு', 'ਪ', 'પ', 'મ', 'ꕪ', 'ય', 'ሃ', 'ㄐ', '౺', 'ฯ', 'ຯ', '𐋌', '𐍁', '𐰺', '୳'],
    'Ш': ['ա', 'ய', 'ധ', 'ሠ', 'Ⱎ', 'ឃ', 'យ', 'ꡆ', 'ꔗ'],
    'Щ': ['պ', 'யு', 'யூ', '山', 'ਘ', 'ખ', 'બ', 'ሣ', 'ሡ', '୴', '౻'],
    'Ъ': ['Ƅ', 'Ⴆ', 'Ⴊ', 'ⵒ', 'ᕹ'],
    'Ы': ['bI', 'ƄI', 'bI', 'bI', 'ꮟI'],
    'Ь': ['Ƅ', 'b', 'b', 'ꮟ', 'Ⱃ', 'ߕ', 'ᱠ', '𐌜'],
    'Э': ['∃', 'Ǝ', '℈', 'ͽ'],
    'Ю': ['ІО', 'IO', 'IO', 'ІО', 'Iⵔ', 'Ꮊ'],
    'Я': ['ᴙ', 'গ', 'ମ', 'এ', 'ᖆ'],
}
BOT_SIGNATURE = " @MasktextBot"

# Real invisible characters (not literal escape text):
NBSP = "\u00A0"   # non-breaking space  (&nbsp;)
ZWJ = "\u200D"    # zero-width joiner   (&#8205;)


def mask_text(text: str) -> str:
    # Each item is (kind, string). kind is "vocab" for a substituted letter,
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
