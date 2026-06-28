from bs4 import BeautifulSoup
import requests
import json
import telebot
from decouple import config

SELECT_DAY_API_KEY= config("SELECT_DAY_API_KEY")


html_text = requests.get("https://nationaltoday.com/").text
soup = BeautifulSoup(html_text, "lxml")

names = []
today_name = soup.find("h2", class_="holiday-title-text")
names.append(today_name.text)
additional_day = soup.find_all("div", class_="additional-holiday-title")
for day in additional_day:
    names.append(day.get_text(strip=True))

with open("prompt_select_best_day.txt", "r") as f:
    file = f.read()

prompt_select_best_day = file.format(
    names=names
)

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {SELECT_DAY_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "openai/gpt-oss-120b:free",
        "messages": [
            {"role": "user", "content": prompt_select_best_day}
        ]
    }
)

if response.status_code!=200:
    print("API Error")
    exit()

content = response.json()["choices"][0]["message"]["content"]

best_holiday = content.split("\n")[0]
best_holiday = best_holiday.replace("Winner:", "").strip()

print(best_holiday)
b_flag = False
url = best_holiday.lower()
if "birthday" in url:
    b_flag = True
    url = url.split("’")[0].strip()

url = url.replace(" ","-")
if not b_flag:
    url = "https://nationaltoday.com/" + url + "/"
else:
    url = "https://nationaltoday.com/birthday/" + url + "/"
print(url)


#extract individual offer for day
html_offer_text = requests.get(url).text
offer_soup = BeautifulSoup(html_offer_text, "lxml")

individual = offer_soup.find_all("h3", class_="component-subhed")
for i in individual:
    if i.text == "Individuals":
        individual_text = i.find_next("div", class_="component-content")
if not individual_text:
    individual_text = ""
    individual_text.text = ""
print(individual_text.text)


#translate name of the day and individual action to persian
with open("translate_prompt.txt", "r") as f_translate:
    file_translate = f_translate.read()

translate_prompt = file_translate.format(
    holiday_name = best_holiday,
    holiday_description = individual_text.text
)


TRANSLATE_API_KEY=config("TRANSLATE_API_KEY")
translate_response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {TRANSLATE_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "openai/gpt-oss-120b:free",
        "messages": [
            {"role": "user", "content": translate_prompt}
        ]
    }
)

if translate_response.status_code!=200:
    print("API Error")
    exit()

translated_text = translate_response.json()["choices"][0]["message"]["content"]

data = json.loads(translated_text)

translated_holiday = data["holiday"]
translated_description = data["description"]

print(translated_holiday)
print(translated_description)

#Connect to telegram bot
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

bot.message_handler(["start"])
def hello_world(message):
    bot.reply_to(message,f"{translated_holiday}-----{translated_description}")

bot.infinity_polling()