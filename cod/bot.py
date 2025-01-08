import random
import logging
from config import TOKEN
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup
import json
import os

# Инициализация бота с использованием токена
bot = TeleBot(TOKEN)

# Настройка логирования: записи логов сохраняются в файл log_file.txt
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

# Путь к JSON-файлу, в котором хранятся мотивационные тексты
JSON_FILE = "motivational_texts.json"

# Функция для загрузки данных из JSON-файла
# Если файл не существует, возвращается структура с пустым списком текстов
def load_json(file_path):
    if not os.path.exists(file_path):
        return {"motivational_texts": []}
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Функция для сохранения данных в JSON-файл
# Обеспечивается сохранение с читаемым форматированием
def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Функция для создания клавиатуры с кнопками
# Клавиатура создается на основе переданного списка кнопок
def create_keyboard(buttons_list):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard

# Обработчик команды /start
# Отправляет приветственное сообщение пользователю
@bot.message_handler(commands=['start'])
def start(message):
    logging.info("Пользователь {message.chat.id} использовал команду /start.")
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, text=f"Привет, {user_name}!\n\n"
                                         f"Я бот который умеет просто отправлять мотивационны фразы. /motivational_texts",
                     reply_markup=create_keyboard(["/motivational_texts", '/help']))

# Обработчик команды /motivational_texts
# Выбирает случайный текст из базы и отправляет его пользователю
@bot.message_handler(commands=['motivational_texts'])
def motivational(message):
    with open('motivational_texts.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    random_text = random.choice(data['motivational_texts'])['text']
    user_name = message.from_user.first_name
    personalized_text = random_text.replace("{user_name}", user_name)
    logging.info(f"Пользователь {message.chat.id} использовал команду (/motivational_texts)()")
    bot.send_message(message.chat.id, personalized_text, reply_markup=create_keyboard(["/motivational_texts", '/help']))

# Обработчик команды /help
# Отправляет список доступных команд пользователю
@bot.message_handler(commands=['help'])
def support(message):
    logging.info(f"Пользователь {message.chat.id} использовал команду (/help)")
    bot.send_message(message.chat.id, text=f"<b>Доступные команды:</b>\n"
                                           f"\t/start\n"
                                           f"\t/help\n"
                                           f"\t/motivational_texts\n\n"
                                           f"<i>Бот создал @chistiy_fun</i>",
                     reply_markup=create_keyboard(["/motivational_texts", '/help']),
                     parse_mode='HTML')

# Обработчик команды /ahelp
# Предназначен для отображения админских команд
@bot.message_handler(commands=['ahelp'])
def admin_support(message):
    logging.info(f"Админ {message.chat.id} использовал команду (/ahelp)")
    bot.send_message(message.chat.id, text=f"<b>Доступные админ-команды:</b>\n"
                                           f"\t/debug\n"
                                           f"\t/aadd -текст-\n"
                                           f"\t/get -номер текста-\n\n"
                                           f"<i>Главный админ @chistiy_fun</i>",
                     reply_markup=create_keyboard(["/motivational_texts", '/help']),
                     parse_mode='HTML')

# Обработчик команды /get
# Отправляет пользователю текст по его номеру из базы
@bot.message_handler(commands=["get"])
def get_motivation(message):
    try:
        logging.info(f"Получена команда /get от пользователя {message.chat.id}: {message.text}")
        command_parts = message.text.split()
        if len(command_parts) != 2 or not command_parts[1].isdigit():
            bot.reply_to(message, "Пожалуйста, укажите номер текста после команды /get. Например: /get 1")
            return

        text_number = int(command_parts[1]) - 1  # Индексация начинается с 0
        data = load_json(JSON_FILE)

        if 0 <= text_number < len(data["motivational_texts"]):
            selected_text = data["motivational_texts"][text_number]["text"]
            bot.reply_to(message, selected_text)
            logging.info(f"Отправлен текст {text_number + 1} пользователю {message.chat.id}")
        else:
            bot.reply_to(message,
                         f"Текста с номером {text_number + 1} не существует. В базе всего {len(data['motivational_texts'])} текстов.")
            logging.warning(f"Запрошен несуществующий текст {text_number + 1} пользователем {message.chat.id}")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды /get: {str(e)}")
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

# Обработчик команды /aadd
# Добавляет новый текст в базу мотивационных фраз
@bot.message_handler(commands=["aadd"])
def add_motivation(message):
    try:
        logging.info(f"Получена команда /aadd от пользователя {message.chat.id}: {message.text}")
        command_parts = message.text.split(" ", 1)
        if len(command_parts) != 2:
            bot.reply_to(message, "Пожалуйста, добавьте текст после команды /aadd. Например: /aadd Ты можешь всё!")
            logging.warning(f"Пользователь {message.chat.id} не указал текст после команды /aadd")
            return

        user_message = command_parts[1].strip()
        if not user_message:
            bot.reply_to(message, "Пустое сообщение не может быть добавлено.")
            logging.warning(f"Пользователь {message.chat.id} отправил пустое сообщение после команды /aadd")
            return

        data = load_json(JSON_FILE)
        new_entry = {"text": user_message}
        data["motivational_texts"].append(new_entry)
        save_json(JSON_FILE, data)

        bot.reply_to(message,
                     f"Ваше сообщение добавлено в базу мотивационных текстов под номером {len(data['motivational_texts'])}!")
        logging.info(f"Добавлено сообщение от пользователя {message.chat.id}: {user_message}")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды /aadd: {str(e)}")
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

# Обработчик команды /debug
# Отправляет администратору файл с логами
@bot.message_handler(commands=['debug'])
def send_logs(message):
    with open("log_file.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

# Логирование запуска бота
logging.info("Бот запущен")

# Запуск основного цикла обработки сообщений
bot.polling()
