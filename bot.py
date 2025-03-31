import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from google_sheets import write_to_sheet

TOKEN = "7617871189:AAGVUK6aurtI21SuxVaO2ytKyrPc75_m2N0"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Главное меню кнопками
def main_info_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🧭 О фестивале", callback_data="info_about")
    builder.button(text="🎥 Форматы участия", callback_data="info_formats")
    builder.button(text="📅 Расписание", callback_data="info_schedule")
    builder.button(text="📤 Прислать работу", callback_data="info_submit")
    builder.button(text="🎫 Билеты и поддержка", callback_data="info_support")
    builder.button(text="❓ FAQ", callback_data="info_faq")
    builder.adjust(2)
    return builder.as_markup()

# Меню ролей
def role_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 Я Автор", callback_data="role_author")
    builder.button(text="👁 Я Зритель", callback_data="role_viewer")
    builder.button(text="🎓 Я Эксперт", callback_data="role_expert")
    builder.adjust(3)
    return builder.as_markup()

# Меню стилей музыки
def style_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎷 Джаз", callback_data="style_jazz")
    builder.button(text="🎹 Классика", callback_data="style_classic")
    builder.button(text="🎧 Электро", callback_data="style_electro")
    builder.button(text="🎸 Рок", callback_data="style_rock")
    builder.adjust(2)
    return builder.as_markup()

# Старт
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "no username"
    intro = FSInputFile("intro_video.mp4")
    await message.answer_video(video=intro, caption="🌉 Добро пожаловать на фестиваль 'Мосты между мирами'!")

    await message.answer("📍 Добро пожаловать!\nВыберите, что вас интересует:", reply_markup=main_info_menu())
    write_to_sheet(str(user_id), username, "/start")

# Обработка кнопок информации
@dp.callback_query(F.data.startswith("info_"))
async def handle_info(callback: CallbackQuery):
    text_map = {
        "info_about": "🧭 *О фестивале*\n\n«Мосты между мирами» — это международный форум, объединяющий людей и искусственный интеллект через искусство и кино. Цель — показать, что человек и ИИ могут быть друзьями и творить вместе.",
        "info_formats": "🎥 *Форматы участия*\n\n- 🎬 Автор: присылает видео или музыку, участвует в показах\n- 👁 Зритель: получает доступ к фестивалю, голосует\n- 🎓 Эксперт: помогает оценивать работы и участвует в отборе",
        "info_schedule": "📅 *Расписание*\n\n📍 Ялта, Театр имени Чехова\n🗓 1 октября 2025 года\n⏰ 18:00 — открытие, показы, концерт и награды",
        "info_submit": "📤 *Прислать работу*\n\nВыберите роль 'Автор' и отправьте видео или аудио. Бот всё запишет и сохранит ссылку в таблицу.",
        "info_support": "🎫 *Билеты и поддержка*\n\nВход свободный, но вы можете поддержать фестиваль донатом или покупкой сувениров. Подробнее — в следующем обновлении.",
        "info_faq": "❓ *FAQ*\n\n📩 Связь: fondmirotvorec@yandex.ru\n🧠 Искусственный интеллект: все ролики сделаны с его помощью\n💡 Идеи, предложения и партнёрство — пишите нам!"
    }
    key = callback.data
    await callback.message.answer(text_map[key], parse_mode="Markdown")
    await callback.answer()

# Выбор роли
@dp.callback_query(F.data.startswith("role_"))
async def selected_role(callback: CallbackQuery):
    role = callback.data.split("_")[1]
    username = callback.from_user.username or "no username"
    user_id = callback.from_user.id

    write_to_sheet(str(user_id), username, role)
    await callback.message.answer(f"✅ Вы успешно зарегистрированы как {role}. Спасибо за участие!")
    await callback.message.answer("📤 Загрузите ваше произведение (видео или аудио):")
    await callback.answer()

# Обработка медиафайлов
@dp.message(F.video | F.audio)
async def handle_media(message: Message):
    file_id = message.video.file_id if message.video else message.audio.file_id
    file = await bot.get_file(file_id)
    telegram_url = f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"

    username = message.from_user.username or "no username"
    user_id = message.from_user.id
    write_to_sheet(str(user_id), username, telegram_url)

    await message.answer("✅ Ваш файл успешно загружен и сохранён! Спасибо за участие.")

    # 🎁 Песня
    song = FSInputFile("song.mp3")
    await message.answer_audio(audio=song, caption="🎁 Вот ваша персональная песня в подарок!")

    # Разрешение на подписку
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, присылайте!", callback_data="yes_songs")
    builder.button(text="❌ Нет, спасибо", callback_data="no_songs")
    await message.answer("Хотите ли вы получать новые AI-песни раз в неделю?", reply_markup=builder.as_markup())

# Подписка
@dp.callback_query(F.data.in_(["yes_songs", "no_songs"]))
async def song_permission(callback: CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or "no username"

    if callback.data == "yes_songs":
        write_to_sheet(str(user_id), username, "✅ Разрешил подписку")
        await callback.message.answer("Спасибо! Вы будете получать песни раз в неделю.")
        await callback.message.answer("Выберите любимый стиль:", reply_markup=style_menu())
    else:
        write_to_sheet(str(user_id), username, "❌ Отказ от подписки")
        await callback.message.answer("Хорошо! Если передумаете — просто напишите 'песня'.")
    await callback.answer()

# Выбор стиля
@dp.callback_query(F.data.startswith("style_"))
async def selected_style(callback: CallbackQuery):
    style = callback.data.split("_")[1]
    user_id = callback.from_user.id
    username = callback.from_user.username or "no username"

    write_to_sheet(str(user_id), username, f"🎵 Стиль: {style}")
    await callback.message.answer(f"Ваш стиль — {style}! Мы учтём это при следующих песнях 🎶")
    await callback.answer()

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
