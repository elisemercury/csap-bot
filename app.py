from webexteamssdk import WebexTeamsAPI
import webexteamssdk
from webexteamsbot import TeamsBot
#import models
import json
import requests
import os
import psycopg2
from urllib.parse import urlparse

#working
bot_app_name = "Time Recording Bot"
bot_token= "N2Y5NTA3NmUtYjc4MC00ZGFhLWE4MjctNDgwOTc4ZjUwMzI2YjI4MDViZTUtOGNk_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
bot_url= "https://csap-bot.herokuapp.com/"
bot_email = "timerec@webex.bot"
subscriber_db = "subscribers.txt"

global greeting_card, help_card

api = WebexTeamsAPI(bot_token)

webhook_list = []
for webhook in api.webhooks.list():
    webhook_list.append(webhook.id)
#print(webhook_list)


for webhook in api.webhooks.list():
    #print(webhook.id)
    if webhook.id != webhook_list[-2] and webhook.id != webhook_list[-1]:
        api.webhooks.delete(webhook.id)


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

DATABASE_URL=$(heroku config:get DATABASE_URL -a csap-bot) python app.py

def greeting(incoming_msg):
    fetch_infos(incoming_msg)
    attachment = greeting_card ### card message
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
    sender, firstName, room, roomId = fetch_infos(incoming_msg)
    
    m = get_attachment_actions(incoming_msg["data"]["id"])
#     for i in sender.emails:
#         mail = str(i)
#     roomId = str(room.id)

    if m["inputs"] == "subscribe":
        with open(subscriber_db) as json_file:
            data = json.load(json_file)
            if roomId not in data["subscribers"]:
                #cur.execute("INSERT INTO subscribers (RoomId) VALUES (%s)", (roomId))
                data["subscribers"].append(roomId)        
                with open(subscriber_db, 'w') as outfile:
                    json.dump(data, outfile)        
        return "Thank you, you sucessfully subscribed to CSAP bot updates."
            
    if m["inputs"] == "unsubscribe":    
        with open(subscriber_db) as json_file:
            data = json.load(json_file)
        if roomId in data["subscribers"]:
            data["subscribers"].remove(roomId)        
            with open(subscriber_db, 'w') as outfile:
                json.dump(data, outfile)     
        return "Thank you, you sucessfully unsubscribed from CSAP bot updates."  
    
    return "Sorry {}, I do not understand the command {} yet.".format(firstName, m["inputs"])    


def create_message_with_attachment(rid, msgtxt, attachment):
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": "Bearer " + bot_token,
    }

    url = "https://api.ciscospark.com/v1/messages"
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

def help(incoming_msg):
    #fetch_infos(incoming_msg)
    attachment = help_card
    backupmessage = "This is an example using Adaptive Cards."

    c = create_message_with_attachment(
        incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
    )    
    
    return ""

def contact(incoming_msg):
    fetch_infos(incoming_msg)
    return "Thank you {} for using the CSAP bot. \n Current version is v1.0. \n Please contact elandman@cisco.com for more information.".format(firstName)

def fetch_infos(incoming_msg):
    global sender, firstName, room, roomId
    sender, firstName, room, roomId = None, None, None, None
    try:
        sender = bot.teams.people.get(incoming_msg.personId)
        firstName = sender.firstName
        room = bot.teams.rooms.get(incoming_msg.roomId)
        roomId = room.id
    except:
        pass
    return sender, firstName, room, roomId


bot.set_greeting(greeting)
bot.add_command("attachmentActions", "*", handle_cards)
bot.add_command("help", "Help", help)
bot.add_command("contact", "Contact", contact)

if __name__ == "__main__":

    webhook_list = []
    for webhook in api.webhooks.list():
        webhook_list.append(webhook.id)
    #print(webhook_list)


    for webhook in api.webhooks.list():
        #print(webhook.id)
        if webhook.id != webhook_list[-2] and webhook.id != webhook_list[-1]:
            api.webhooks.delete(webhook.id)

    # Run Bot
    bot.run()

greeting_card = """
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

help_card = """
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
                                            "text": "Help",
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
            "text": "I was especially designed to keep you up to date on the most important topics around CSAP. ",
            "wrap": true
        },
        {
            "type": "TextBlock",
            "text": "🙋 **I understand the following commands:**",
            "spacing": "ExtraLarge"
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "120px",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "`subscribe`"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Subscribe to CSAP bot updates.",
                            "wrap": true
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "120px",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "`unsubscribe`"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Unsubscribe from CSAP bot updates."
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "120px",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "`more info`"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Open **CSAP Global** Sharepoint info page."
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "120px",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "`help`"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Open CSAP bot information."
                        }
                    ]
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "120px",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "`contact`"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Contact the team behind CSAP bot.",
                            "wrap": true
                        }
                    ]
                }
            ]
        },
        {
            "type": "ActionSet",
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
            "horizontalAlignment": "Left"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
    }
  """