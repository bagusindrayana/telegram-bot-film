import os
import requests
import json
from dotenv import load_dotenv
import telebot
import mysql.connector
from flask import Flask,request
app = Flask(__name__)


load_dotenv()

ENV = os.environ.get('ENV')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_NAME = os.environ.get('DB_NAME')

mydb = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME
)

if mydb.is_connected():
    print("Berhasil terhubung ke database")

def getHistoryById(id):
    mycursor = mydb.cursor()
    sql = "SELECT * FROM history_film WHERE id = %s"
    val = (id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchone()
    return myresult

def getHistoryByLink(link):
    mycursor = mydb.cursor()
    sql = "SELECT * FROM history_film WHERE link = %s"
    val = (link,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchone()
    return myresult

def insertHistory(link,message_id):
    cek = getHistoryByLink(link)
    if cek is None:
        mycursor = mydb.cursor()
        sql = "INSERT INTO history_film (link, message_id) VALUES (%s, %s)"
        val = (link,message_id)
        mycursor.execute(sql, val)
        mydb.commit()
        return mycursor.lastrowid
    else:
        return cek[0]

# data = getHistoryByLink("https://pusatfilm21.vip/tv/one-piece-2")
# print(data[1])
# exit()
bot = telebot.TeleBot(BOT_TOKEN)
api_url = "https://perompak7samudra.vercel.app/api"

def searchMovie(movieName):
    url = api_url+"/search?query=" + movieName + "&providers[]=PusatFilm"
    response = requests.get(url)
    data = response.json()
    return data

def detailMovie(movieLink):
    url = api_url + "/get?link=" + movieLink + "/&provider=PusatFilm"
    response = requests.get(url)
    data = response.json()
    return data

def cleanLink(link):
    return link.replace("/api/get?link=","").replace("/&provider=PusatFilm","")

@bot.message_handler(commands=['start', 'hello','help'])
def send_welcome(message):
    bot.reply_to(message, """
Selamat datang di bot PusatFilm
Ketik /search <judul film> untuk mencari film
""")

@bot.message_handler(commands=['search'])
def search(message):
    movieName = message.text.replace("/search ", "")
    data = searchMovie(movieName)
    data5 = data[:5]

    # send message photo and title
    # when user click the message, call detailMovie function
    for i in data5:
        link = cleanLink(i['link'])
        id = insertHistory(link,message.id)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text="Link Stream 🎥", callback_data="/detail "+str(id)))
        bot.send_photo(message.chat.id, i['thumb'], caption=i['title'],  reply_markup=markup,parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    
    if call.data.startswith("/detail"):
        # print(call.text)
        id = call.data.replace("/detail ","")
        print("ID : "+str(id))
        history = getHistoryById(id)
        print(history)
        link = history[1]
        
        # message_text = call.message.caption
        # link = message_text.split("\n")[1]
        # link = call.text.replace("https://perompak7samudra.vercel.app/api/get?link=","").replace("/&provider=PusatFilm","")
        data = detailMovie(link)
        
        if "episode" in data:
            markup = telebot.types.InlineKeyboardMarkup()
            for e in data['episode']:
                link = cleanLink(e['link'])
                id = insertHistory(link,call.message.id)
                markup.add(telebot.types.InlineKeyboardButton(text="Eps "+e['title'], callback_data="/detail "+str(id)))
            bot.send_message(call.message.chat.id, data['title'] + "Episode : ", reply_markup=markup,parse_mode="Markdown")
        else:
            linkMessage = "Link Streaming "+data['title']+" : \n"
            markup = telebot.types.InlineKeyboardMarkup()
            for s in data['stream']:
                markup.add(telebot.types.InlineKeyboardButton(text=s['title'], url="https://perompak7samudra.vercel.app"+s['detail']))
                # linkMessage += "["+s['title']+"](https://perompak7samudra.vercel.app"+s['detail']+")\n\n"
            bot.send_message(call.message.chat.id,  linkMessage, reply_markup=markup,parse_mode="Markdown")
        

if ENV != "production":
    bot.infinity_polling()
else:
    WEB_PORT = os.environ.get('WEB_PORT', '5000')
    WEB_URL = os.environ.get('WEB_URL')
    HOOK_URL = WEB_URL + '/' + BOT_TOKEN
    # bot.start_webhook(listen='0.0.0.0', port=WEB_PORT, url_path=BOT_TOKEN, webhook_url=HOOK_URL)
    # bot.idle()

    @app.route('/' + BOT_TOKEN, methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200

    @app.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url=HOOK_URL)
        return "!", 200


    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=WEB_PORT)
