from webexteamssdk import WebexTeamsAPI
import webexteamssdk
from webexteamsbot import TeamsBot
import json
import requests
import os
import psycopg2
from urllib.parse import urlparse
from datetime import date, datetime
import pickle
import time
import re
import xlsxwriter

global greeting_card, help_card, approve_card, notif_card, send_card

# fetch env variables
bot_app_name = os.environ["BOT_NAME"]
bot_token= os.environ["BOT_TOKEN"]
bot_url= os.environ["BOT_URL"]
bot_email = os.environ["BOT_EMAIL"]
logs = os.environ["LOGFILE"]

api = WebexTeamsAPI(bot_token)

webhook_list = []
for webhook in api.webhooks.list():
    webhook_list.append(webhook.id)

for webhook in api.webhooks.list():
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
        {"resource": "attachmentActions", "event": "created"},])

# actiavte database connection
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

    attachment = greeting_card #.format ### card message
    backupmessage = "Hi there! 👋 It's nice to meet you."

    c = create_message_with_attachment(
        incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
    )
    
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
            text="Thank you, you sucessfully subscribed to GoCSAP bot updates. 🥳"
            api.messages.create(roomId=roomId, text=text)    
            # delete card
            api.messages.delete(messageId=m["messageId"])  
            return ""
        except:
            # delete card
            api.messages.delete(messageId=m["messageId"])  
            return "Thank you, you sucessfully subscribed to GoCSAP bot updates. 🥳"
            
    elif m["inputs"] == "unsubscribe":    
        try:
            cur.execute("""DELETE FROM subscribers WHERE roomid = (%s)""", (db_entry,))
            con.commit()
            log(incoming_msg, severity=0, personId="", infoMsg="Subscriber database updated.")
            # send success message
            text="Thank you, you sucessfully unsubscribed from GoCSAP bot updates."
            api.messages.create(roomId=roomId, text=text)    
            # delete card
            api.messages.delete(messageId=m["messageId"])    
            return ""
        except:
            # delete card
            api.messages.delete(messageId=m["messageId"]) 
            return "Thank you, you successfully unsubscribed from GoCSAP bot updates."

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
                return "Oops, it seems like you didn't fill out all required fields. Please verify your entries and re-submit the notification."
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
                                   button1_url=parse[9], button2_url=parse[10], button3_url=parse[11],
                                   msg_id=parse[12], isVisible="false")
            backupmessage = "Hi there! 👋 The GoCSAP bot just sent you a card."
            
            text="Notification {} was approved and sent to bot subscribers! 🎉".format(parse[12])
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
    
    
    elif "approve_admin" in m["inputs"]:
        requestor = m["inputs"].split(" ")[1]
        level = m["inputs"].split(" ")[2]
        if level == "admin":
            if check_permission(email=requestor) == "Authorized":
                text = "{} is already an admin.".format(requestor)
                api.messages.delete(messageId=m["messageId"])    
                return text
            else:
                cur.execute("""INSERT INTO admins (email, personid, since, role) VALUES (%s, %s, %s, %s)""", (requestor, "", date.today().strftime("%d%m%Y"), "admin"))
                con.commit()
                
                text="Hurray, you are now registered as an **admin** for the GoCSAP bot! 🎉 \nYou can now type **send notif** to submit notifications and type **analytics** to view GoCSAP bot analytics"
                api.messages.create(toPersonEmail=requestor, 
                                     markdown=text)    
                
                api.messages.delete(messageId=m["messageId"])  
                text = "Thank you, {} is now an admin for the GoCSAP bot.".format(requestor)
                return text
            
        if level == "superadmin":
            if check_permission(email=requestor, level="superadmin") == "Authorized":
                text = "{} is already a superadmin.".format(requestor)
                api.messages.delete(messageId=m["messageId"])    
                return text
            else:
                cur.execute("""INSERT INTO admins (email, personid, since, role) VALUES (%s, %s, %s, %s)""", (requestor, "", date.today().strftime("%d%m%Y"), "superadmin"))
                con.commit()
                
                text="Hurray, you are now registered as a **superadmin** for the GoCSAP bot! 🎉 \nYou can now type **send notif** to submit notifications, type **analytics** to view GoCSAP bot analytics and receive requests for approving new admins."
                api.messages.create(toPersonEmail=requestor, 
                                     markdown=text)    
                
                api.messages.delete(messageId=m["messageId"])  
                text = "Thank you, {} is now a superadmin for the GoCSAP bot.".format(requestor)
                return text            

    elif "decline_admin" in m["inputs"]:
        requestor = m["inputs"].split(" ")[1]
        level = m["inputs"].split(" ")[2]
        api.messages.delete(messageId=m["messageId"]) 
        text = "The {} request for {} has been successfully declined.".format(level, requestor)
        return text
    
    elif m["inputs"] == "pull_report":
        today_date = date.today().strftime("%d %B %Y")
        # nr subscribers
        cur.execute("""SELECT COUNT (*) FROM subscribers;""")
        nr_subscribers = cur.fetchall()[0][0]
        # nr admins
        cur.execute("""SELECT COUNT (*) FROM admins WHERE role='admin';""")
        nr_admins = cur.fetchall()[0][0]
        # nr superadmins
        cur.execute("""SELECT COUNT (*) FROM admins WHERE role='superadmin';""")
        nr_superadmins = cur.fetchall()[0][0]
        
        admins = []
        cur.execute("""SELECT email, since FROM admins WHERE role='admin';""")
        result = cur.fetchall()
        for element in result:
            for person in element:
                admins.append(person)
        
        superadmins = []
        cur.execute("""SELECT email, since FROM admins WHERE role='superadmin';""")
        result = cur.fetchall()
        for element in result:
            for person in element:
                superadmins.append(person)        
        
        workbook = xlsxwriter.Workbook('GoCSAP_botAnalytics_'+date.today().strftime("%d%m%Y")+'.xlsx')
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        worksheet.set_column(0, 0, 22)
        worksheet.set_column(3, 3, 22)
        
        # title
        worksheet.write(0, 0, "GoCSAP Bot Analytics "+date.today().strftime("%d %B %Y"), bold)
        
        worksheet.write(2, 0, "Total subscribers:")
        worksheet.write(2, 1, nr_subscribers)

        worksheet.write(4, 0, "Total admins:")
        worksheet.write(4, 1, nr_admins)        
        
        worksheet.write(5, 0, "Total superadmins:")
        worksheet.write(5, 1, nr_superadmins)        
        
        # list of admins
        worksheet.write(7, 0, "Admin email", bold)
        worksheet.write(7, 1, "Admin since", bold)
        row = 8
        col = 0
        i = 0
        for person in admins:
            worksheet.write(row, col, person)
            if i == 0:
                col += 1
                i += 1
            else:
                i = 0
                col = 0
                row += 1
        
        # list of superadmins
        worksheet.write(7, 3, "Superadmin email", bold)
        worksheet.write(7, 4, "Superadmin since", bold)
        row = 8
        col = 3
        i = 0
        for person in superadmins:
            worksheet.write(row, col, person)
            if i == 0:
                col += 1
                i += 1
            else:
                i = 0
                col = 3
                row += 1
        workbook.close()
        
        api.messages.delete(messageId=m["messageId"]) 
        
        text = "Please find your detailed GoCSAP bot analytics report attached. 📊"
        personId = m["personId"]
        api.messages.create(toPersonId=personId, 
                            text=text, files=['GoCSAP_botAnalytics_'+date.today().strftime("%d%m%Y")+'.xlsx'])    
        return ""
        
        
        
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
                                   msg_id=parse[12], isVisible="true")   
    print(7)
    backupmessage = "Hi there! 👋 The GoCSAP bot just sent you a card."
    
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

def create_message_with_attachment(rid, msgtxt, attachment, toPersonEmail=""):
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": "Bearer " + bot_token,
    }

    url = "https://api.ciscospark.com/v1/messages"
    if toPersonEmail == "":
        data = {"roomId": rid, "attachments": [attachment], "markdown": msgtxt}
    else:
        data = {"toPersonEmail": toPersonEmail, "attachments": [attachment], "markdown": msgtxt}
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
        log(incoming_msg, severity=0, personId="", infoMsg="Subscriber database updated.", personEmail=incoming_msg.personEmail)
    except:
        print("Could not be added to DB")
        
    return "Thank you, you sucessfully subscribed to CSAP bot updates. 🥳"

def unsubscribe(incoming_msg):
    fetch_infos(incoming_msg)
    db_entry = roomId

    try:
        cur.execute("""DELETE FROM subscribers WHERE roomid = (%s)""", (db_entry,))
        con.commit()
        log(incoming_msg, severity=0, personId="", infoMsg="Subscriber database updated.", personEmail=incoming_msg.personEmail)
    except:
        print("Could not be removed from DB")
    return "Thank you, you sucessfully unsubscribed from CSAP bot updates."  

def help(incoming_msg):
    if check_permission(email=incoming_msg.personEmail, level="superadmin") == "Authorized":
        admin_info = "As superadmin you can send notifications to bot subscribers, view bot analytics and grant/revoke admin access."
        attachment = help_card_admin.format(level="superadmin", adminInfo=admin_info)
        backupmessage = "Hi there! 👋 The GoCSAP bot just sent some help."

        c = create_message_with_attachment(
            incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
        )    
    elif check_permission(email=incoming_msg.personEmail) == "Authorized":
        admin_info = "As admin you can send notifications to bot subscribers and view bot analytics."
        attachment = help_card_admin.format(level="admin", adminInfo=admin_info)
        backupmessage = "Hi there! 👋 The GoCSAP bot just sent some help."

        c = create_message_with_attachment(
            incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
        )    
    else:
        attachment = help_card
        backupmessage = "Hi there! 👋 The GoCSAP bot just sent some help."

        c = create_message_with_attachment(
            incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
        )    
    
    return ""

def contact(incoming_msg):
    fetch_infos(incoming_msg)
    return "Thank you {} for using the CSAP bot! \n Current version is v1.0. \n Please contact elandman@cisco.com for more information or for feedback and improvement suggestions.".format(firstName)

def fetch_infos(incoming_msg):
    global sender, firstName, room, roomId, personId, email
    sender, firstName, room, roomId = None, None, None, None
    sender = bot.teams.people.get(incoming_msg.personId)
    personId = sender.id
    email = sender.emails
    firstName = sender.firstName
    room = bot.teams.rooms.get(incoming_msg.roomId)
    roomId = room.id
    return sender, firstName, room, roomId, email, personId

def send_notif(incoming_msg):
    person = bot.teams.people.get(incoming_msg.personId)
    personId = person.id
    attachment = send_card
    backupmessage = "Hi there! 👋 You requested to create a notification through the GoCSAP bot."

    c = create_message_with_attachment(incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment))  
    log(incoming_msg, severity=1, personId=personId, infoMsg="Notification request made.", personEmail=incoming_msg.personEmail)
    
    return ""   

def log(incoming_msg, severity, personId, infoMsg="", personEmail = ""):
    # function for logging al things sent with the bot
    # severity 0, 1, 2, 3 (0=informational, ..., 3=emergency)
    with open(logs) as json_file:
        data = json.load(json_file)
    now = datetime.now()
    logDate = now.strftime("%d%m%Y-%H:%M")   
    
    data[logDate] = {"date": now.strftime("%d-%m-%Y"),
                     "severity": severity,
                     "infoMsg": infoMsg,
                     "personEmail": personEmail,
                     "personId": personId}
    
    with open(logs, 'w') as outfile:
        json.dump(data, outfile)    

def check_permission(personId="", email="", level="admin"):
    if personId != "":
        if level == "superadmin":
            cur.execute("""SELECT personid FROM admins WHERE role='superadmin';""")
            superAdminList = cur.fetchall()            
            for elements in superAdminList:
                for superAdmin in elements:
                    if personId == superAdmin:
                        return "Authorized"
            return "Unauthorized"
        else:
            cur.execute("""SELECT personid FROM admins;""")
            adminList = cur.fetchall()
            for elements in adminList:
                for admin in elements:
                    if personId == admin:
                        return "Authorized"
            return "Unauthorized"  
        
    elif email != "":
        if level == "superadmin":
            cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
            superAdminList = cur.fetchall()            
            for elements in superAdminList:
                for superAdmin in elements:
                    if email == superAdmin:
                        return "Authorized"
            return "Unauthorized"
        else:
            cur.execute("""SELECT email FROM admins;""")
            adminList = cur.fetchall()
            for elements in adminList:
                for admin in elements:
                    if email == admin:
                        return "Authorized"
            return "Unauthorized"            
    else:
        return "Unauthorized"    
    
def valid_email(email):  
    if(re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]cisco[.]\w{2,3}$', email)):  
        return "valid"
          
    else:  
        return "invalid" 
    
def request_admin_access(incoming_msg):
    request = incoming_msg.text
    request = request.split(" ")
    
    # request for someone else
    if len(request) > 2:
        reqEmail = request[2]
        if valid_email(reqEmail) == "valid":
            if request[1] == "admin":
                print(reqEmail)
                if check_permission(email=reqEmail) == "Authorized":
                    text = "{} is already an admin. Use the *cancel admin* command to revoke admin rights.".format(reqEmail)
                    return text
                else:
                    # fetch list of all superadmins to send request to
                    cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
                    superAdminList = cur.fetchall() 
                    
                    attachment = request_admin_card.format(requestor=reqEmail, level="admin")
                    backupmessage = "Hi admin! 👋 Someone requested admin access and your approval is required."
                    
                    # send request to all superadmins
                    for element in superAdminList:
                        for email in element:    
                            c = create_message_with_attachment(incoming_msg.roomId, 
                                                           msgtxt=backupmessage, 
                                                           attachment=json.loads(attachment), 
                                                           toPersonEmail=email)  
                    log(incoming_msg, severity=2, personId=incoming_msg.personId, infoMsg="New admin request submitted.", personEmail=incoming_msg.personEmail)                    

                    # send confimation to requestor if requestor is not superadmin
                    for element in superAdminList:
                        for email in element:
                            if incoming_msg.personEmail == email:
                                return ""
                    text="Thank you, your request for admin access for {} has been forwarded! Once the request has been approved/declined {} will receive a notification.".format(reqEmail, reqEmail)
                    return text
                
            elif request[1] == "superadmin":
                if check_permission(email=reqEmail, level="superadmin") == "Authorized":
                    text = "{} is already a superadmin. Use the *cancel admin* command to revoke admin rights.".format(reqEmail)
                    return text
                else:
                    # fetch list of all superadmins to send request to
                    cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
                    superAdminList = cur.fetchall() 
                    
                    attachment = request_admin_card.format(requestor=reqEmail, level="superadmin")
                    backupmessage = "Hi admin! 👋 Someone requested admin access and your approval is required."
                    
                    # send request to all superadmins
                    for element in superAdminList:
                        for email in element: 
                            c = create_message_with_attachment(incoming_msg.roomId, 
                                                               msgtxt=backupmessage, 
                                                               attachment=json.loads(attachment), 
                                                               toPersonEmail=email)  
                    log(incoming_msg, severity=2, personId=incoming_msg.personId, infoMsg="New superadmin request submitted.", personEmail=incoming_msg.personEmail)                    

                    # send confim ation to requestor
                    for element in superAdminList:
                        for email in element:
                            if incoming_msg.personEmail == email:
                                return ""
                    text="Thank you, your request for superadmin access for {} has been forwarded! Once the request has been approved/declined {} will receive a notification.".format(reqEmail, reqEmail)
                    return text 
            
            else:
                return "Oops, something went wrong 😢"

        else:
            text = "{} is not a valid email address. Admin rights are reserved for Cisco employees with a valid email address only. Please try again.".format(reqEmail)
            return text
    else:
        reqEmail = incoming_msg.personEmail
        print(incoming_msg)
        if valid_email(reqEmail) == "valid":
            if request[1] == "admin":
                if check_permission(email=reqEmail) == "Authorized":
                    text = "You are already an admin. Use the *cancel admin* command to revoke admin rights.".format(reqEmail)
                    return text
                else:
                    # fetch list of all superadmins to send request to
                    cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
                    superAdminList = cur.fetchall() 
                    
                    attachment = request_admin_card.format(requestor=reqEmail, level="admin")
                    backupmessage = "Hi admin! 👋 Someone requested admin access and your approval is required."
                    
                    # send request to all superadmins
                    for element in superAdminList:
                        for email in element: 
                            c = create_message_with_attachment(incoming_msg.roomId, 
                                                               msgtxt=backupmessage, 
                                                               attachment=json.loads(attachment), 
                                                               toPersonEmail=email)  
                    log(incoming_msg, severity=2, personId=incoming_msg.personId, infoMsg="New admin request submitted.", personEmail=incoming_msg.personEmail)                    

                    # send confim ation to requestor
                    text="Thank you, your request for admin access has been forwarded! Once your request has been approved/declined you will receive a notification."
                    return text
                
            elif request[1] == "superadmin":
                if check_permission(email=incoming_msg.personEmail, level="superadmin") == "Authorized":
                    text = "You are already a superadmin. Use the *cancel admin* command to revoke admin rights.".format(reqEmail)
                    return text
                else:
                    # fetch list of all superadmins to send request to
                    cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
                    superAdminList = cur.fetchall() 
                    
                    attachment = request_admin_card.format(requestor=reqEmail, level="superadmin")
                    backupmessage = "Hi admin! 👋 Someone requested admin access and your approval is required."
                    
                    # send request to all superadmins
                    for element in superAdminList:
                        for email in element: 
                            c = create_message_with_attachment(incoming_msg.roomId, 
                                                               msgtxt=backupmessage, 
                                                               attachment=json.loads(attachment), 
                                                               toPersonEmail=email)  
                    log(incoming_msg, severity=2, personId=incoming_msg.personId, infoMsg="New superadmin request submitted.", personEmail=incoming_msg.personEmail)                    

                    # send confim ation to requestor
                    text="Thank you, your request for superadmin access has been forwarded! Once your request has been approved/declined you will receive a notification."
                    return text 
            
            else:
                return "Oops, something went wrong 😢"

        else:
            text = "Your email address is invalid. Admin rights are reserved for Cisco employees with a valid email address only."
            return text

def cancel_admin_access(incoming_msg):
    request = incoming_msg.text
    request = request.split(" ")

    # check if this is the last superadmin in the DB
    cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
    superAdminList = cur.fetchall() 
    if len(superAdminList) == 1:
        for element in superAdminList:
            for email in element:
                if len(request) > 2:
                    if email == request[2]:
                        text = "{} is the only superadmin for the GoCSAP bot. At least one superadmin is required, therefore its access cannot be revoked. {} can add a second superadmin by typing the command **make superadmin** followed by an email address.".format(request[2], request[2])
                        return text
                else:
                    if email == incoming_msg.personEmail:
                        text = "You are the only superadmin for the GoCSAP bot. At least one superadmin is required, therefore your access cannot be revoked. You can add a second superadmin by typing the command **make superadmin** followed by an email address."
                        return text    
                        
    # request for someone else, superadmin right required
    if len(request) > 2:
        # check if superadmin
        if check_permission(email=incoming_msg.personEmail, level="superadmin") == "Authorized":
            reqEmail = request[2]
            if check_permission(email=reqEmail) == "Authorized":
                cur.execute("""DELETE FROM admins WHERE email = (%s)""", (reqEmail,))
                con.commit()
                
                text="Your admin access for the GoCSAP bot has been revoked."
                api.messages.create(toPersonEmail=reqEmail, 
                                    text=text)    
                
                log(incoming_msg, severity=2, personId="", infoMsg="Admin access revoked for {}.".format(reqEmail), personEmail=incoming_msg.personEmail)

                text = "Admin access for {} has successfully been revoked.".format(reqEmail)
                return text
            else:       
                text = "{} is not an admin.".format(reqEmail)
                return text
        else:
            # not a superadmin
            log(incoming_msg, severity=2, personId="", infoMsg="No permission to revoke admin access.", personEmail=incoming_msg.personEmail)
            text = "You do not have permission to revoke someone else's admin access. Only superadmins can grant and revoke admin access."
            return text
        
    # revoke my own access
    else:
        reqEmail = incoming_msg.personEmail
        if check_permission(email=reqEmail) == "Authorized":
            cur.execute("""DELETE FROM admins WHERE email = (%s)""", (reqEmail,))
            con.commit()
            log(incoming_msg, severity=2, personId="", infoMsg="Admin rights revoked for {}.".format(reqEmail), personEmail=incoming_msg.personEmail)

            text = "Your admin access has successfully been revoked.".format(reqEmail)
            return text
        else:       
            text = "You are not an admin.".format(reqEmail)
            return text            

def admin_analytics(incoming_msg):
    reqEmail = incoming_msg.personEmail
    if check_permission(email=reqEmail) == "Authorized":
        
        today_date = date.today().strftime("%d %B %Y")
        # nr subscribers
        cur.execute("""SELECT COUNT (*) FROM subscribers;""")
        nr_subscribers = cur.fetchall()[0][0]
        # nr admins
        cur.execute("""SELECT COUNT (*) FROM admins WHERE role='admin';""")
        nr_admins = cur.fetchall()[0][0]
        # nr superadmins
        cur.execute("""SELECT COUNT (*) FROM admins WHERE role='superadmin';""")
        nr_superadmins = cur.fetchall()[0][0]
        
        
        attachment = analytics_card.format(today_date=today_date, nr_subscribers=nr_subscribers, 
                                           nr_admins=nr_admins, nr_superadmins=nr_superadmins)
        backupmessage = "Hi admin! 👋 Here are the GoCSAP bot analytics you requested."

        log(incoming_msg, severity=1, personId=incoming_msg.personId, infoMsg="Analytics requested with success.", personEmail=incoming_msg.personEmail)

        c = create_message_with_attachment(
            incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
        )    

        return ""       
    else:
        log(incoming_msg, severity=2, personId=incoming_msg.personId, infoMsg="Analytics requested without permission.", personEmail=incoming_msg.personEmail)
        text = "You do not have permission to view GoCSAP bot analytics. You can request admin access by typing **make admin**.".format(reqEmail)
        return text    
    
def joke(incoming_msg):
    f = "https://official-joke-api.appspot.com/random_ten"
    data = requests.get(f)
    result = json.loads(data.text)
    result = result[0]

    setup = result["setup"]
    punchline = result["punchline"]

    text = "Ha, so you want to hear a joke? 😃"
    api.messages.create(toPersonId=incoming_msg.personId, 
                        text=text) 
    time.sleep(1.5)
    text = "{}".format(setup)
    api.messages.create(toPersonId=incoming_msg.personId, 
                        text=text)  
    time.sleep(3)
    text = "{}".format(punchline)    
    api.messages.create(toPersonId=incoming_msg.personId, 
                        text=text)
    time.sleep(1)
    return "😂"

def logfile(incoming_msg):
    reqEmail = incoming_msg.personEmail
    if check_permission(email=reqEmail, level="superadmin") == "Authorized":  
        log(incoming_msg, severity=2, personId=incoming_msg.personId, infoMsg="Logfile requested by superadmin.", personEmail=incoming_msg.personEmail)
        text = "Please find the GoCSAP bot logfile attached."
        api.messages.create(toPersonEmail=reqEmail, 
                            text=text, files=['logs.txt'])    
        return ""
    else:
        text = "You do not have permission to view the GoCSAP bot logfile. Please request superadmin acces by typing **make superadmin**."
        log(incoming_msg, severity=3, personId=incoming_msg.personId, infoMsg="Logfile requested without permission.", personEmail=incoming_msg.personEmail)
        return text

bot.set_greeting(greeting)
bot.add_command("attachmentActions", "*", handle_cards)
bot.add_command("help", "Help", help)
bot.add_command("contact", "Contact", contact)
bot.add_command("subscribe", "subscribe", subscribe)
bot.add_command("unsubscribe", "unsubscribe", unsubscribe)
bot.add_command("send notif", "Send notif", send_notif)
bot.add_command("make admin", "make admin", request_admin_access)
bot.add_command("make superadmin", "make superadmin", request_admin_access)
bot.add_command("cancel admin", "cancel admin", cancel_admin_access)
bot.add_command("analytics", "analytics", admin_analytics)
bot.add_command("logfile", "logfile", logfile)
bot.add_command("joke", "joke", joke)


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

help_card_admin = """
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
                                    "width": "stretch",
                                    "items": [
                                        {{
                                            "type": "TextBlock",
                                            "text": "GoCSAP Bot",
                                            "weight": "Lighter",
                                            "color": "Accent"
                                        }},
                                        {{
                                            "type": "TextBlock",
                                            "weight": "Bolder",
                                            "text": "Admin Help",
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
            "text": "Hello! 👋 I'm your GoCSAP bot. You can **subscribe** to receive updates and latest news from within the CSAP program.",
            "wrap": true
        }},
        {{
            "type": "TextBlock",
            "text": "Your current GoCSAP bot access level: **{level}**. {adminInfo}",
            "wrap": true
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.ShowCard",
                    "title": "View Commands",
                    "card": {{
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "body": [
                            {{
                                "type": "TextBlock",
                                "text": "🙋 **I understand the following commands:**",
                                "spacing": "ExtraLarge"
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`subscribe`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Subscribe to GoCSAP bot updates.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`unsubscribe`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Unsubscribe from GoCSAP bot updates."
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`help`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Open GoCSAP bot information."
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`contact`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Contact the team behind the GoCSAP bot.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`make admin`"
                                            }},
                                            {{
                                                "type": "TextBlock",
                                                "text": "`make superadmin`",
                                                "spacing": "None"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Submit a request for GoCSAP bot admin access. Followed by a Cisco email address when requesting for someone else.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }}
                        ]
                    }}
                }}
            ],
            "spacing": "Small"
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.ShowCard",
                    "title": "View Admin Commands",
                    "card": {{
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "body": [
                            {{
                                "type": "TextBlock",
                                "text": "🔥 **I understand the following admin commands:**"
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`send notif`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Submit a notification to be sent to all GoCSAP bot subscribers.",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`analytics`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "auto",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Request GoCSAP bot analytics."
                                            }}
                                        ]
                                    }}
                                ]
                            }},
                            {{
                                "type": "ColumnSet",
                                "columns": [
                                    {{
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "`cancel admin`"
                                            }}
                                        ]
                                    }},
                                    {{
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {{
                                                "type": "TextBlock",
                                                "text": "Revoke all admin rights. Followed by a Cisco email address when revoking for someone else (only superadmins can revoke for someone else).",
                                                "wrap": true
                                            }}
                                        ]
                                    }}
                                ]
                            }}
                        ]
                    }}
                }}
            ],
            "spacing": "None"
        }}
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """

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

analytics_card = """
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
                            "type": "TextBlock",
                            "text": "GoCSAP Bot, {today_date}",
                            "weight": "Lighter",
                            "color": "Accent"
                        }},
                        {{
                            "type": "TextBlock",
                            "weight": "Bolder",
                            "text": "Admin Analytics",
                            "horizontalAlignment": "Left",
                            "wrap": true,
                            "color": "Light",
                            "size": "Large",
                            "spacing": "Small"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "📊 Welcome to the GoCSAP bot admin analytics. You can view a summary of statistics below, or pull a detailed report by clicking the **Pull Report** button.",
                            "wrap": true
                        }}
                    ],
                    "width": "stretch"
                }}
            ]
        }},
        {{
            "type": "ColumnSet",
            "columns": [
                {{
                    "type": "Column",
                    "width": 35,
                    "items": [
                        {{
                            "type": "TextBlock",
                            "text": "Total subscribers:",
                            "spacing": "Small"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "Total admins:",
                            "spacing": "ExtraLarge"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "Total superadmins:",
                            "spacing": "Small"
                        }}
                    ]
                }},
                {{
                    "type": "Column",
                    "width": 50,
                    "items": [
                        {{
                            "type": "TextBlock",
                            "text": "{nr_subscribers}",
                            "spacing": "Small"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "{nr_admins}",
                            "spacing": "ExtraLarge"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "{nr_superadmins}",
                            "spacing": "Small"
                        }}
                    ]
                }}
            ],
            "spacing": "Padding",
            "horizontalAlignment": "Center"
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.Submit",
                    "title": "Pull Report",
                    "data":  "pull_report"
                }}
            ],
            "horizontalAlignment": "Left",
            "spacing": "None"
        }}
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """ #.format(test="ALOHA")

request_admin_card = """
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
                            "type": "TextBlock",
                            "weight": "Bolder",
                            "text": "New {level} access request",
                            "horizontalAlignment": "Left",
                            "wrap": true,
                            "color": "Light",
                            "size": "Large",
                            "spacing": "Small"
                        }},
                        {{
                            "type": "TextBlock",
                            "text": "**{requestor}** requested **{level}** access to the GoCSAP bot. Please approve or decline the request.",
                            "wrap": true
                        }}
                    ],
                    "width": "stretch"
                }}
            ]
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.ShowCard",
                    "title": "What is this?",
                    "card": {{
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "body": [
                            {{
                                "type": "TextBlock",
                                "text": "You are a superadmin for the CSAP bot, therefore your approval is required when admin/superadmin requests are submitted.",
                                "wrap": true
                            }},
                            {{
                                "type": "FactSet",
                                "facts": [
                                    {{
                                        "title": "Admin",
                                        "value": "Can submit notifications through the CSAP bot to all bot subscribers."
                                    }},
                                    {{
                                        "title": "Superadmin",
                                        "value": "Have admin rights, can approve new admins/superadmins and have access to admin/superadmin records."
                                    }}
                                ]
                            }}
                        ]
                    }}
                }}
            ],
            "spacing": "None"
        }},
        {{
            "type": "ActionSet",
            "actions": [
                {{
                    "type": "Action.Submit",
                    "title": "Decline",
                    "id": "Decline",
                    "data": "decline_admin {requestor} {level}"
                }},
                {{
                    "type": "Action.Submit",
                    "title": "Approve",
                    "id": "Approve",
                    "data": "approve_admin {requestor} {level}"
                }}
            ],
            "spacing": "None",
            "horizontalAlignment": "Left"
        }}
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}}
    }}
  """

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
            "color": "Light",
            "isVisible": {isVisible}
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
                                            "text": "GoCSAP Bot",
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
            "text": "Hello! 👋 I'm your GoCSAP bot. You can **subscribe** to receive updates and latest news from within the CSAP program.",
            "wrap": true
        },
        {
            "type": "TextBlock",
            "text": "I was especially designed to keep you up to date on the most important topics around CSAP. ",
            "wrap": true
        },
        {
            "type": "ActionSet",
            "actions": [
                {
                    "type": "Action.ShowCard",
                    "title": "View Commands",
                    "card": {
                        "type": "AdaptiveCard",
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "body": [
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
                                        "width": "130px",
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
                                                "text": "Subscribe to GoCSAP bot updates.",
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
                                        "width": "130px",
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
                                                "text": "Unsubscribe from GoCSAP bot updates."
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
                                        "width": "130px",
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
                                                "text": "Open GoCSAP bot information."
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
                                        "width": "130px",
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
                                "type": "ColumnSet",
                                "columns": [
                                    {
                                        "type": "Column",
                                        "width": "130px",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "`make admin`"
                                            },
                                            {
                                                "type": "TextBlock",
                                                "text": "`make superadmin`",
                                                "spacing": "None"
                                            }
                                        ]
                                    },
                                    {
                                        "type": "Column",
                                        "width": "stretch",
                                        "items": [
                                            {
                                                "type": "TextBlock",
                                                "text": "Submit a request for GoCSAP bot admin access. Followed by a Cisco email address when requesting for someone else.",
                                                "wrap": true
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            ],
            "spacing": "Small"
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