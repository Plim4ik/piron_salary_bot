from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ContentTypeFilter

async def save_excel_file(message: types.Message, state: FSMContext):
    # Здесь должна быть логика сохранения присланного файла Excel
    await message.document.download("Excel/" + message.document.file_name)
    await message.reply("Файл сохранен!")

def register_handlers(dp):
    dp.register_message_handler(save_excel_file, content_types=ContentTypeFilter(content_types=types.ContentType.DOCUMENT))
