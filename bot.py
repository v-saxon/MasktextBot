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
# Vocabulary contains no RTL, Arabic-joining, Mongolian, N'Ko, Syriac, or
# Hangul-jamo characters, no Indic dependent vowel signs / combining marks,
# and no supplementary-plane (surrogate-pair) characters.
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
# Letters whose substituted symbol may get a prefix marker inserted right before it.
# Group 1: random choice of one of these three marks, or nothing at all.
PREFIX_GROUP_1 = {"И", "В", "К", "Ы", "Ь", "Ш"}
PREFIX_GROUP_1_MARKS = ["⁝", "⁚", "ˌ", ""]

# Group 2: always one of these two marks (never blank).
PREFIX_GROUP_2 = {"Н", "Ч", "Ж"}
PREFIX_GROUP_2_MARKS = ["ˉ", "ˈ"]


def _prefix_for(letter: str) -> str:
    if letter in PREFIX_GROUP_1:
        return random.choice(PREFIX_GROUP_1_MARKS)
    if letter in PREFIX_GROUP_2:
        return random.choice(PREFIX_GROUP_2_MARKS)
    return ""


BOT_SIGNATURE = " @MasktextBot"

# Real invisible characters (not literal escape text):
NBSP = "\u00A0"   # non-breaking space   (&nbsp;)
ZWJ = "\u200D"    # zero-width joiner    (&#8205;)
WJ = "\u2060"     # word joiner


def _random_separator() -> str:
    """
    Separator placed between two neighboring substituted symbols.
    Always contains a ZWJ. On top of that, a WORD JOINER (U+2060) is thrown
    in at random -- sometimes before the ZWJ, sometimes after, sometimes
    not at all.
    """
    if random.random() < 0.5:
        return ZWJ  # WJ not added this time
    if random.random() < 0.5:
        return WJ + ZWJ
    return ZWJ + WJ


def _make_variant_picker():
    """
    Returns a function next_variant(letter) that, for a single mask_text()
    call, cycles through that letter's substitution symbols in random order
    without repeating one until every variant has been used at least once.
    Once a full cycle is exhausted, it reshuffles and starts a new cycle,
    only making sure the first pick of the new cycle isn't the same symbol
    that just finished the previous cycle (when more than one variant exists).
    """
    pools = {}       # letter -> list of variants still unused in this cycle
    last_used = {}   # letter -> most recently used variant for that letter

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

    # Each item is (kind, string). kind is "vocab" for a substituted letter
    # (which may itself be a multi-character variant, e.g. "IO" or "bI" —
    # treated as one atomic unit so separators are never inserted inside it),
    # or "other" for anything else (spaces, punctuation, digits, Latin letters...).
    tokens = []
    for char in text:
        if char == " ":
            # Rule: every space becomes a non-breaking space + a regular space.
            tokens.append(("other", NBSP + " "))
        else:
            upper_char = char.upper()
            if upper_char in SYMBOL_MAP:
                variant = next_variant(upper_char)
                prefix = _prefix_for(upper_char)
                tokens.append(("vocab", prefix + variant))
            else:
                # Not a mapped Cyrillic letter -> left unchanged.
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
