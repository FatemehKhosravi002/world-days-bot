import telebot
from decouple import config

with open("name_of_the_day.txt", "r") as f:
    file = f.read()
    lines = file.splitlines()
    translated_holiday = lines[0].split("=")[1]
    translated_description = lines[1].split("=")[1]


TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(["start"])
def hello_world(message):
    bot.reply_to(message,f"{translated_holiday}-----{translated_description}")

bot.infinity_polling()