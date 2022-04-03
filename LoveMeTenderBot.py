import telebot
import random
import TenderParser as tp
from datetime import datetime
import os

TOKEN = '5243674466:AAEpscGDckjJmf2ZBWW-sGqZcI661fyvHpM'

# Состояния диалога
STATE_START = 0
STATE_WAIT_FOR_DATE = 1
STATE_WAIT_FOR_KEYWORDS = 2
STATE_END = 3

current_state = STATE_START
input_date = ''
input_keywords = ''

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['getcompliment'])
def get_compliment_processing(message):
    global current_state
    percent = format(random.random() * 1000, '.3f')
    bot.send_message(message.chat.id,
                     f'Ты выглядишь на все {percent}%! 😍😍😍',
                     parse_mode='Markdown')
    current_state = STATE_END


@bot.message_handler(commands=['gettenders'])
def get_tenders_processing(message):
    bot.send_message(message.chat.id,
                     '➡ Введи *дату*, с которой нужно искать тендеры.\n ❗ Дата должна быть в формате *дд.мм.гггг* (пример: 01.01.2001)',
                     parse_mode='Markdown')
    global current_state
    current_state = STATE_WAIT_FOR_DATE


@bot.message_handler(func=lambda message: current_state == STATE_WAIT_FOR_DATE)
def enter_date_processing(message):
    global input_date
    input_date = message.text
    try:
        datetime.strptime(input_date, '%d.%m.%Y')
    except:
        bot.send_message(message.chat.id,
                         '🤬 Это не очень-то похоже на нормальную дату! \n↩ Посмотри на пример и попробуй ещё раз ',
                         parse_mode='Markdown')
    else:
        if datetime.strptime(input_date, '%d.%m.%Y').date() > datetime.today().date():
            bot.send_message(message.chat.id,
                             '🤬 Введённая дата не может быть больше текущей! \n↩ Попробуй ещё раз ',
                             parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id,
                             '✅ Принято! Теперь укажи поисковую фразу из описания тендера.',
                             parse_mode='Markdown')
            bot.send_message(message.chat.id,
                             'Ты можешь указать несколько поисковых фраз, разделив их символом *&* - я поищу тендеры для каждой из них и верну общий список',
                             parse_mode='Markdown')
            bot.send_message(message.chat.id,
                             'Пример: генеральный план*&*проект планировки*&*концепция',
                             parse_mode='Markdown')
            global current_state
            current_state = STATE_WAIT_FOR_KEYWORDS


@bot.message_handler(func=lambda message: current_state == STATE_WAIT_FOR_KEYWORDS)
def enter_keywords_processing(message):
    global input_keywords
    global current_state
    input_phrases = message.text.split('&')
    keywords_count = len(input_phrases)
    bot.send_message(message.chat.id,
                     f'✅ Так, введено поисковых фраз: *{keywords_count}*.\n Сейчас поищу что-ниудь, терпение... ⏱',
                     parse_mode='Markdown')
    tenders_list_html = tp.get_tenders_list(input_date, input_phrases)
    if len(tenders_list_html) == 0:
        bot.send_message(message.chat.id,
                         f'⛔ Косяк (код 1): сайт {tp.SITE_URL} вернул пустой список тендеров.\n Укажи другие параметры поиска',
                         parse_mode='Markdown')
        current_state = STATE_END
    else:
        bot.send_message(message.chat.id,
                         f'🔥 Отлично! Количество найденных тендеров: *{len(tenders_list_html)}*.\n Формирую файл... ⏱',
                         parse_mode='Markdown')
        tenders_df = tp.set_tenders_to_df(tenders_list_html)
        result_filename = tp.export_tenders_to_xls(tenders_df)
        if result_filename == '':
            bot.send_message(message.chat.id,
                             '⛔ Косяк (код 2): не удалось сформировать файл',
                             parse_mode='Markdown')
            current_state = STATE_END
        else:
            doc_to_send = open(result_filename, 'rb')
            bot.send_message(message.chat.id,
                             f'Вот твой файл со списком тендеров:',
                             parse_mode='Markdown')
            bot.send_document(message.chat.id, doc_to_send)
            doc_to_send.close()
            os.remove(result_filename)
    current_state = STATE_END


@bot.message_handler(func=lambda message: current_state == STATE_END)
def end_state_processing(message):
    bot.send_message(message.chat.id,
                     f'Ты можешь начать заново, выбрав одну из команд: /getcompliment или /gettenders',
                     parse_mode='Markdown')


bot.polling(none_stop=True)
