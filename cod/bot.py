import random
import logging
from config import TOKEN
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
import json

bot = TeleBot(TOKEN)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    logging.info("Отправка приветственного сообщения(/start)")
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, text=f"Привет, {user_name}!\n\n"
                                           f"Я бот который умеет просто отправлять мотивационны фразы. /motivational_texts",
                     reply_markup=create_keyboard(["/motivational_texts", '/help']))

@bot.message_handler(commands=['motivational_texts'])
def motivational(message):
    num = random.randint(0,10)
    with open('motivational_texts.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    random_text = random.choice(data['motivational_texts'])['text']
    user_name = message.from_user.first_name
    personalized_text = random_text.replace("{user_name}", user_name)
    logging.info(f"Отправка мотивационного сообщения(/motivational_texts)({num})")
    bot.send_message(message.chat.id, personalized_text, reply_markup=create_keyboard(["/motivational_texts", '/help']))

@bot.message_handler(commands=['help'])
def support(message):
    logging.info(f"Отправка вспомогательного сообщения(/help)")
    bot.send_message(message.chat.id, text=f"<b>Доступные команды:</b>\n"
                                           f"\t/start\n"
                                           f"\t/help\n"
                                           f"\t/motivational_texts\n\n"
                                           f"<i>Бот создал @chistiy_fun</i>",
                     reply_markup=create_keyboard(["/motivational_texts", '/help']),
                     parse_mode='HTML')

@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


logging.info("Бот запущен")
bot.polling()