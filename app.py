from webexteamssdk import WebexTeamsAPI
from webexteamsbot import TeamsBot
import urllib3
import json
import time
import requests
import os

bot_app_name = "Time Recording Bot"
bot_token= "N2Y5NTA3NmUtYjc4MC00ZGFhLWE4MjctNDgwOTc4ZjUwMzI2YjI4MDViZTUtOGNk_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
bot_url= "https://csap-bot.herokuapp.com/"
bot_email = "timerec@webex.bot"
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
    room = bot.tea"""
    {
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "100px",
                                    "items": [
                                        {
                                            "type": "Image",
                                            "altText": "",
                                            "url": "https://i.pinimg.com/originals/54/68/bf/5468bf0cb6dcdeab64c17731dac360ae.gif",
                                            "horizontalAlignment": "Left"
                                        }
                                    ]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "CSAP Bot",
                                            "weight": "Lighter",
                                            "color": "Accent"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "weight": "Bolder",
                                            "text": "Welcome!",
                                            "horizontalAlignment": "Left",
                                            "wrap": true,
                                            "color": "Light",
                                            "size": "Large",
                                            "spacing": "Small"
                                        }
                                    ],
                                    "verticalContentAlignment": "Center"
                                }
                            ]
                        }
                    ],
                    "width": "stretch"
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "Hello, I'm your CSAP bot. You can **subscribe** to receive updates and latest news from within the CSAP program!",
            "wrap": true
        },
        {
            "type": "TextBlock",
            "text": "📋 **CSAP bot content includes:**",
            "spacing": "ExtraLarge"
        },
        {
            "type": "TextBlock",
            "text": "• General CSAP infos and news",
            "spacing": "Padding",
            "wrap": true
        },
        {
            "type": "TextBlock",
            "text": "• Notifications about events",
            "spacing": "Small"
        },
        {
            "type": "TextBlock",
            "text": "• Get updated on the latest newsletters created by CSAPers",
            "height": "stretch",
            "wrap": true,
            "spacing": "Small"
        }],
    "actions": [{"type": "Action.Submit",
                         "title": "Subscribe",
                         "data": "subscribe",
                         "style": "positive",
                         "id": "button1"
                        },
                        {"type": "Action.OpenUrl",
                         "title": "More Info",
                         "url": "https://cisco.sharepoint.com/sites/CSAPGlobal/SitePages/CSAP%20Live.aspx"
                        },
                        {"type": "Action.Submit",
                         "title": "Unsubscribe",
                         "data": "unsubscribe",
                         "style": "positive",
                         "id": "button3" 
                        }
                        ],
    
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
    }
  """
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
    print(m)
    sender = bot.teams.people.get(incoming_msg.personId)
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
    bot.run(host="127.0.0.1", port="80")