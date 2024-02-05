import os
import requests
import json
from dotenv import load_dotenv
import telebot
import psycopg2
from flask import Flask,request,jsonify
app = Flask(__name__)


load_dotenv()

ENV = os.environ.get('ENV')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_NAME = os.environ.get('DB_NAME')

def initDb():
    db = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )
    return db
mydb = initDb()
try:
    cur = mydb.cursor()
    cur.execute('SELECT 1')
    
    print("Berhasil terhubung ke database")
except Exception as err:
    print(err)
    print("Gagal terhubung ke database")
    pass

def checkUser(user_id):
    global mydb
    try:
        mycursor = mydb.cursor()
    except Exception as err:
        print(err)
        mydb = initDb()
        mycursor = mydb.cursor()
    sql = "SELECT * FROM users WHERE user_id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchone()
    mydb.commit()
    return myresult

def insertUser(user_id,username):
    global mydb
    cek = checkUser(user_id)
    if cek is None:
        try:
            mycursor = mydb.cursor()
        except psycopg2.InterfaceError as err:
            print(err)
            mydb = initDb()
            mycursor = mydb.cursor()
        sql = "INSERT INTO users (user_id, username) VALUES (%s, %s)"
        val = (user_id,username)
        mycursor.execute(sql, val)
        mydb.commit()
        return True
    else:
        return False

def getHistoryById(id):
    global mydb
    try:
        mycursor = mydb.cursor()
    except Exception as err:
        print(err)
        mydb = initDb()
        mycursor = mydb.cursor()
    sql = "SELECT * FROM history_film WHERE id = %s"
    val = (id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchone()
    mydb.commit()
    return myresult

def getHistoryByLink(link):
    global mydb
    try:
        mycursor = mydb.cursor()
    except Exception as err:
        print(err)
        mydb = initDb()
        mycursor = mydb.cursor()
    sql = "SELECT * FROM history_film WHERE link = %s"
    val = (link,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchone()
    mydb.commit()
    return myresult

def insertHistory(link,message_id):
    global mydb
    cek = getHistoryByLink(link)
    if cek is None:
        try:
            mycursor = mydb.cursor()
        except psycopg2.InterfaceError as err:
            print(err)
            mydb = initDb()
            mycursor = mydb.cursor()
        sql = "INSERT INTO history_film (link, message_id) VALUES (%s, %s) RETURNING id;"
        val = (link,message_id)
        mycursor.execute(sql, val)
        data = mycursor.fetchone()
        mydb.commit()
        id_of_new_row = data[0]
        return id_of_new_row
    else:
        return cek[0]

# data = getHistoryByLink("https://pusatfilm21.vip/tv/one-piece-2")
# print(data[1])
# exit()
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
api_url = "https://perompak7samudra-52cvvzmy5q-de.a.run.app/api"

def searchMovie(movieName):
    print("Start search movie ",movieName)
    url = api_url+"/search?query=" + movieName + "&providers[]=PusatFilm"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error : "+response.text)
        return []
    else:
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



@bot.message_handler(commands=['search'])
def search(message):
    movieName = message.text.replace("/search ", "")
    if movieName == "" or movieName == "/search":
        bot.reply_to(message, "Silahkan ketik /search <judul film> untuk mencari film")
        return
    bot.reply_to(message, "Mencari film "+movieName+" silahkan tunggu...")
    data = searchMovie(movieName)
    data5 = data[:5]

    if len(data5) == 0:
        bot.reply_to(message, "Film "+movieName+" tidak ditemukan")
        return

    # send message photo and title
    # when user click the message, call detailMovie function
    for i in data5:
        link = cleanLink(i['link'])
        id = insertHistory(link,message.id)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text="Link Stream 🎥", callback_data="/detail "+str(id)))
        bot.send_photo(message.chat.id, i['thumb'], caption=i['title'],  reply_markup=markup,parse_mode="Markdown")

@bot.message_handler(commands=['start', 'hello','help'])
def send_welcome(message):
    try:
        insertUser(message.from_user.id,message.from_user.username)
    except Exception as err:
        print(err)
    bot.reply_to(message, """
Selamat datang di bot PusatFilm
Ketik /search <judul film> untuk mencari film
""")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("/detail"):
        # print(call.text)
        try:
            id = call.data.replace("/detail ","")
            history = getHistoryById(id)
            link = history[2]
            print("Link : "+link)
            bot.send_message(call.message.chat.id, "Mencari link streaming film silahkan tunggu...")
            
            # message_text = call.message.caption
            # link = message_text.split("\n")[1]
            # link = call.text.replace("https://perompak7samudra-52cvvzmy5q-de.a.run.app/api/get?link=","").replace("/&provider=PusatFilm","")
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
                    markup.add(telebot.types.InlineKeyboardButton(text=s['title'], url="https://perompak7samudra-52cvvzmy5q-de.a.run.app"+s['detail']))
                    # linkMessage += "["+s['title']+"](https://perompak7samudra-52cvvzmy5q-de.a.run.app"+s['detail']+")\n\n"
                bot.send_message(call.message.chat.id,  linkMessage, reply_markup=markup,parse_mode="Markdown")
        except Exception as err:
            print(err)
            bot.send_message(call.message.chat.id, "Maaf terjadi kesalahan, silahkan coba lagi")

WEB_PORT = os.environ.get('WEB_PORT', '5000')
WEB_URL = os.environ.get('WEB_URL')
HOOK_URL = WEB_URL + '/' + BOT_TOKEN
# bot.start_webhook(listen='0.0.0.0', port=WEB_PORT, url_path=BOT_TOKEN, webhook_url=HOOK_URL)
# bot.idle()

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    print(json_string)
    bot.process_new_updates([update])
    # bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=HOOK_URL,drop_pending_updates=True)
    return "!", 200

# check if webhook is working
@app.route("/status")
def status():
    info = bot.get_webhook_info()
    result = {
        "url": info.url,
        "last_error_date": info.last_error_date,
        "last_error_message": info.last_error_message,
        "pending_update_count": info.pending_update_count,
    }
    return jsonify(result),200

def main():
    if ENV != "production":
        bot.remove_webhook()
        bot.infinity_polling()
    else:
        app.run(host="0.0.0.0", port=WEB_PORT)
    
if __name__ == "__main__":
    main()
