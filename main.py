import os
import requests
import json
import traceback
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
API_URL = os.environ.get('API_URL')
API_PROVIDER = os.environ.get('API_PROVIDER')
IFRAME_LINK = os.environ.get('IFRAME_LINK')

# def initDb():
#     db = psycopg2.connect(
#         host=DB_HOST,
#         port=DB_PORT,
#         user=DB_USER,
#         password=DB_PASS,
#         database=DB_NAME
#     )
#     return db
# mydb = initDb()
# try:
#     cur = mydb.cursor()
#     cur.execute('SELECT 1')
    
#     print("Berhasil terhubung ke database")
# except Exception as err:
#     print(err)
#     print("Gagal terhubung ke database")
#     pass

# def checkUser(user_id):
#     global mydb
#     try:
#         mycursor = mydb.cursor()
#     except psycopg2.InterfaceError as err:
#         print(err)
#         mydb = initDb()
#         mycursor = mydb.cursor()
#     try:
#         sql = "SELECT * FROM users WHERE user_id = %s"
#         val = [user_id]
#         mycursor.execute(sql, val)
#         myresult = mycursor.fetchone()
#         mydb.commit()
#         return myresult
#     except Exception as err:
#         print("Error Check User : ")
#         print(err)
#         return None
    

# def insertUser(user_id,username):
#     global mydb
#     cek = checkUser(user_id)
#     if cek is None:
#         try:
#             mycursor = mydb.cursor()
#         except psycopg2.InterfaceError as err:
#             print(err)
#             mydb = initDb()
#             mycursor = mydb.cursor()
#         try:
#             sql = "INSERT INTO users (user_id, username) VALUES (%s, %s)"
#             val = (user_id,str(username))
#             mycursor.execute(sql, val)
#             mydb.commit()
#             return True
#         except Exception as err:
#             print("Error Insert User : ")
#             print(err)
#             return False
#     else:
#         return False

# def getHistoryById(id):
#     global mydb
#     try:
#         mycursor = mydb.cursor()
#     except Exception as err:
#         print(err)
#         mydb = initDb()
#         mycursor = mydb.cursor()
#     sql = "SELECT * FROM history_film WHERE id = %s"
#     val = (id,)
#     mycursor.execute(sql, val)
#     myresult = mycursor.fetchone()
#     mydb.commit()
#     return myresult

# def getHistoryByLink(link):
#     global mydb
#     try:
#         mycursor = mydb.cursor()
#     except Exception as err:
#         print(err)
#         mydb = initDb()
#         mycursor = mydb.cursor()
#     sql = "SELECT * FROM history_film WHERE link = %s"
#     val = (link,)
#     mycursor.execute(sql, val)
#     myresult = mycursor.fetchone()
#     mydb.commit()
#     return myresult

# def insertHistory(link,message_id):
#     global mydb
#     cek = getHistoryByLink(link)
#     if cek is None:
#         try:
#             mycursor = mydb.cursor()
#         except psycopg2.InterfaceError as err:
#             print(err)
#             mydb = initDb()
#             mycursor = mydb.cursor()
#         sql = "INSERT INTO history_film (link, message_id) VALUES (%s, %s) RETURNING id;"
#         val = (link,message_id)
#         mycursor.execute(sql, val)
#         data = mycursor.fetchone()
#         mydb.commit()
#         id_of_new_row = data[0]
#         return id_of_new_row
#     else:
#         return cek[0]

bot = telebot.TeleBot(BOT_TOKEN, threaded=ENV != "production")


def searchMovie(movieName):
    print("Start search movie... ",movieName)
    url = API_URL+"/search?query=" + str(movieName) + "&providers[]="+API_PROVIDER
    response = requests.get(url)
    if response.status_code != 200:
        print("Error : "+str(response.text))
        return []
    else:
        data = response.json()
        return data
def detailMovie(movieLink):
    url = API_URL + "/get?link=" + movieLink + "/&provider="+API_PROVIDER
    print(url)
    response = requests.get(url)
    data = response.json()
    return data

def cleanLink(link):
    return link.replace("/api/get?link=","").replace("/&provider="+API_PROVIDER,"")



@bot.message_handler(commands=['search'])
def search(message):
    print(message.from_user.id,message.from_user.username)
    print("Search movie... ",message.text)
    movieName = message.text.replace("/search ", "")
    
    try:
        if movieName == "" or movieName == "/search":
            bot.reply_to(message, 'Silahkan ketik /search "judul film" (tanpa tanda kutip) untuk mencari film, contoh /search avenger')
            return
        bot.reply_to(message, "Mencari film "+movieName+" silahkan tunggu...")
    except Exception as err:
        print(err)
        return
    data = searchMovie(movieName)
    data5 = data[:5]

    if len(data5) == 0:
        bot.reply_to(message, "Film "+movieName+" tidak ditemukan")
        return

    
    for i in data5:
        link = cleanLink(i['link'])
        # id = insertHistory(link,message.id)
        

        try:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text="Link Stream 🎥", callback_data="/detail "+str(link)))
            bot.send_photo(message.chat.id, i['thumb'], caption='<a href="'+str(link)+'">\u200b</a><b>'+i['title']+'</b>',  reply_markup=markup,parse_mode="HTML")
        except Exception as err:
            print("ERROR 1 : ",err)
            try:
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(text="Link Stream 🎥", callback_data="/detail "+str(link)))
                bot.send_message(message.chat.id, '<a href="'+str(link)+'">\u200b</a><b>'+i['title']+'</b>',  reply_markup=markup,parse_mode="HTML")
            except Exception as err:
                print("ERROR 2 : ",err)
                try:
                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton(text="Link Stream 🎥", callback_data="/detail [btn:0]"))
                    bot.send_message(message.chat.id, '<a href="'+str(link)+'">\u200b</a>'+i['title'],  reply_markup=markup,parse_mode="HTML")
                except Exception as err:
                    print("ERROR 3 : ",err)
                    bot.send_message(message.chat.id, "Link Stream <b>"+i['title']+"</b> : "+str(link),parse_mode="HTML")
               

        # check link length
        # if len(str(link).encode('utf-8')) <= 64:
        #     markup.add(telebot.types.InlineKeyboardButton(text="Link Stream 🎥", callback_data="/detail "+str(link)))
        #     try:
        #         bot.send_photo(message.chat.id, i['thumb'], caption=i['title'],  reply_markup=markup,parse_mode="Markdown")
        #     except Exception as err:
        #         print(err)
        #         bot.send_message(message.chat.id, "Link Stream "+i['title']+" : "+str(link),parse_mode="Markdown")
        # else:
        #     bot.send_photo(message.chat.id, i['thumb'], caption=i['title'])
        #     bot.send_message(message.chat.id, "Link Stream "+i['title']+" : "+str(link),parse_mode="Markdown")

@bot.message_handler(commands=['start', 'hello','help'])
def send_welcome(message):
    print(message.from_user.id,message.from_user.username)
    # try:
    #     insertUser(message.from_user.id,message.from_user.username)
    # except Exception as err:
    #     print(err)
    #     print(err.__traceback__)
    #     traceback.print_tb(err.__traceback__)

    bot.reply_to(message, """
Selamat datang di bot """+API_PROVIDER+"""
Ketik /search "judul film" (tanpa tanda kutip) untuk mencari film, contoh /search avenger
""")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("/detail"):
        link = call.data.replace("/detail ","")
        print(link)
        # loop call.message.entities when type is text_link
        links = []
        for entity in call.message.entities:
            if entity.type == "text_link":
                links.append(entity.url)
        if link.startswith("[btn:"):
            index = int(link.replace("[btn:","").replace("]",""))
            link = links[index]
        try:
            
            # history = getHistoryById(id)
            # link = history[2]
            # print("Link : "+link)
            bot.send_message(call.message.chat.id, "Mencari link streaming film silahkan tunggu...")
            data = detailMovie(link)
            
            if "episode" in data:
                markup = telebot.types.InlineKeyboardMarkup()
                strLink = ""
                index = 0
                for e in data['episode']:
                    link = cleanLink(e['link'])
                    # id = insertHistory(link,call.message.id)
                    markup.add(telebot.types.InlineKeyboardButton(text="Eps "+e['title'], callback_data="/detail [btn:"+str(index)+"]"))
                    index += 1
                    strLink += '<a href="'+str(link)+'">\u200b</a>'
                bot.send_message(call.message.chat.id, strLink+"<b>"+data['title'] + "</b> Episode (urutan season dari paling bawah) : ", reply_markup=markup,parse_mode="HTML")
            else:
                linkMessage = "Link Streaming "+data['title']+" (Tidak Menjamin Semua Link Work): \n"
                markup = telebot.types.InlineKeyboardMarkup()
                for s in data['stream']:
                    if s['detail'] == None or s['detail'] == "" or s['detail'] == "None" or s['detail'] == "null":
                        streamLink = s['link']
                        # if steramLink start with //
                        if streamLink.startswith("//"):
                            streamLink = "https:"+streamLink

                        markup.add(telebot.types.InlineKeyboardButton(text=s['title'], url=streamLink))
                    else:
                        if "/iframe?link=" in s['detail']:
                            link_frame = IFRAME_LINK+s['detail']
                        else:
                            link_frame = s['detail']
                        markup.add(telebot.types.InlineKeyboardButton(text=s['title'], url=link_frame))
                bot.send_message(call.message.chat.id,  linkMessage, reply_markup=markup,parse_mode="Markdown")
        except Exception as err:
            print(err)
            bot.send_message(call.message.chat.id, "Maaf terjadi kesalahan, silahkan coba lagi")

WEB_PORT = os.environ.get('WEB_PORT', '5000')
WEB_URL = os.environ.get('WEB_URL')
HOOK_URL = WEB_URL + '/' + BOT_TOKEN

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    drop_pending_updates = False
    if request.args.get("drop_pending_updates"):
        drop_pending_updates = True
    bot.set_webhook(url=HOOK_URL,drop_pending_updates=drop_pending_updates)
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

# route to check status database
@app.route("/dbstatus")
def dbstatus():
    try:
        # cur = mydb.cursor()
        # cur.execute('SELECT 1')
        return "Database connected",200
    except Exception as err:
        return "Database not connected",500

# route list users
@app.route('/users')
def users():
    # try:
    #     mycursor = mydb.cursor()
    # except Exception as err:
    #     print(err)
    #     mydb = initDb()
    #     mycursor = mydb.cursor()
    # mycursor.execute("SELECT * FROM users")
    # myresult = mycursor.fetchall()
    # mydb.commit()
    myresult = []
    return jsonify(myresult),200

@app.route("/stop")
def stop():
    bot.remove_webhook()
    bot.stop_polling()
    return "Bot stopped",200

def main():
    print(ENV)
    if ENV != "production":
        bot.remove_webhook()
        bot.infinity_polling()
    else:
        app.run(host="0.0.0.0", port=WEB_PORT)
    
if __name__ == "__main__":
    main()
