import os
import requests
import json
from dotenv import load_dotenv
import telebot
import mysql.connector


load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
api_url = "https://perompak7samudra.vercel.app/api"

def searchMovie(movieName):
    url = api_url+"/search?query=" + movieName + "&providers[]=PusatFilm"
    response = requests.get(url)
    data = response.json()
    return data

def detailMovie(movieLink):
    url = api_url + "/get?link=" + movieLink + "/&provider=PusatFilm"
    print(url)
    response = requests.get(url)
    data = response.json()
    return data

def cleanLink(link):
    return link.replace("/api/get?link=","").replace("/&provider=PusatFilm","")

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['search'])
def search(message):
    movieName = message.text.replace("/search ", "")
    data = searchMovie(movieName)
    data5 = data[:5]

    # send message photo and title
    # when user click the message, call detailMovie function
    for i in data5:
        # sample_string_bytes = i['link'].replace("/api/get?link=","").replace("/&provider=PusatFilm","").encode("ascii") 
  
        # base64_bytes = base64.b64encode(sample_string_bytes) 
        # base64_string = base64_bytes.decode("ascii") 
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text="Link Stream 🎥", callback_data="/detail",kwargs={"test":"test"}))
        bot.send_photo(message.chat.id, i['thumb'], caption="<a href='"+i['link']+"'>"+i['title']+"</a>",  reply_markup=markup,parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    
    if call.data.startswith("/detail"):
        # print(call.text)
        print(call.message)
        # message_text = call.message.caption
        # link = message_text.split("\n")[1]
        # link = call.text.replace("https://perompak7samudra.vercel.app/api/get?link=","").replace("/&provider=PusatFilm","")
        # data = detailMovie(link)
        
        # if "episode" in data:
        #     markup = telebot.types.InlineKeyboardMarkup()
        #     for e in data['episode']:
        #         print("/detail "+e['link'])
        #         markup.add(telebot.types.InlineKeyboardButton(text=e['title'], callback_data="/detail",url="https://perompak7samudra.vercel.app"+e['link']))
        #     bot.send_message(call.message.chat.id, data['title'] + "Episode : ", reply_markup=markup,parse_mode="Markdown")
        # else:
        #     linkMessage = "Link Streaming : \n"
        #     for s in data['stream']:
        #         linkMessage += "["+s['title']+"](https://perompak7samudra.vercel.app"+s['detail']+")\n\n"
        #     bot.send_message(call.message.chat.id,  linkMessage, parse_mode="Markdown")
        

bot.infinity_polling()