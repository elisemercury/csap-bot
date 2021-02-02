from webexteamssdk import WebexTeamsAPI
from webexteamsbot import TeamsBot
import urllib3
import json
import time
import requests
import os

bot_app_name = "Alert Bot"
bot_token= "MDk2MmRmYTEtOGQyZS00MjlhLThkMGMtNWYzNjNhNDJlYjE0NDY4MzVhNGUtNTM2_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
bot_url= "https://csap-bot.herokuapp.com/"
bot_email = "alertsbot@webex.bot"
subscriber_db = "subscribers.txt"

api = WebexTeamsAPI(bot_token)

bot = TeamsBot(
    bot_app_name,
    teams_bot_token=bot_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    webhook_resource_event=[
        {"resource": "messages", "event": "created"},
        {"resource": "attachmentActions", "event": "created"},
    ]
)

def greeting(incoming_msg):
    global sender, room
    sender = bot.teams.people.get(incoming_msg.personId)
    firstName = sender.firstName
    room = bot.teams.rooms.get(incoming_msg.roomId)
    attachment = card_message ### card message
    backupmessage = "This is an example using Adaptive Cards."

    c = create_message_with_attachment(
        incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
    )
    print(c)
    return ""

def handle_cards(api, incoming_msg):
    """
    Sample function to handle card actions.
    :param api: webexteamssdk object
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    
    m = get_attachment_actions(incoming_msg["data"]["id"])
    for i in sender.emails:
        mail = str(i)
    roomId = str(room.id)
    
    if m["inputs"] == "subscribe":
        with open(str(os.getcwd()) + "\\" + "subscribers.txt", "a") as f:
            f.write(mail + "," + roomId + "\n")
            
    if m["inputs"] == "unsubscribe":            
        with open(str(os.getcwd()) + "\\" + "subscribers.txt", "r") as f:
            lines = f.readlines()
        with open(str(os.getcwd()) + "\\" + "subscribers.txt", "w") as f:
            for line in lines:
                if line.strip("\n") != (mail + "," + roomId):
                    f.write(line)
                    
        with open(str(os.getcwd()) + "\\" + "unsubscribers.txt", "a") as f:
            f.write(mail + "," + roomId + "\n")
        
    if m["inputs"] == "more info":
        attachment = card_message ### card message
        backupmessage = "This is an example using Adaptive Cards."

        c = create_message_with_attachment(
            roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
        )
        return ""
    
    
    return "card action was - {}".format(m["inputs"])


def create_message_with_attachment(rid, msgtxt, attachment):
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": "Bearer " + bot_token,
    }

    url = "https://webexapis.com/v1/messages"
    data = {"roomId": rid, "attachments": [attachment], "markdown": msgtxt}
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def get_attachment_actions(attachmentid):
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": "Bearer " + bot_token,
    }

    url = "https://api.ciscospark.com/v1/attachment/actions/" + attachmentid
    response = requests.get(url, headers=headers)
    return response.json()


bot.set_greeting(greeting)
bot.add_command("attachmentActions", "*", handle_cards)

if __name__ == "__main__":
    # Run Bot
    bot.run()