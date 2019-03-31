import telepot
import time
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ForceReply
from telepot.loop import MessageLoop
import json
import requests

# Variables used in the telegram bot
userList  = []          # List of connected users
url=''
Emergency = True
# Telegram Bot Handler
def handle(msg):

    global url

    # Message variables
    chat_id = msg['chat']['id']
    command = msg['text']
    print chat_id
    print 'Message Received: %s' % command
    userList = json.loads(requests.get(url+"/users").text)

    # Start Connection

    if command == '/start':
        flag=1
        # Update user list
        for i in userList:
            if i['chat_id'] == chat_id:
                bot.sendMessage(chat_id, "You're already in my list")
                flag=0

        if flag==1:
                dic={}
                dic['chat_id'] = chat_id
                dic['emergency'] = True

                string = json.dumps(dic)
                data=requests.post(url=url+"/users",data=string)
                bot.sendMessage(chat_id, "You're now connected! Emergency notifications are turned on")

        # Keyboard UI
        bot.sendMessage(chat_id,"Please select what you want to do from the keyboard below. If you can't see the"
                                " keyboard please type \start or re-enter the chat.",
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Switch emergency status on/off")],
                                    [KeyboardButton(text="Stop the service")]
                                ]
                            ))

    # Disconnect from the Service
    elif command == 'Stop the service':
        print url+"/users?chat_id="+str(chat_id)
        a=requests.delete(url=url+"/users?chat_id="+str(chat_id))
        bot.sendMessage(chat_id,"Removed! To reconnect please use the \start command.",
                        reply_markup=ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="/start")]
                            ]
                            ))

    # Switch Emergency Status On/Off
    elif command == 'Switch emergency status on/off':
        requests.put(url+"/users?chat_id="+str(chat_id))
        for i in userList:
            if i["chat_id"] == chat_id:
                Emergency = i["emergency"]
                break

        if not Emergency:
            bot.sendMessage(chat_id, "The emergency notifications are ON",
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Switch emergency status on/off")],
                                    [KeyboardButton(text="Stop the service")]
                                ]
                            ))
        else:
            bot.sendMessage(chat_id, "The emergency notifications are OFF",
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Switch emergency status on/off")],
                                    [KeyboardButton(text="Stop the service")]
                                ]
                            ))


    # Invalid Command
    else:
        Status = False
        for i in userList:
            if i["chat_id"] == chat_id:
                Status = True
                break

        if(Status == True):
            keyboard = [
                [KeyboardButton(text="Switch emergency status on/off")],
                [ KeyboardButton(text="Stop the service")]
            ]
        else:
            keyboard = [
                [KeyboardButton(text="/start")]
            ]

        bot.sendMessage(chat_id,"Sorry, this is not a valid command.",
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=keyboard
                        ))


if __name__ == '__main__':

    # Read the config file to get server url
    try:
        file = open("config.json", "r")
        json_str = file.read()
        file.close()
    except:
        raise KeyError("Error opening config file. Please check.")

    config_json = json.loads(json_str)
    url = config_json["catalog"]["url"]

    # Read the telegram settings from the catalogue
    try:
        url=url + "/telegram"
        respond = requests.get(url)
    except:
        raise KeyError("Unable to connect to catalogue")
    respond=respond.json()

    # Start the telegram bot
    bot=telepot.Bot(respond["token"])

    try:
        MessageLoop(bot, handle).run_as_thread()
    except:
        print "Error connecting to telegram bot. Please check your connection or check if the bot token is available"

    print 'Bot started'
    while 1:
        time.sleep(10)