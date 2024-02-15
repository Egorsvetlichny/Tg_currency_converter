import random
import logging

import telebot
import requests

from config import tg_api_token, outer_api_token
from console_logger import logger

bot = telebot.TeleBot(tg_api_token)


@bot.message_handler(commands=['start'])
def start_func(message):
    bot.send_message(message.chat.id,
                     'Привет! Я бот для конвертации валют!\n'
                     'Используй команду /help, чтобы посмотреть, что я умею!')

    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = ['/start', '/help', '/info', '/bye', '/convert']
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, 'Или сразу выберите соответствующую команду: ', reply_markup=keyboard)

    user = message.from_user
    logger.info("Пользователь %s начал диалог.", user.first_name)


@bot.message_handler(commands=['info'])
def info_func(message):
    bot.send_message(message.chat.id, 'Безусловно, сначала логичнее прочитать инструкцию, спасибо за это! '
                                      'Итак, как ты уже знаешь, я бот для конвертации валют. '
                                      'Чтобы конвертировать валюту тебе неободихмо использовать команду /convert. '
                                      'Для этого напиши мне сообщение в формате: '
                                      '/convert <сумма> <из валюты> to <в валюту>')

    user = message.from_user
    logger.info("Пользователь %s воспользовался справкой.", user.first_name)


@bot.message_handler(commands=['convert'])
def convert_func(message):
    user = message.from_user

    args = message.text.split()[1:]

    if len(args) != 4:
        bot.reply_to(message, "Неверный формат команды! Используйте: /convert <сумма> <из валюты> to <в валюту>")
        logger.info("Пользователь %s неверно использовал команду /convert.", user.first_name)
        return
    else:
        amount = args[0]
        from_currency = args[1].upper()
        to_currency = args[3].upper()

        response = requests.get(
            f'https://openexchangerates.org/api/latest.json?app_id={outer_api_token}&base={from_currency}')
        data = response.json()

        if response.status_code == 200:
            if to_currency in data['rates']:
                converted_amount = float(amount) * float(data['rates'][to_currency])
                bot.reply_to(message, f"По текущему курсу {amount} {from_currency} = {converted_amount} {to_currency}")
                logger.info("Пользователь %s успешно конвертировал валюту.", user.first_name)
            else:
                bot.reply_to(message, "Неверный код валюты")
                logger.info("Пользователь %s неверно указал валюту.", user.first_name)
        else:
            bot.reply_to(message, "Не удалось получить данные о курсах валют")
            logger.info("Пользователь %s пытался конвертировать валюту.", user.first_name)


@bot.message_handler(commands=['bye'])
def bye_func(message):
    bot.send_message(message.chat.id,
                     'Спасибо, что использовал меня, увидимся! В следующий раз я конвертирую для тебя весь мир!')

    user = message.from_user
    logger.info("Пользователь %s попрощался с ботом.", user.first_name)


@bot.message_handler(commands=['help'])
def help_func(message):
    help_message = "Список доступных команд:\n\n" \
                   "/start - старт бота;\n" \
                   "/help - Вывести список команд;\n" \
                   "/info - Получить информацию о боте;\n" \
                   "/bye - Попрощаться с ботом;\n" \
                   "/convert - Конвертировать валюту."
    bot.send_message(message.chat.id, help_message)

    user = message.from_user
    logger.info("Пользователь %s воспользовался функцией помощи.", user.first_name)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user = message.from_user

    text = message.text.lower()

    if 'привет' in text or 'здравствуй' in text or 'хай' in text or 'салют' in text:
        bot.reply_to(message, "Привет! Безумно рад тебя видеть!")
        logger.info("Пользователь %s поздоровался.", user.first_name)
    elif 'пока' in text or 'до свидания' in text or 'увидимся' in text or 'до скорого' in text:
        bot.reply_to(message, "Пока! Приходи ещё!")
        logger.info("Пользователь %s попрощался.", user.first_name)
    elif 'как дела' in text or 'как настроение' in text:
        bot.reply_to(message, "Лучше всех! А вы как?")
        logger.info("Пользователь %s спросил, как дела.", user.first_name)
    elif 'что ты умеешь' in text or 'что ты можешь' in text or 'помощь' == text or 'help' == text:
        help_func(message)
        logger.info("Пользователь %s спросил, о функционале бота.", user.first_name)
    else:
        responses = ['Не понимаю, о чем ты!', 'Ну что за ерунда?', 'Используй встроенные команды!',
                     'Не, не, это не ко мне', 'А для кого подсказка была по функционалу!?',
                     'Используй команду "/help"', 'Хватит писать белиберду!']
        response = random.choice(responses)
        bot.send_message(message.chat.id, response)
        logger.info("Пользователь %s отправил сообщение: %s", user.first_name, message.text)


if __name__ == '__main__':
    bot.polling()
    logging.shutdown()
