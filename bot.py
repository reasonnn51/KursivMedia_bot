import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from excel import load_employees

# Загрузка токена
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в .env")

# Инициализация бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Клавиатура
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎂 Дни рождения")],
    ],
    resize_keyboard=True
)

@dp.message(F.text.startswith("/start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Введите фамилию или email для поиска сотрудника.\n\n"
        "Нажмите кнопку ниже, чтобы посмотреть ближайшие дни рождения 🎉",
        reply_markup=keyboard
    )

@dp.message(F.text == "🎂 Дни рождения")
async def show_birthdays(message: Message):
    users = load_employees()
    today = datetime.today()
    upcoming_days = 7

    upcoming = []
    for u in users:
        birth_str = u.get("birth")
        try:
            birth_date = datetime.strptime(birth_str, "%d.%m.%Y")
            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)

            delta = (next_birthday - today).days
            if 0 <= delta <= upcoming_days:
                upcoming.append((u, next_birthday.strftime("%d.%m")))
        except:
            continue

    if not upcoming:
        await message.answer("🎉 В ближайшие 7 дней нет дней рождений.")
        return

    text = "🎂 <b>Ближайшие дни рождения:</b>\n\n"
    for user, bday in upcoming:
        text += (
            f"👤 <b>{user.get('name')}</b>\n"
            f"🎉 Дата: {bday}\n"
            f"💼 Должность: {user.get('position')}\n"
            f"📋 Отдел: {user.get('sheet')}\n\n"
        )

    await message.answer(text)

@dp.message(F.text)
async def search_employee(message: Message):
    keyword = message.text.strip().lower()
    if not keyword or len(keyword) < 2:
        await message.answer("⚠️ Введите фамилию или email.")
        return

    users = load_employees()
    results = [
        u for u in users
        if keyword in u.get("name", "").lower() or keyword in u.get("email", "").lower()
    ]

    if not results:
        await message.answer("❌ Сотрудник не найден.")
        return

    for user in results:
        text = (
            f"👤 <b>{user.get('name')}</b>\n"
            f"💼 Должность: {user.get('position')}\n"
            f"📧 Email: {user.get('email')}\n"
            f"📞 Телефон: {user.get('phone')}\n"
            f"📅 Начал работу: {user.get('start_date')}\n"
            f"🎂 День рождения: {user.get('birth')}\n"
            f"📄 Тип контракта: {user.get('contract_type')}\n"
            f"📋 Отдел: {user.get('sheet')}\n"
        )
        await message.answer(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
