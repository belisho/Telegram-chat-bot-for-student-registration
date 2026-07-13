"""All user-facing text and option lists for the MHSS-KIDDS bot.

Keeping every message in one place makes the bot easy to translate and edit
without touching the handler logic. Use ``.format(...)`` for placeholders.
"""
from __future__ import annotations

# --- General / start ---
WELCOME = (
    "🙏 እንኳን ወደ <b>መሠረተ ሕይወት ሰንበት ት/ቤት የክረምት አብነት ትምህርት መመዝገቢያ እና መረጃ መጠየቂያ Chat bot</b> በደህና መጡ!\n"
)

DESCRIPTIVE_TEXT = (
    "<b>የመሠረተ ሕይወት ሰንበት ትምህርት ቤት 2018 ዓ.ም</b>"
)

# Shown on /start with the live registration count. Values are bold.
REGISTERED_COUNT = "📊 ለማስተማር የምንቀበለው ተማሪ ብዛት <b>{limit}</b> ሲሆን እስካሁን ባለው <b>{count}</b> ተማሪዎች ተመዝግበዋል።"

HELP = (
    "<b>Available commands</b>\n"
    "/start - Show the welcome screen and check a student's status\n"
    "/register - Register a new student\n"
    "/status - Check a student's registration status by name\n"
    "/cancel - Cancel the current operation\n"
    "/help - Show this help message"
)

# --- Name search / status ---
ASK_NAME = (
    "<b>እባክዎ መመዝገብዎን እና የተመደቡበትን ክፍል ለማረጋገጥ የመጀመሪያ ስምዎን ያስገቡ!</b>\n"
    "<blockquote><b>ማሳሰቢያ፡</b> መጀመሪያ ሲመዘገቡ የተጠቀሙትን ቋንቋ ተጠቅመው ያስገቡ።</blockquote>"
   )

INVALID_NAME = (
    "⚠️ የገባው ስም ትክክል አይደለም። እባክዎ ቢያንስ የመጀመሪያ ስም ያስገቡ።\n"
)

SEARCHING = "🔎 እየፈለግን ነው..."

MATCHES_FOUND = (
    "የሚከተሉት ተመሳሳይ ስሞች ተገኝተዋል። እባክዎ የእርስዖን ስም ይምረጡ!\n"
)

NO_MATCHES = (
    "ተመሳሳይ ስም አልተገኘም። ምን አልባት የተመዘገቡት በ English alphabet ከሆነ እንደገና ይሞክሩ!\n"
)

REGISTER_NEW_BUTTON = "➕ አዲስ ተማሪ ለመመዝገብ"

STUDENT_DETAILS = (
    "✅ <b>የተማሪ መረጃ</b>\n\n"
    "👤 <b>ሙሉ ስም:</b> {full_name}\n"
    "📚 <b>የትምህርት ደረጃ: </b> {education}\n"
    "🏫 <b>የተመደበበት ክፍል / Assigned class:</b> {assigned_class}"
    "<blockquote><b>መረጃ፡</b> \n ትምህርቱ ከሀምሌ 06 ጀምሮ ዘወትር ከሰኞ እስከ አርብ ከቀኑ 8፡00 እስከ 10፡00 ይሰጣል።</blockquote>"
)

STUDENT_DETAILS_MISSING = "አልተሟላም!"

# --- Registration form ---
LIMIT_EXCEEDED = (
    "🚫 ይቅርታ! የምዝገባ ቁጥር ገደብ ({limit}) ደርሷል። አዲስ ምዝገባ በአሁኑ ጊዜ አይቻልም።\n"
)

REG_START = (
    "📝 <b>የተማሪ ምዝገባ</b>\n"
    "በማንኛውም ጊዜ ለማቋረጥ /cancel ይጫኑ።\n"
)

ASK_FIRST_NAME = "1️⃣ የመጀመሪያ ስም ያስገቡ:"
ASK_FATHER_NAME = "2️⃣ የአባት ስም ያስገቡ:"
ASK_PHONE = (
    "3️⃣ ስልክ ቁጥር ያስገቡ:\n"
    "(e.g. 0912345678, 0712345678, +251912345678)"
)
ASK_AGE = "4️⃣ ዕድሜ ያስገቡ (7-16):"
ASK_EDUCATION = "5️⃣ የትምህርት ደረጃ ይምረጡ:"
ASK_WAITING_FAMILY = "6️⃣ ከትምህርት በኋላ ቤተሰብ ይጠብቃሉ?"

INVALID_FIRST_NAME = "⚠️ እባክዎ ትክክለኛ ስም ያስገቡ።"
INVALID_FATHER_NAME = "⚠️ እባክዎ ትክክለኛ የአባት ስም ያስገቡ።"
INVALID_PHONE = (
    "⚠️ ስልክ ቁጥሩ ትክክል አይደለም። / Invalid phone number.\n"
)
INVALID_AGE = (
    "⚠️ ዕድሜው ከ7 እስከ 16 መሆን አለበት።"
)
INVALID_EDUCATION = "⚠️ እባክዎ ከዝርዝሩ ውስጥ ይምረጡ።"

# Waiting-family options.
WAITING_FAMILY_YES = "አዎ "
WAITING_FAMILY_NO = "አይ "

REG_CONFIRMATION = (
    "🎉 <b>ምዝገባው በተሳካ ሁኔታ ተጠናቋል!</b>\n"
    "👤 <b>ሙሉ ስም:</b> {first_name} {father_name}\n"
    "📞 <b>ስልክ:</b> {phone}\n"
    "🎂 <b>ዕድሜ:</b> {age}\n"
    "📚 <b>የትምህርት ደረጃ :</b> {education}\n"
    "👨‍👩‍👧 <b>ከትምህርት በኋላ ቤተሰብ ይጠብቃሉ?:</b> {waiting_family}\n\n"
    "እናመሰግናለን!"
    "<blockquote><b>መረጃ፡</b> \n ትምህርቱ ከሀምሌ 06 ጀምሮ ዘወትር ከሰኞ እስከ አርብ ከቀኑ 8፡00 እስከ 10፡00 ይሰጣል።</blockquote>"
)


# --- Post-cancel / main menu ---
CANCELLED = "❌ ተሰርዟል።"
CHOOSE_ACTION = "<b> ክንውኑ ተሰርዟል።</b> \n ምን ማድረግ ይፈልጋሉ? እባክዎ ይምረጡ"
MENU_PROMPT = "<b>ምን ማድረግ ይፈልጋሉ? እባክዎ ይምረጡ!</b>"
BTN_TO_REGISTER = "📝 ለመመዝገብ / To register"
BTN_REGISTRATION_STATUS = "🔎 የምዝገባ ሁኔታ ለማረጋገጥ/ Registration status"
BTN_CANCEL = "❌ አቋርጥ"

GENERIC_ERROR = (
    "⚠️ አንድ ስህተት ተከስቷል። እባክዎ ቆይተው እንደገና ይሞክሩ።\n"
)

SHEET_ERROR = (
    "⚠️ ከመረጃ ቋቱ ጋር መገናኘት አልተቻለም። እባክዎ ቆይተው እንደገና ይሞክሩ።\n"
    "Could not reach the data store. Please try again later."
)

# --- Level of education options (edit freely) ---
EDUCATION_LEVELS: list[str] = [
"ጀማሪ",
"ነአኩተከ",
"አቡነ ዘበሰማያት",
"ጸሎተ ሃይማኖት",
"ቅዱስ ቅዱስ",
"ስብኀት",
"ጸሎተ እግዝዕትነ ማርያም",
"ውዳሴማርያም ዘሰኑይ",
"ውዳሴማርያም ዘሰሉስ",
"ውዳሴማርያም ዘረቡዕ",
"ውዳሴማርያም ዘሐሙስ",
"ውዳሴማርያም ዘአርብ",
"ውዳሴማርያም ዘቀዳሚት ሰንበት",
"ውዳሴማርያም ዘሰንበተ ክርስቲያን",
"አንቀጸ ብርሐን",
"ይዌድስዋ መላእክት",
"መልክዓ ማርያም",
"መልክዓ ኢየሱስ",
"መዝሙረ ዳዊት",
"ሌላ"
]
