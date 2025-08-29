import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

# 🔐 Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@Master_Mystic"
CHANNEL_LINK = "https://t.me/Master_Mystic"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не установлен")

# 🌐 URL вебхука
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"

# 🛠️ Бот и диспетчер
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ——— нормализация до 1..22 ———
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

# ——— краткие описания ———
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

# ——— подробные описания ———
DETAILED_DESCRIPTIONS = {
    (18,6,6): (
        "🔮 <b>Хвост 18-6-6: Любовная магия</b>\n\n"
        "В прошлой жизни ты либо совершал любовные привороты, либо сам страдал от недостатка любви. "
        "Часто это проявлялось как сильная эмоциональная привязка, зависимость или принуждение.\n\n"
        "В этой жизни ты можешь бессознательно искать любовь вовне, не умея полюбить себя. "
        "Тебе важно одобрение других, и ты можешь быть склонен к манипуляциям через чувства.\n\n"
        "📌 <b>Задачи этого хвоста:</b>\n"
        "• Полюбить себя и научиться дарить любовь без зависимости.\n"
        "• Не циклиться только на отношениях — иначе другие сферы жизни будут страдать.\n"
        "• Пройти искушение использовать магию — и отказаться от неё.\n"
        "• Развивать интуицию и выбирать путь по внутреннему отклику, а не по выгоде.\n"
        "• Стать смелым, решительным и ответственным — только тогда жизнь начнёт выстраиваться гармонично."
    ),
    (9,9,18): (
        "🔮 <b>Хвост 9-9-18: Волшебник, магические знания</b>\n\n"
        "Ты обладал глубокими знаниями, но не передал их миру. Мог использовать их во вред или из страха быть непонятым.\n\n"
        "В этой жизни ты можешь бояться делиться своими знаниями, думая: «Мои знания никому не нужны» или «Не хочу создавать себе конкурентов».\n\n"
        "📌 <b>Задачи этого хвоста:</b>\n"
        "• Принять, что твоя душа мудра и опытна.\n"
        "• Начать делиться мудростью — через творчество, блог, хобби.\n"
        "• Помогать людям, не назидая, а делясь опытом.\n"
        "• Избавиться от страха и начать передавать знания.\n"
        "• Не закрываться в одиночестве — создать команду единомышленников."
    ),
    # ... остальные описания (сохранил все, как в предыдущем скрипте)
}

# ——— ссылки на PDF-файлы ———
PDF_LINKS = {
    (18,6,6): "https://drive.google.com/uc?export=download&id=1dM0z8LpAgNZEO2bViZXiJBQssG1MmFZh",
    (9,9,18): "https://drive.google.com/uc?export=download&id=10_7IQ-bHmJnmmzYLwpF06NDKlRhavJUV",
    (9,18,9): "https://drive.google.com/uc?export=download&id=1BBgsTpA_twkhsgAly9i3DtR6fseIMlRa",
    (18,9,9): "https://drive.google.com/uc?export=download&id=1IOKcMbpaRniLBmPL8s-anCwi1eBrr_O9",
    (6,5,17): "https://drive.google.com/uc?export=download&id=1SdzrR0vieHPZsPI4oxAynQ8KUgN2wYkK",
    (15,20,5): "https://drive.google.com/uc?export=download&id=1WC9HbCl6PfDasDX1uYM6qcF7nvFO8JcS",
    (15,5,8): "https://drive.google.com/uc?export=download&id=1krx7t8o2S8cFdp58HES9lyblQq7nfgKt",
    (3,9,12): "https://drive.google.com/uc?export=download&id=1kugwosiU6g31pPujfCZfSo9WGDouzIJ6",
    (3,12,9): "https://drive.google.com/uc?export=download&id=15pb7irKooMODIvkGacYGNQbGgngdp_w-",
    (9,12,3): "https://drive.google.com/uc?export=download&id=1QaMYUJv--n8iLwseG8_MAgz79dggEgg6",
    (15,8,11): "https://drive.google.com/uc?export=download&id=1w69XCIBm3u6XVTXJF893iL3nV_CzgaRJ",
    (9,15,6): "https://drive.google.com/uc?export=download&id=18wj_PCzN7ZEaUvfmGiDW2AttFdY15snQ",
    (6,17,11): "https://drive.google.com/uc?export=download&id=1uRuiDM-csTgk6SGweSkhbGT20yfK1kXd",
    (12,19,7): "https://drive.google.com/uc?export=download&id=12EhO882TN6FFZNkV1LV18Gzy6SGTbJaF",
    (21,4,10): "https://drive.google.com/uc?export=download&id=1RYUBW4pCeSmsXwcjjTLiWdXHWP1uud2z",
    (12,16,4): "https://drive.google.com/uc?export=download&id=161NMgmh9KDcrK0og17JrHBSloSNYvNmz",
    (3,22,19): "https://drive.google.com/uc?export=download&id=14eTveJvncg3FRsOlGqBuiDD1Vd885BcE",
    (21,10,16): "https://drive.google.com/uc?export=download&id=1t3mCNby-NCCBE4Pz_EFbuvXsJim9mpqG",
    (6,8,20): "https://drive.google.com/uc?export=download&id=1e1xcWuo1uYHDLYGJGkzhP1niun92kUUP",
    (3,7,22): "https://drive.google.com/uc?export=download&id=10R1PoK8lQbcP5fEVVXecMoLymi45tsGW",
    (9,3,21): "https://drive.google.com/uc?export=download&id=1PWq5Vf6nBrL0eZPWXJa4SmLHsdbJIoKc",
    (21,7,13): "https://drive.google.com/uc?export=download&id=10kDSS349TSu9eYaiCo61uWVjx11WOWRA",
    (18,6,15): "https://drive.google.com/uc?export=download&id=1O27XG5pSIcGbfsNSQILNTbNVdXxYbf5Z",
    (6,20,14): "https://drive.google.com/uc?export=download&id=1lPwcqfBzC9gUNdC_10QYPavb3v3N-YIS",
    (21,10,7): "https://drive.google.com/uc?export=download&id=1vl2gBjs_jQBDHakFJBsHr4uU7OaGsPnn",
    (3,13,10): "https://drive.google.com/uc?export=download&id=1unFYU8JlQPhYPmFgLlaRpDwX49TBP2WE",
    (12,18,3): "https://drive.google.com/uc?export=download&id=1vl2gBjs_jQBDHakFJBsHr4uU7OaGsPnn",
    (18,3,12): "https://drive.google.com/uc?export=download&id=1unFYU8JlQPhYPmFgLlaRpDwX49TBP2WE",
    (6,14,8): "https://drive.google.com/uc?export=download&id=1dM0z8LpAgNZEO2bViZXiJBQssG1MmFZh",
}

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

    # Кнопка "Подробное описание"
    detailed_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Подробное описание", callback_data=f"detail_{tail_triplet}")]
        ]
    )

    # Кнопка "Скачать PDF"
    pdf_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📥 Скачать PDF", callback_data=f"pdf_{tail_triplet}")]
        ]
    )

    await message.answer(
        f"🔮 <b>Твой кармический хвост:</b> {tail_triplet[0]}-{tail_triplet[1]}-{tail_triplet[2]}\n"
        f"📌 {description}\n\n"
        f"👉 Подпишись на канал: {CHANNEL_LINK}",
        reply_markup=detailed_button
    )
    await message.answer("Хочешь сохранить описание?", reply_markup=pdf_button)

@dp.message(F.text == "ℹ️ О проекте")
async def about(message: Message):
    await message.answer(
        "🔮 <b>Master Mystic</b>\n\n"
        "Разработан с любовью для тех, кто ищет глубину, смысл и магию в жизни.\n\n"
        f"Канал: <a href='{CHANNEL_LINK}'>@Master_Mystic</a>"
    )

# ——— обработка кнопки "Подробное описание" ———
@dp.callback_query(F.data.startswith("detail_"))
async def show_detailed_description(callback):
    try:
        data = callback.data.replace("detail_", "")
        cleaned = data.replace("(", "").replace(")", "")
        if ", " in cleaned:
            M, N, D = map(int, cleaned.split(", "))
        elif "-" in cleaned:
            M, N, D = map(int, cleaned.split("-"))
        else:
            M, N, D = map(int, cleaned.split())
        triplet = (M, N, D)
    except Exception as e:
        await callback.answer("❌ Ошибка при обработке данных.")
        return

    detailed = DETAILED_DESCRIPTIONS.get(triplet, "Подробное описание пока недоступно.")
    await callback.message.answer(detailed)
    await callback.answer()

# ——— обработка кнопки "Скачать PDF" ———
@dp.callback_query(F.data.startswith("pdf_"))
async def send_pdf(callback):
    try:
        data = callback.data.replace("pdf_", "")
        cleaned = data.replace("(", "").replace(")", "")
        if ", " in cleaned:
            M, N, D = map(int, cleaned.split(", "))
        elif "-" in cleaned:
            M, N, D = map(int, cleaned.split("-"))
        else:
            M, N, D = map(int, cleaned.split())
        triplet = (M, N, D)
    except Exception as e:
        await callback.answer("❌ Ошибка при обработке данных.")
        return

    pdf_url = PDF_LINKS.get(triplet)
    if pdf_url:
        await callback.message.answer(
            f"📄 Вот твой персональный PDF:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬇️ Скачать PDF", url=pdf_url)]
            ])
        )
        await callback.answer()
    else:
        await callback.answer("PDF для этого хвоста пока недоступен.")

# ——— запуск вебхука ———
async def main():
    await bot.set_webhook(WEBHOOK_URL)
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    await site.start()
    print(f"✅ Вебхук запущен на {WEBHOOK_URL}")
    try:
        await asyncio.sleep(3600)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())