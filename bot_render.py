from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

# Токен бота прямо в коде (твой)
BOT_TOKEN = "8219556396:AAGOHmQR1tVrcE4h_V1Nb-B56AthpWXECKE"

# Ссылка на канал для подписки
CHANNEL_LINK = "https://t.me/MasterMystic"

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ——— нормализация до 1..22 ———
def norm22(n: int) -> int:
    while n > 22:
        n = sum(int(d) for d in str(n))
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

# ——— простой словарь хвостов ———
TAILS = {
    (18,6,6): "Любовная магия — опыт сильной зависимости/привязки.",
    (9,9,18): "Волшебник, магические знания — доступ к тайным знаниям.",
    (9,18,9): "Магическая жертва — тема жертвенности ради идеи/ритуала.",
    (18,9,9): "Волшебник. Отшельничество — изоляция ради знаний.",
    (6,5,17): "Гордыня — испытание славой и самоценностью.",
    # Можно добавить остальные хвосты по твоему списку
}

def describe_tail(triplet):
    return TAILS.get(triplet, "Неизвестный хвост — описание пока отсутствует.")

# ——— команды бота ———
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Я бот Master Mystic 🌿\n"
        "Я могу рассчитать твой кармический хвост.\n\n"
        "Используй команду:\n"
        "/tail ДД.ММ.ГГГГ — чтобы узнать свой хвост.\n"
    )

@dp.message(Command("tail"))
async def tail_command(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Укажи дату в формате: /tail ДД.ММ.ГГГГ")
        return
    try:
        day, month, year = map(int, parts[1].split("."))
    except:
        await message.reply("Неверный формат. Используй: ДД.ММ.ГГГГ")
        return

    tail_triplet = calc_tail(day, month, year)
    description = describe_tail(tail_triplet)
    await message.answer(
        f"Твой кармический хвост: {tail_triplet[0]}-{tail_triplet[1]}-{tail_triplet[2]}\n"
        f"{description}\n\n"
        f"Если хочешь получать ещё больше знаний и магических подсказок — подпишись на мой канал: {CHANNEL_LINK}"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
