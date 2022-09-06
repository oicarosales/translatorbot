import json
import requests
import urllib
import time
import mysql.connector
from googletrans import Translator, constants

TOKEN = json.loads(open("/home/icaro/MEGA/projetos/translatorbot/config.json").read())["token"]
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
USERNAME_BOT = json.loads(open("/home/icaro/MEGA/projetos/translatorbot/config.json").read())["username_bot"]


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates):
    for update in updates["result"]:
        if update.get("message") != None:
            if update.get("message", {}).get("text") != None:
                text = update["message"]["text"]
                chat = update["message"]["chat"]["id"]
                print(text)

                if text == "/start" or text == "/start@" + USERNAME_BOT:
                    send_message("Todos os idiomas serão traduzidos para o português.\n\n"
                                 "Caso envie uma frase em português, ela será traduzida para o inglês.", chat)
                    send_message("Exemplo: /translate Hello World!", chat)

                elif text == "/ajuda" or text == "/ajuda@" + USERNAME_BOT:
                    send_message("/ajuda - Mostra esta mensagem de ajuda.\nA qualquer momento, me envie o link de uma música ou playlist que eu baixo e envio para você.\nLembre-se, playlists com muitas musicas podem demorar um pouco.", chat) 
                    
                elif "/translate" in text or "/translate@" + USERNAME_BOT in text:
                    translate(text.replace("/translate","").replace("/translate@" + USERNAME_BOT,""),chat)                  
                    

                
                #EASTER EGG
                elif text == "Obrigado" or text == "Obrigada" or text == "obrigada" or text == "obrigado":
                    send_message(
                        "De nada!\nSeres humanos gentis como você serão poupados quando as máquinas tomarem o planeta Terra.", chat)
                    
                else:
                    get_updates


    
    
def send_document(doc, chat_id):
    files = {'document': open(doc, 'rb')}
    requests.post(URL + "sendDocument?chat_id={}".format(chat_id), files=files)
        
    
def send_message(text, chat_id):
    tot = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(tot, chat_id)
    get_url(url)
    
def mysql_insert(text,translation,chat):
    mysqldb = mysql.connector.connect(
        host=json.loads(open("/home/icaro/MEGA/projetos/translatorbot/config.json").read())["dbhost"],
        user=json.loads(open("/home/icaro/MEGA/projetos/translatorbot/config.json").read())["uid"],
        passwd=json.loads(open("/home/icaro/MEGA/projetos/translatorbot/config.json").read())["pwd"],
        database=json.loads(open("/home/icaro/MEGA/projetos/translatorbot/config.json").read())["database"]
    )
    
    mycursor = mysqldb.cursor()
    sql = 'INSERT INTO HISTORY (translatedtext,translationtext,chatid,date_time) VALUES (%s,%s,%s,%s)'
    val = (text,translation,chat,time.strftime("%Y-%m-%d %H:%M:%S"))
    mycursor.execute(sql, val)
    mysqldb.commit()
    mysqldb.close()    
    

def translate(text,chat):
    # identify language
    translator = Translator()
    detected = translator.detect(text)
    if detected.lang == "pt":
        translation = translator.translate(text, dest='en')
    else:
        translation = translator.translate(text, dest='pt')
    send_message(translation.text, chat)
    mysql_insert(text,translation.text,chat)
    

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates is not None:
            if len(updates["result"]) > 0:
                last_update_id = get_last_update_id(updates) + 1
                echo_all(updates)


if __name__ == '__main__':
    main()
