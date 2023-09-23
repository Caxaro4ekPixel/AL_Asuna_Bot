from aiogram.filters.callback_data import CallbackData


class CallbacksTitle(CallbackData, prefix="title"):
    id: int
