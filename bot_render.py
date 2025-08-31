import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# 🔐 Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не установлен в переменных окружения")

# 🌐 URL вебхука (Render)
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"

# 🛠️ Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🛠️ Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# 👤 Твой ID
ADMIN_ID = 1030370280

# Хранение пользователей, которые нажали "ГОТОВО"
waiting_for_date = set()

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
    (3,22,19): "Не рождённое дитя — кармические утраты и потери.",
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
        "В прошлой жизни ты либо совершал любовные привороты, либо сам страдал от недостатка любви. "
        "Часто это проявлялось как сильная эмоциональная привязка, зависимость или принуждение.\n\n"
        "В этой жизни ты можешь бессознательно искать любовь вовне, не умея полюбить себя. "
        "Тебе важно одобрение других, и ты можешь быть склонен к манипуляциям через чувства.\n\n"
        "❗ <b>Задачи этого хвоста:</b>\n"
        "• Полюбить себя и научиться дарить любовь без зависимости.\n"
        "• Не циклиться только на отношениях — иначе другие сферы жизни будут страдать.\n"
        "• Пройти искушение использовать магию — и отказаться от неё.\n"
        "• Развивать интуицию и выбирать путь по внутреннему отклику, а не по выгоде.\n"
        "• Стать смелым, решительным и ответственным — только тогда жизнь начнёт выстраиваться гармонично."
    ),
    (9,9,18): (
        "Ты обладал глубокими знаниями, но не передал их миру. Мог использовать их во вред или из страха быть непонятым.\n\n"
        "В этой жизни ты можешь бояться делиться своими знаниями, думая: «Мои знания никому не нужны» или «Не хочу создавать себе конкурентов».\n\n"
        "❗ <b>Задачи этого хвоста:</b>\n"
        "• Принять, что твоя душа мудра и опытна.\n"
        "• Начать делиться мудростью — через творчество, блог, хобби.\n"
        "• Помогать людям, не назидая, а делясь опытом.\n"
        "• Избавиться от страха и начать передавать знания.\n"
        "• Не закрываться в одиночестве — создай команду единомышленников."
    ),
    # ... остальные описания
}

# ——— ссылки на PDF ———
PDF_LINKS = {
    (18,6,6): "https://drive.google.com/file/d/10R1PoK8lQbcP5fEVVXecMoLymi45tsGW/view?usp=drive_link",
    (9,9,18): "https://drive.google.com/file/d/1QaMYUJv--n8iLwseG8_MAgz79dggEgg6/view?usp=drive_link",
    # ... остальные
}

# ——— кнопки ———
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сделать полный анализ")],
        [KeyboardButton(text="Подписаться на канал Master Mystic")]
    ],
    resize_keyboard=True
)

subscribe_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться", url="https://t.me/Master_Mystic")]
    ]
)

# ——— команда /start ———
@dp.message(Command("start"))
async def start(message: Message):
    logger.info(f"Пользователь {message.from_user.id} начал чат")
    await message.answer(
        "Привет! Я — бот <b>Master Mystic</b> 🌿\n\n"
        "Я помогу рассчитать твой <i>Кармический хвост</i> и узнать главные задачи души, которые ты притащил(а) из прошлой жизни. Что мешает тебе двигаться вперёд.\n\n"
        "Это бесплатно.\n\n"
        "Введите дату рождения в формате <b>ДД.ММ.ГГГГ</b>",
        reply_markup=start_keyboard
    )

# ——— обработчик "Подписаться" ———
@dp.message(F.text == "Подписаться на канал Master Mystic")
async def subscribe(message: Message):
    await message.answer(
        "🔹 Подписывайся на канал, где я делюсь:\n"
        "• Кейсами клиентов\n"
        "• Энергетикой камней\n"
        "• Как менять жизнь через матрицу судьбы\n\n"
        "Будет интересно!",
        reply_markup=subscribe_button
    )

# ——— обработчик "Сделать полный анализ" ———
@dp.message(F.text == "Сделать полный анализ")
async def full_analysis(message: Message):
    payment_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Продолжить", callback_data="pay")],
            [InlineKeyboardButton(text="⏸ Я подумаю", callback_data="think")]
        ]
    )
    await message.answer(
        "<b>Отлично! В полном анализе ты узнаешь:</b>\n"
        "● Денежный код\n"
        "● Призвание и путь души\n"
        "● Кармические задачи\n"
        "● Зоны силы и слабости\n\n"
        "<b>💲 Полный анализ по Матрице судьбы будет стоить 1000₽.</b>\n\n"
        "Это не гадание, это анализ по дате рождения. Хочешь получить? Жми «Продолжить» — и я пришлю реквизиты для оплаты. После оплаты — в течение 24 часов пришлю подробный расчёт.",
        reply_markup=payment_button
    )

# ——— обработка "Продолжить" ———
@dp.callback_query(F.data == "pay")
async def send_payment_info(callback):
    payment_info = (
        "💳 <b>Реквизиты для оплаты:</b>\n\n"
        "Сбербанк: <code>4276 5400 2708 8180</code>\n\n"
        "После оплаты нажми кнопку <b>ГОТОВО</b> — и я пришлю расчёт."
    )
    ready_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ ГОТОВО", callback_data="ready")]
        ]
    )
    await callback.message.edit_text(payment_info, reply_markup=ready_button, parse_mode="HTML")

# ——— обработка "ГОТОВО" ———
@dp.callback_query(F.data == "ready")
async def send_contact(callback):
    waiting_for_date.add(callback.from_user.id)
    await callback.message.edit_text(
        "Пожалуйста, введите вашу дату рождения в формате <b>ДД.ММ.ГГГГ</b> (например, 15.04.1990):",
        reply_markup=None,
        parse_mode="HTML"
    )

# ——— обработка ввода даты после "ГОТОВО" ———
@dp.message(F.text)
async def process_date(message: Message):
    if message.from_user.id not in waiting_for_date:
        return

    try:
        day, month, year = map(int, message.text.split("."))
    except:
        await message.reply("⚠️ Ошибка формата даты. Введите в формате ДД.ММ.ГГГГ.")
        return

    if not (1 <= day <= 31) or not (1 <= month <= 12) or year < 1900:
        await message.reply("⚠️ Введите корректную дату.")
        return

    waiting_for_date.discard(message.from_user.id)

    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Новый клиент: {message.from_user.full_name}\n"
                 f"Юзернейм: @{message.from_user.username or 'нет'}\n"
                 f"Дата рождения: {day}.{month}.{year}"
        )
        logger.info(f"Данные отправлены админу: {day}.{month}.{year}")
    except Exception as e:
        logger.error(f"Не удалось отправить админу: {e}")
        await message.answer("❌ Ошибка отправки данных. Пожалуйста, напишите мне в личные сообщения.")

    await message.answer(
        "Спасибо за доверие 🙏. В течение 24 часов я пришлю вам результат. "
        "Если у вас будут вопросы, пишите в личные сообщения <a href='https://t.me/Mattrehka'>Master Mystic</a>",
        parse_mode="HTML"
    )

# ——— ОСНОВНОЙ ОБРАБОТЧИК ДАТЫ (бесплатный анализ) ———
@dp.message(F.text.regexp(r"^(\d{2})\.(\d{2})\.(\d{4})$"))
async def handle_date(message: Message):
    if message.from_user.id in waiting_for_date:
        return

    try:
        day, month, year = map(int, message.text.split("."))
    except:
        await message.reply("⚠️ Ошибка формата даты. Введите в формате ДД.ММ.ГГГГ.")
        return

    if not (1 <= day <= 31) or not (1 <= month <= 12) or year < 1900:
        await message.reply("⚠️ Введите корректную дату.")
        return

    tail_triplet = calc_tail(day, month, year)
    description = describe_tail(tail_triplet)
    detailed_text = DETAILED_DESCRIPTIONS.get(tail_triplet, "Подробное описание пока недоступно.")

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Читать подробности", url=PDF_LINKS.get(tail_triplet, "#"))],
            [InlineKeyboardButton(text="✅ Я прочитал — сделать полный анализ", callback_data="full_analysis")]
        ]
    )

    await message.answer(
        f"🔮 <b>Твой кармический хвост:</b> {tail_triplet[0]}-{tail_triplet[1]}-{tail_triplet[2]}\n"
        f"📌 {description}\n\n"
        f"{detailed_text}",
        reply_markup=inline_keyboard
    )

# ——— обработка "Я прочитал — сделать полный анализ" ———
@dp.callback_query(F.data == "full_analysis")
async def callback_full_analysis(callback):
    payment_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Продолжить", callback_data="pay")],
            [InlineKeyboardButton(text="⏸ Я подумаю", callback_data="think")]
        ]
    )
    await callback.message.edit_text(
        "<b>Отлично! В полном анализе ты узнаешь:</b>\n"
        "● Денежный код\n"
        "● Призвание и путь души\n"
        "● Кармические задачи\n"
        "● Зоны силы и слабости\n\n"
        "<b>💲 Полный анализ по Матрице судьбы будет стоить 1000₽.</b>\n\n"
        "Это не гадание, это анализ по дате рождения. Хочешь получить? Жми «Продолжить» — и я пришлю реквизиты для оплаты. После оплаты — в течение 24 часов пришлю подробный расчёт.",
        reply_markup=payment_button
    )

# ——— запуск бота ———
async def main():
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler

    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(WEBHOOK_URL)
            logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
        else:
            logger.info(f"✅ Webhook уже установлен: {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"❌ Ошибка при установке webhook: {e}")

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    await site.start()
    logger.info("🚀 Бот запущен и слушает webhook")

    try:
        await asyncio.sleep(3600)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
