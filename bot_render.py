import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, AiohttpWebhookRunner
from aiohttp import web

# 🔐 Получаем токен и ссылку на канал
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@Master_Mystic"
CHANNEL_LINK = "https://t.me/Master_Mystic"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не установлен")

# 🌐 Получаем URL сервиса (у тебя будет свой)
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"

# 🛠️ Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ——— функция нормализации ———
def norm22(n: int) -> int:
    while n > 22:
        n = sum(int(digit) for digit in str(n))
    return n

# ——— расчёт хвоста ———
def calc_tail(day: int, month: int, year: int):
    A = norm22(day)
    B = norm22(month)
    C = norm22(sum(int(d) for d in str(year)))
    D = norm22(A + B + C)
    E = norm22(A + B + C + D)
    M = norm22(D + E)
    N = norm22(M + D)
    return (M, N, D)

# ——— словарь хвостов ———
TAILS = {
    (18,6,6): "Любовная магия — опыт сильной зависимости/привязки.",
    (9,9,18): "Волшебник, магические знания — доступ к тайным знаниям.",
    (9,18,9): "Магическая жертва — тема жертвенности ради идеи/ритуала.",
    (18,9,9): "Волшебник. Отшельничество — изоляция ради знаний.",
    (6,5,17): "Гордыня — испытание славой и самоценностью.",
    (15,20,5): "Бунтарь — сопротивление установленным правилам.",
    (15,5,8): "Предательства, страсти в семье — испытания в роде.",
    (3,9,12): "Одинокая женщина — путь через одиночество и самопознание.",
    (3,12,9): "Одинокая женщина — путь через одиночество и самопознание.",
    (9,12,3): "Одинокая женщина — путь через одиночество и самопознание.",
    (15,8,11): "Физическая агрессия — работа с внутренним гневом.",
    (9,15,6): "Мир страстей и сказок — склонность к иллюзиям.",
    (6,17,11): "Загубленный талант — скрытые способности и недооценка.",
    (12,19,7): "Воин — борьба за правду и справедливость.",
    (21,4,10): "Угнетённая душа — внутренние ограничения и блоки.",
    (12,16,4): "Император — сила воли, контроль и лидерство.",
    (3,22,19): "Не рожденное дитя — кармические утраты и потери.",
    (21,10,16): "Духовный жрец — работа с внутренними знаниями и мистикой.",
    (6,8,20): "Разочарование рода — кармические ошибки предков.",
    (3,7,22): "Узник — ограничения и зависимость от обстоятельств.",
    (9,3,21): "Надзиратель — контроль и наблюдение над другими.",
    (21,7,13): "Разрушение и смерть многим душам — тяжелая карма рода.",
    (18,6,15): "Тёмный маг — сила и манипуляции энергией.",
    (6,20,14): "Душа, которую принесли в жертву — путь через жертвенность.",
    (21,10,7): "Воин веры — духовные испытания и вера.",
    (3,13,10): "Суицид — уроки через кризисы и отчаяние.",
    (12,18,3): "Физические страдания — испытания телом и духом.",
    (18,3,12): "Физические страдания — испытания телом и духом.",
    (6,14,8): "Диктатор — контроль, власть и подавление воли других.",
}

def describe_tail(triplet):
    return TAILS.get(triplet, "Неизвестный хвост")

# ——— кнопки ———
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔮 Рассчитать кармический хвост")],
        [KeyboardButton(text="ℹ️ О проекте")]
    ],
    resize_keyboard=True
)

check_sub_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_sub")]
    ]
)

# ——— команда /start ———
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Я бот <b>Master Mystic</b> 🌿\n"
        "Я рассчитываю твой <i>кармический хвост</i> по дате рождения.\n\n"
        "Но сначала — подпишись на мой канал:\n"
        f"<a href='{CHANNEL_LINK}'>@Master_Mystic</a>\n\n"
        "После подписки нажми кнопку:",
        reply_markup=check_sub_button
    )

# ——— проверка подписки ———
async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

@dp.callback_query(F.data == "check_sub")
async def handle_check_sub(callback):
    if await is_user_subscribed(callback.from_user.id):
        await callback.message.edit_text(
            "✨ Отлично! Ты подписан.\n\n"
            "Нажми кнопку ниже:",
            reply_markup=None
        )
        await callback.message.answer("Выбери действие:", reply_markup=keyboard)
    else:
        await callback.answer("❌ Подпишись и нажми снова!", show_alert=True)

@dp.message(F.text == "🔮 Рассчитать кармический хвост")
async def ask_for_date(message: Message):
    await message.answer("Введите дату: <b>ДД.ММ.ГГГГ</b>")

@dp.message(F.text.regexp(r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(\d{4})$"))
async def handle_date(message: Message):
    try:
        day, month, year = map(int, message.text.split("."))
    except:
        return
    if not (1 <= day <= 31) or not (1 <= month <= 12) or year < 1900:
        await message.reply("⚠️ Введите корректную дату.")
        return

    tail_triplet = calc_tail(day, month, year)
    description = describe_tail(tail_triplet)

    await message.answer(
        f"🔮 <b>Твой хвост:</b> {tail_triplet[0]}-{tail_triplet[1]}-{tail_triplet[2]}\n"
        f"📌 {description}\n\n"
        f"👉 {CHANNEL_LINK}"
    )

@dp.message(F.text == "ℹ️ О проекте")
async def about(message: Message):
    await message.answer(
        "🔮 <b>Master Mystic</b>\n\n"
        "Разработан с любовью для тех, кто ищет глубину, смысл и магию в жизни.\n\n"
        f"Канал: <a href='{CHANNEL_LINK}'>@Master_Mystic</a>"
    )

# ——— запуск вебхука ———
async def main():
    # Устанавливаем вебхук
    await bot.set_webhook(WEBHOOK_URL)
    # Запускаем сервер
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    runner = AiohttpWebhookRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    await site.start()
    print(f"✅ Вебхук запущен на {WEBHOOK_URL}")

if __name__ == "__main__":
    asyncio.run(main())