from webexteamssdk import WebexTeamsAPI
import webexteamssdk
from webexteamsbot import TeamsBot
#import models
import json
import requests
import os
import psycopg2
from urllib.parse import urlparse
from datetime import date, datetime
import pickle

#working
bot_app_name = "GoCSAP"
bot_token= "NTUxMGExNmItOTA2OC00YmI3LTkzOGUtZDJjNDY4MTc2MjZiZjMzMGU4YWUtMjQx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
bot_url= "https://csap-bot.herokuapp.com/"
bot_email = "GoCSAP@webex.bot"
subscriber_db = "subscribers.txt"
logs = "logs.txt"

global greeting_card, help_card, approve_card, notif_card, send_card

api = WebexTeamsAPI(bot_token)

webhook_list = []
for webhook in api.webhooks.list():
    webhook_list.append(webhook.id)
#print(webhook_list)


for webhook in api.webhooks.list():
    #print(webhook.id)
    if webhook.id != webhook_list[-2] and webhook.id != webhook_list[-1]:
        try:
            api.webhooks.delete(webhook.id)
        except:
            continue


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

url = urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

con = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
            )
cur = con.cursor()

def greeting(incoming_msg):
    fetch_infos(incoming_msg)
    print(personId)
    attachment = greeting_card #.format ### card message
    backupmessage = "Oops, this notification contained a card but it could not be displayed 😢"

    c = create_message_with_attachment(
        incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
    )

    result = check_admin(personId)
    print(result)
    
    return ""

def handle_cards(api, incoming_msg):
    room = bot.teams.rooms.get(incoming_msg["data"]["roomId"])
    roomId = room.id    
    m = get_attachment_actions(incoming_msg["data"]["id"])
    personId = m["personId"]
    db_entry = (str(roomId))

    if m["inputs"] == "subscribe":
        try:
            cur.execute("""INSERT INTO subscribers (roomid) VALUES (%s)""", (db_entry,))
            con.commit()
            # update log
            log(incoming_msg, severity=0, personId="", infoMsg="Subscriber database updated.")
            # send success message
            text="Thank you, you sucessfully subscribed to CSAP bot updates."
            api.messages.create(roomId=roomId, text=text)    
            # delete card
            api.messages.delete(messageId=m["messageId"])  
            return ""
        except:
            # delete card
            api.messages.delete(messageId=m["messageId"])  
            return "Thank you, you sucessfully subscribed to CSAP bot updates."
            
    elif m["inputs"] == "unsubscribe":    
        try:
            cur.execute("""DELETE FROM subscribers WHERE roomid = (%s)""", (db_entry,))
            con.commit()
            log(incoming_msg, severity=0, personId="", infoMsg="Subscriber database updated.")
            # send success message
            text="Thank you, you sucessfully unsubscribed from CSAP bot updates."
            api.messages.create(roomId=roomId, text=text)    
            # delete card
            api.messages.delete(messageId=m["messageId"])    
            return ""
        except:
            # delete card
            api.messages.delete(messageId=m["messageId"]) 
            return "Thank you, you successfully unsubscribed from CSAP bot updates."

    elif "{'textbox_1':" in str(m["inputs"]):
        print(1)
        log(incoming_msg, severity=1, personId=personId, infoMsg="Notification submitted.")
        print(2)
        parse = []
        image_url = m["inputs"]["image_url"]
        small_title = m["inputs"]["small_title"]
        main_title = m["inputs"]["main_title"]
        textbox_1 = m["inputs"]["textbox_1"]
        textbox_2 = m["inputs"]["textbox_2"]
        textbox_3 = m["inputs"]["textbox_3"]
        button1_text = m["inputs"]["button1_text"]
        button2_text = m["inputs"]["button2_text"]
        button3_text = m["inputs"]["button3_text"]
        button1_url = m["inputs"]["button1_url"]
        button2_url = m["inputs"]["button2_url"]
        button3_url = m["inputs"]["button3_url"]   
        review = m["inputs"]["review"]   
        print(3)
        # correct URL is invalid
        if "https" not in image_url:
            image_url = "https://" + image_url
        if "https" not in button1_url:
            button1_url = "https://" + button1_url
        if "https" not in button2_url:
            button2_url = "https://" + button2_url
        if "https" not in button3_url:
            button3_url = "https://" + button3_url
        print(4)
        parse.extend([image_url, small_title, main_title, textbox_1, textbox_2, textbox_3, button1_text, button2_text,
                    button3_text, button1_url, button2_url, button3_url])
        
        for element in parse:
            if element == "" or element == " ":
                return "Oops, seems like you didn't fill out all required fields. Please verify your entries and re-submit the notification."
        print(5)
        parse_msg(parse, roomId, review)

        return ""

    elif m["inputs"] == "approve_msg":
        with open('parse.pkl', 'rb') as f:
            parse = pickle.load(f)        

        # check if message approval comes from same room, so no confusion in case multiple people use bot
        # at the same time
        if roomId == parse[13]:
            attachment = notif_card.format(image_url=parse[0], small_title=parse[1], main_title=parse[2], 
                                   textbox_1=parse[3], textbox_2=parse[4], textbox_3=parse[5], 
                                   button1_text=parse[6], button2_text=parse[7], button3_text=parse[8], 
                                   button1_url=parse[9], button2_url=parse[10], button3_url=parse[11])
            backupmessage = "Oops, this notification contained a card but it could not be displayed 😢"
            
            text="Notification approved and sent to bot subscribers! 🎉"
            api.messages.create(roomId=roomId, 
                                 text=text)    

            api.messages.delete(messageId=m["messageId"])            
            os.remove("parse.pkl") 
            
            c = create_message_with_attachment(
                roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
            ) # change to bot subscribers
            
            log(incoming_msg, severity=2, personId=personId, infoMsg="Notification approved and sent.")
            return ""      
        
        else:
            api.messages.delete(messageId=m["messageId"])    
            log(incoming_msg, severity=2, personId=personId, infoMsg="Notification approval without permission. Not sent.")
            return "Oops, you do not have permission to approve the notification!"

    elif m["inputs"] == "decline_msg":
        os.remove("parse.pkl") 
        api.messages.delete(messageId=m["messageId"]) 
        log(incoming_msg, severity=2, personId=personId, infoMsg="Notification declined and not sent.")        
        return "Notification declined an not sent 😞"

    api.messages.delete(messageId=m["messageId"])
    log(incoming_msg, severity=3, personId=personId, infoMsg="Faulty command. Please review: "+str(m["inputs"]))
    return "Sorry, I do not understand the command {} yet.".format(firstName, m["inputs"])    

def parse_msg(parse, roomId, review):
    print(5)
    now = datetime.now()
    msg_id = now.strftime("%d%m%Y-%H%M")
    
    parse.extend([msg_id, roomId])
    print(6)
    attachment = notif_card.format(image_url=parse[0], small_title=parse[1], main_title=parse[2], 
                                   textbox_1=parse[3], textbox_2=parse[4], textbox_3=parse[5], 
                                   button1_text=parse[6], button2_text=parse[7], button3_text=parse[8], 
                                   button1_url=parse[9], button2_url=parse[10], button3_url=parse[11],
                                   msg_id=parse[12])   
    print(7)
    backupmessage = "Oops, this notification contained a card but it could not be displayed 😢"
    
    if str(review) == "true":
        print(8)
        with open('parse.pkl', 'wb') as f:
            pickle.dump(parse, f)
        c = create_message_with_attachment(roomId, msgtxt=backupmessage, 
                                           attachment=json.loads(attachment))    

        print(9)                                    
         
        c = create_message_with_attachment(roomId, msgtxt=backupmessage, 
                                           attachment=json.loads(approve_card.format(msg_id=parse[12])))  
        print(10)
        log(incoming_msg="", severity=1, personId=personId, infoMsg="Notification submitted and sent for review.")
        
    else:
        c = create_message_with_attachment(roomId, msgtxt=backupmessage, attachment=json.loads(attachment))
        log(incoming_msg="", severity=2, personId=personId, infoMsg="Notification submitted without review.")
        # change to bot subscribers

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

def subscribe(incoming_msg):
    fetch_infos(incoming_msg)
    db_entry = roomId
    try:
        cur.execute("""INSERT INTO subscribers (roomid) VALUES (%s)""", (db_entry,))
        con.commit()
        log(incoming_msg, severity=0, personId="", infoMsg="Subscriber database updated.")
    except:
        print("Could not be added to DB")
        
    return "Thank you, you sucessfully subscribed to CSAP bot updates."

def unsubscribe(incoming_msg):
    fetch_infos(incoming_msg)
    db_entry = roomId

    try:
        cur.execute("""DELETE FROM subscribers WHERE roomid = (%s)""", (db_entry,))
        con.commit()
        log(incoming_msg, severity=0, personId="", infoMsg="Subscriber database updated.")
    except:
        print("Could not be removed from DB")
    return "Thank you, you sucessfully unsubscribed from CSAP bot updates."  

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
    sender = bot.teams.people.get(incoming_msg.personId)
    email = sender.emails
    firstName = sender.firstName
    room = bot.teams.rooms.get(incoming_msg.roomId)
    roomId = room.id
    return sender, firstName, room, roomId, email

def send_notif(incoming_msg):
    person = bot.teams.people.get(incoming_msg.personId)
    personId = person.id
    attachment = send_card
    backupmessage = "Oops, this notification contained a card but it could not be displayed 😢"

    c = create_message_with_attachment(incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment))  
    log(incoming_msg, severity=1, personId=personId, infoMsg="Notification request made.")
    
    return ""   

def log(incoming_msg, severity, personId, infoMsg=""):
    # function for logging al things sent with the bot
    # severity 0, 1, 2, 3 (0=informational, ..., 3=emergency)
    with open(logs) as json_file:
        data = json.load(json_file)
    print(300)
    now = datetime.now()
    logDate = now.strftime("%d%m%Y-%H:%M")   
    
    data[logDate] = {"date": now.strftime("%d-%m-%Y"),
                     "severity": severity,
                     "infoMsg": infoMsg,
                     "personId": personId}
    print(301) 
    with open(logs, 'w') as outfile:
        json.dump(data, outfile)    

def check_admin(personId="", email=""):
    if personId != "":
        adminList = cur.execute("""SELECT personid FROM admins""")
        print(adminList)
        if personId in adminList:
            return "Authorized"
        else:
            return "Unauthorized"

    elif email != "":
        adminList = cur.execute("""SELECT email FROM admins""")
        print(adminList)
        if email in adminList:
            return "Authorized"
        else:
            return "Unauthorized"
    else:
        return "Unauthorized"

bot.set_greeting(greeting)
bot.add_command("attachmentActions", "*", handle_cards)
bot.add_command("help", "Help", help)
bot.add_command("contact", "Contact", contact)
bot.add_command("subscribe", "subscribe", subscribe)
bot.add_command("unsubscribe", "unsubscribe", unsubscribe)
bot.add_command("send notif", "Send notif", send_notif)

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

approve_card = """
    {{
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {{
    "type": "AdaptiveCard",
    "body": [
        {{
            "type": "TextBlock",
            "text": "Your message with message ID {msg_id} has been sent for review. Please approve or decline the message to be sent to all bot subscribers.",
            "wrap": true
        }},
        {{
            "type": "ColumnSet",
            "columns": [
                {{
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {{
                            "type": "ActionSet",
                            "actions": [
                                {{
                                    "type": "Action.Submit",
                                    "title": "Decline",
                                    "style": "destructive",
                                    "id": "decline_msg",
                                    "data": "decline_msg"
                                }},
                                {{
                                    "type": "Action.Submit",
                                    "title": "Approve",
                                    "style": "positive",
                                    "id": "approve_msg",
                                    "data": "approve_msg"
                                }}
                            ],
                            "horizontalAlignment": "Left",
                            "spacing": "None"
                        }}
                    ]
                }}
            ],
            "spacing": "None"
        }}
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """ #.format(test="ALOHA")


notif_card = """
    {{
      "contentType": "application/vnd.microsoft.card.adaptive",
      "content": {{
    "type": "AdaptiveCard",
    "body": [
        {{
            "type": "ColumnSet",
            "columns": [
                {{
                    "type": "Column",
                    "items": [
                        {{
                            "type": "ColumnSet",
                            "columns": [
                                {{
                                    "type": "Column",
                                    "width": "100px",
                                    "items": [
                                        {{
                                            "type": "Image",
                                            "altText": "",
                                            "url": "{image_url}",
                                            "horizontalAlignment": "Left"
                                        }}
                                    ]
                                }},
                                {{
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {{
                                            "type": "TextBlock",
                                            "text": "{small_title}",
                                            "weight": "Lighter",
                                            "color": "Accent"
                                        }},
                                        {{
                                            "type": "TextBlock",
                                            "weight": "Bolder",
                                            "text": "{main_title}",
                                            "horizontalAlignment": "Left",
                                            "wrap": true,
                                            "color": "Light",
                                            "size": "Large",
                                            "spacing": "Small"
                                        }}
                                    ],
                                    "verticalContentAlignment": "Center"
                                }}
                            ]
                        }}
                    ],
                    "width": "stretch"
                }}
            ]
        }},
        {{
            "type": "TextBlock",
            "text": "{textbox_1}",
            "wrap": true
        }},
        {{
            "type": "TextBlock",
            "text": "{textbox_2}",
            "spacing": "ExtraLarge"
        }},
        {{
            "type": "TextBlock",
            "text": "{textbox_3}",
            "spacing": "Padding",
            "wrap": true
        }},
        {{
        "type": "ActionSet",
    "actions": [{{"type": "Action.OpenUrl",
                         "title": "{button1_text}",
                         "url": "{button1_url}",
                         "horizontalAlignment": "Left"
                        }},
                 {{"type": "Action.OpenUrl",
                         "title": "{button2_text}",
                         "url": "{button2_url}",
                         "horizontalAlignment": "Left"
                        }},
                {{"type": "Action.OpenUrl",
                         "title": "{button3_text}",
                         "url": "{button3_url}",
                         "horizontalAlignment": "Left"
                        }}
                        ],
                "horizontalAlignment": "Left",
                "spacing": "None"
    }},
    {{
        "type": "TextBlock",
        "text": "Under review: {msg_id}",
        "spacing": "None",
        "horizontalAlignment": "Right",
        "fontType": "Monospace",
        "size": "Small",
        "weight": "Lighter",
        "color": "Light"
    }}
    
    
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """ #.format(test="ALOHA")

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

send_card = """
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
                            "type": "Image",
                            "url": "https://i.pinimg.com/originals/54/68/bf/5468bf0cb6dcdeab64c17731dac360ae.gif",
                            "size": "Medium",
                            "height": "50px"
                        }
                    ],
                    "width": "auto"
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "Input.Text",
                            "placeholder": "Small Text",
                            "spacing": "None",
                            "id": "small_title"
                        },
                        {
                            "type": "Input.Text",
                            "placeholder": "Main title",
                            "id": "main_title",
                            "spacing": "None"
                        }
                    ],
                    "width": "stretch"
                }
            ]
        },
        {
            "type": "Container",
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "Input.Text",
                                    "placeholder": "Text box 1",
                                    "isMultiline": true,
                                    "id": "textbox_1"
                                },
                                {
                                    "type": "Input.Text",
                                    "placeholder": "Text box 2",
                                    "id": "textbox_2",
                                    "spacing": "Small"
                                },
                                {
                                    "type": "Input.Text",
                                    "placeholder": "Text Box 3",
                                    "id": "textbox_3",
                                    "isMultiline": true,
                                    "spacing": "Small"
                                },
                                {
                                    "type": "ColumnSet",
                                    "columns": [
                                        {
                                            "type": "Column",
                                            "width": "stretch",
                                            "items": [
                                                {
                                                    "type": "Input.Text",
                                                    "placeholder": "Button 1 text",
                                                    "id": "button1_text"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "Column",
                                            "width": "stretch",
                                            "items": [
                                                {
                                                    "type": "Input.Text",
                                                    "placeholder": "Button 2 text",
                                                    "id": "button2_text"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "Column",
                                            "width": "stretch",
                                            "items": [
                                                {
                                                    "type": "Input.Text",
                                                    "placeholder": "Button 3 text",
                                                    "id": "button3_text"
                                                }
                                            ]
                                        }
                                    ],
                                    "spacing": "Small"
                                }
                            ]
                        }
                    ],
                    "spacing": "None",
                    "bleed": true
                }
            ],
            "bleed": true
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "Input.Text",
                                            "placeholder": "Button URL",
                                            "id": "button1_url"
                                        }
                                    ]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "Input.Text",
                                            "placeholder": "Button URL",
                                            "id": "button2_url"
                                        }
                                    ]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "Input.Text",
                                            "placeholder": "Button URL",
                                            "id": "button3_url"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "Input.Text",
                            "placeholder": "Image URL",
                            "id": "image_url",
                            "spacing": "None"
                        }
                    ]
                }
            ],
            "horizontalAlignment": "Center",
            "spacing": "ExtraLarge",
            "separator": true
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {
                            "type": "Input.Toggle",
                            "title": "Review before sending",
                            "value": "true",
                            "wrap": false,
                            "id": "review",
                            "spacing": "None"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.Submit",
                                    "title": "Submit Notification",
                                    "id": "submit"
                                }
                            ],
                            "horizontalAlignment": "Center",
                            "spacing": "None"
                        }
                    ]
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "If **Review before sending** is checked, the notification will first be sent to you for review before it is sent to all subscribers.",
            "wrap": true,
            "color": "Light"
        }
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}
    }
  """