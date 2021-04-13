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
from notif_templates import * 
from bot_cards import * 

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

    reqEmail = incoming_msg.personEmail
    print(reqEmail + ": " + check_permission(email=reqEmail))

    api.messages.create(roomId=incoming_msg.roomId, 
            text="⚠️ The bot is currently is maintenance mode. Please do not use it. Contact elandman@cisco.com for more info.") 

    c = create_message_with_attachment(
        incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
    )
    
    return ""

def handle_cards(api, incoming_msg):
    m = get_attachment_actions(incoming_msg["data"]["id"])
    personId = m["personId"]
    roomId = m["roomId"]
    db_entry = (str(roomId))

    if m["inputs"] == "subscribe":
        try:
            cur.execute("""INSERT INTO testing (roomid) VALUES (%s)""", (db_entry,))
            log(severity=0, infoMsg="Subscriber database updated.", personId=personId)
            return ""
        except:
            con.rollback()
            log(severity=3, infoMsg="Failed to update database of testers.", personId=personId) 
        finally:
            con.commit()
            # delete card
            api.messages.delete(messageId=m["messageId"])  
            # send success message
            return "Thank you, you successfully subscribed to GoCSAP bot updates. 🥳"
            
    elif m["inputs"] == "unsubscribe":    
        try:
            cur.execute("""DELETE FROM testing WHERE roomid = (%s)""", (db_entry,))
            log(severity=0, infoMsg="Tester database updated.", personId=personId)
            # send success message
            return ""
        except:  
            con.rollback()
            log(severity=3, infoMsg="Failed to update database of testers.", personId=personId) 
        finally:
            con.commit() 
            # delete card
            api.messages.delete(messageId=m["messageId"]) 
            # send success message
            return "Thank you, you successfully unsubscribed from GoCSAP bot updates. 😢"

    elif "{'textbox_1_card_1':" in str(m["inputs"]):    
        log(severity=1, infoMsg="New notification submitted.", personId=personId)
        
        parse = []
        image_url = m["inputs"]["image_url"]
        small_title = m["inputs"]["small_title"]
        main_title = m["inputs"]["main_title"]
        textbox_1 = m["inputs"]["textbox_1_card_1"]
        textbox_1 = textbox_1.replace("\n", "\\r\\n").replace('"', '“')

        textbox_2 = m["inputs"]["textbox_2"]
        textbox_2 = textbox_2.replace("\n", "\\r\\n").replace('"', '“')

        textbox_3 = m["inputs"]["textbox_3"]
        textbox_3 = textbox_3.replace("\n", "\\r\\n").replace('"', '“')

        button1_text = m["inputs"]["button1_text"]
        button2_text = m["inputs"]["button2_text"]
        # button3_text = m["inputs"]["button3_text"]
        button1_url = m["inputs"]["button1_url"]
        button2_url = m["inputs"]["button2_url"]
        # button3_url = m["inputs"]["button3_url"]   
        review = m["inputs"]["review"]   

        # correct URL is invalid
        if "https" not in image_url:
            image_url = "https://" + image_url
        if "https" not in button1_url:
            button1_url = "https://" + button1_url
        if "https" not in button2_url:
            button2_url = "https://" + button2_url
        # if "https" not in button3_url:
        #     button3_url = "https://" + button3_url

        parse.extend([image_url, small_title, main_title, textbox_1, textbox_2, textbox_3, button1_text, button2_text,
                     button1_url, button2_url])
        
        for element in parse:
            if element == "" or element == " ":
                return "Oops, it seems like you didn't fill out all required fields. Please verify your entries and re-submit the notification."

        parse_msg(incoming_msg, parse, roomId, review, template="1", personId=personId)

        return ""

    elif "{'textbox_1_card_2':" in str(m["inputs"]):
        
        log(severity=1, infoMsg="New notification submitted.", personId=personId)
        
        parse = []
        main_title = m["inputs"]["main_title"]
        textbox_1 = m["inputs"]["textbox_1_card_2"]
        textbox_1 = textbox_1.replace("\n", "\\r\\n").replace('"', '“')
        
        review = m["inputs"]["review"]   

        parse.extend([main_title, textbox_1])
        
        for element in parse:
            if element == "" or element == " ":
                return "Oops, it seems like you didn't fill out all required fields. Please verify your entries and re-submit the notification."

        parse_msg(incoming_msg, parse, roomId, review, template="2", personId=personId)

        return ""

    elif "{'textbox_1_card_own':" in str(m["inputs"]):
        
        log(severity=1, infoMsg="New notification submitted.", personId=personId)
        
        parse = []
        textbox_1 = m["inputs"]["textbox_1_card_own"]
        
        review = m["inputs"]["review"]   

        parse.extend([textbox_1])
        
        for element in parse:
            if element == "" or element == " ":
                return "Oops, it seems like you didn't fill out all required fields. Please verify your entries and re-submit the notification."

        parse_msg(incoming_msg, parse, roomId, review, template="own", personId=personId)

        return ""
    
    ### add new template here

    elif m["inputs"] == "approve_msg":
        with open('parse.pkl', 'rb') as f:
            parse = pickle.load(f)        

        # check if message approval comes from same room, so no confusion in case multiple people use bot
        # at the same time
        if roomId == parse[-2]:
            # check which template has been chosen
            if parse[-1] == "1":
                attachment = notif_card_1.format(image_url=parse[0], small_title=parse[1], main_title=parse[2], 
                                          textbox_1=parse[3], textbox_2=parse[4], textbox_3=parse[5], 
                                          button1_text=parse[6], button2_text=parse[7], 
                                          button1_url=parse[8], button2_url=parse[9],
                                          msg_id=parse[10], isVisible="false")
            elif parse[-1] == "2":
                attachment = notif_card_2.format(main_title=parse[0], textbox_1=parse[1], 
                                                 msg_id=parse[2], isVisible="false")

            elif parse[-1] == "own":
                attachment = parse[0]
                attachment = '{"contentType": "application/vnd.microsoft.card.adaptive","content":' + attachment
                attachment = attachment + "}" 

            backupmessage = "Hi there! 👋 The GoCSAP bot just sent you a card."         
            
            roomMsgs = api.messages.list(roomId=roomId)
            for count, msg in enumerate(roomMsgs):
                if count == 0:
                    delMsg1  = msg.id
                elif count == 1:
                    delMsg2  = msg.id
                else:
                    break
                    
            api.messages.delete(messageId=delMsg1)     
            api.messages.delete(messageId=delMsg2)    
            os.remove("parse.pkl")    
            
            text="Notification {} was approved and sent to bot testers! 🎉".format(parse[-3])
            api.messages.create(roomId=roomId, 
                                 text=text)               
            
            cur.execute("""SELECT roomId FROM testing;""")
            result = cur.fetchall()
            for element in result:
                for roomId in element:
                    c = create_message_with_attachment(
                        roomId, msgtxt=backupmessage, attachment=json.loads(attachment)
                    ) 

            log(severity=1, infoMsg="Notification approved and sent. Notification Id: {}".format(parse[-3]), personId=personId)
            return ""      
        
        else:
            api.messages.delete(messageId=m["messageId"])    
            log(severity=2, infoMsg="Notification approved without permission. Not sent.", personId=personId)
            return "Oops, you do not have permission to approve the notification!"

    elif m["inputs"] == "decline_msg":

        roomMsgs = api.messages.list(roomId=roomId)
        for count, msg in enumerate(roomMsgs):
            if count == 0:
                delMsg1  = msg.id
            elif count == 1:
                delMsg2  = msg.id
            else:
                break
                
        api.messages.delete(messageId=delMsg1)     
        api.messages.delete(messageId=delMsg2)    
        os.remove("parse.pkl")   
        
        log(severity=2, infoMsg="Notification declined and not sent.", personId=personId)   
        
        return "Notification declined and not sent 😞"
    
    elif "approve_admin" in m["inputs"]:
        requestor = m["inputs"].split(" ")[1]
        level = m["inputs"].split(" ")[2]
        if level == "admin":
            if check_permission(email=requestor) == "Authorized":
                text = "{} is already an admin.".format(requestor)
                api.messages.delete(messageId=m["messageId"])    
                return text
            # check if requestor is already a superadmin, if yes, update records to admin
            elif check_permission(email=requestor, level="superadmin") == "Authorized":
                try:
                    cur.execute("""UPDATE admins SET role =  (%s) WHERE email = (%s)""", ("admin", requestor))
                    log(severity=2, infoMsg="Superadmin downgraded to admin: {}.".format(requestor), personId=personId)
                    text="Your access level for the GoCSAP bot has been changed to **admin**! \nYou can now type **send notif** to submit notifications and type **analytics** to view GoCSAP bot analytics."
                    api.messages.create(toPersonEmail=requestor, 
                                        markdown=text)                        
                except:
                    cur.rollback()
                    log(severity=3, infoMsg="Failed to update database of admins: {}.".format(requestor), personId=personId)  
                    text = ""     
                finally:
                    con.commit()
                    
                    # fetch list of all superadmins
                    cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
                    superAdminList = cur.fetchall() 

                    # send approval info to all superadmins
                    text = "The {} request for {} has been successfully approved.".format(level, requestor)
                    
                    for element in superAdminList:
                        for email in element:
                            # delete approval request card 
                            roomMsgs = api.messages.list_direct(personEmail=email)
                            for count, msg in enumerate(roomMsgs):
                                # check last 10 messages
                                if count < 10:
                                    try:
                                        if requestor in msg.attachments[0]["content"]["body"][0]["columns"][0]["items"][1]["text"]:
                                            api.messages.delete(messageId=msg.id)
                                    except:
                                        continue

                            api.messages.create(toPersonEmail=email, 
                                                markdown=text)

                    return ""                             
            # new admin
            else:
                try:
                    cur.execute("""INSERT INTO admins (email, personid, since, role) VALUES (%s, %s, %s, %s)""", (requestor, "", date.today().strftime("%d%m%Y"), "admin"))
                    log(severity=2, infoMsg="New admin added: {}.".format(requestor), personId=personId)
                    text="Hurray, you are now registered as an **admin** for the GoCSAP bot! 🎉 \nYou can now type **send notif** to submit notifications and type **analytics** to view GoCSAP bot analytics."
                    api.messages.create(toPersonEmail=requestor, 
                                        markdown=text)    
                except:
                    cur.rollback()
                    log(severity=3, infoMsg="Failed to update database of admins: {}.".format(requestor), personId=personId)  
                    text = ""
                finally:
                    con.commit()

                    # fetch list of all superadmins
                    cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
                    superAdminList = cur.fetchall() 

                    # send approval info to all superadmins
                    text = "The {} request for {} has been successfully approved.".format(level, requestor)
                    
                    for element in superAdminList:
                        for email in element:
                            # delete approval request card 
                            roomMsgs = api.messages.list_direct(personEmail=email)
                            for count, msg in enumerate(roomMsgs):
                                # check last 10 messages
                                if count < 10:
                                    try:
                                        if requestor in msg.attachments[0]["content"]["body"][0]["columns"][0]["items"][1]["text"]:
                                            api.messages.delete(messageId=msg.id)
                                    except:
                                        continue

                            api.messages.create(toPersonEmail=email, 
                                                markdown=text)
                    return ""
            
        if level == "superadmin":
            if check_permission(email=requestor, level="superadmin") == "Authorized":
                text = "{} is already a superadmin.".format(requestor)
                api.messages.delete(messageId=m["messageId"])    
                return text
            # check if requestor is already an admin, if yes, update records to superadmin
            elif check_permission(email=requestor, level="admin") == "Authorized":
                try:
                    cur.execute("""UPDATE admins SET role =  (%s) WHERE email = (%s)""", ("superadmin", requestor))
                    log(severity=2, infoMsg="Admin ugraded to superadmin: {}.".format(requestor), personId=personId)
                    text="Your access level for the GoCSAP bot has been changed to **superadmin**! 🎉 \nYou can now type **send notif** to submit notifications, type **analytics** to view GoCSAP bot analytics and receive requests for approving new admins."
                    api.messages.create(toPersonEmail=requestor, 
                                        markdown=text)    
                except:
                    cur.rollback()
                    log(severity=3, infoMsg="Failed to update database of admins: {}.".format(requestor), personId=personId)  
                    text = ""     
                finally:
                    con.commit()

                    # fetch list of all superadmins
                    cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
                    superAdminList = cur.fetchall() 

                    # send approval info to all superadmins
                    text = "The {} request for {} has been successfully approved.".format(level, requestor)
                    
                    for element in superAdminList:
                        for email in element:
                            # delete approval request card 
                            roomMsgs = api.messages.list_direct(personEmail=email)
                            for count, msg in enumerate(roomMsgs):
                                # check last 10 messages
                                if count < 10:
                                    try:
                                        if requestor in msg.attachments[0]["content"]["body"][0]["columns"][0]["items"][1]["text"]:
                                            api.messages.delete(messageId=msg.id)
                                    except:
                                        continue

                            api.messages.create(toPersonEmail=email, 
                                                markdown=text)

                    return ""   
            # new superadmin           
            else:
                try:
                    cur.execute("""INSERT INTO admins (email, personid, since, role) VALUES (%s, %s, %s, %s)""", (requestor, "", date.today().strftime("%d%m%Y"), "superadmin"))
                    log(severity=2, infoMsg="New superadmin added: {}.".format(requestor), personId=personId)
                    text="Hurray, you are now registered as a **superadmin** for the GoCSAP bot! 🎉 \nYou can now type **send notif** to submit notifications, type **analytics** to view GoCSAP bot analytics and receive requests for approving new admins."
                    api.messages.create(toPersonEmail=requestor, 
                                     markdown=text)    
                except:
                    cur.rollback()
                    log(severity=3, infoMsg="Failed to update database of admins: {}.".format(requestor), personId=personId)
                    text = ""
                finally:
                    con.commit()

                    # fetch list of all superadmins
                    cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
                    superAdminList = cur.fetchall() 

                    # send approval info to all superadmins
                    text = "The {} request for {} has been successfully approved.".format(level, requestor)
                    
                    for element in superAdminList:
                        for email in element:
                            # delete approval request card 
                            roomMsgs = api.messages.list_direct(personEmail=email)
                            for count, msg in enumerate(roomMsgs):
                                # check last 10 messages
                                if count < 10:
                                    try:
                                        if requestor in msg.attachments[0]["content"]["body"][0]["columns"][0]["items"][1]["text"]:
                                            api.messages.delete(messageId=msg.id)
                                    except:
                                        continue

                            api.messages.create(toPersonEmail=email, 
                                                markdown=text)
                    return ""

    elif "decline_admin" in m["inputs"]:
        requestor = m["inputs"].split(" ")[1]
        level = m["inputs"].split(" ")[2]
        api.messages.delete(messageId=m["messageId"]) 
        
        # fetch list of all superadmins to send request to
        cur.execute("""SELECT email FROM admins WHERE role='superadmin';""")
        superAdminList = cur.fetchall() 
        
        # send decline info to all superadmins
        text = "The {} request for {} has been successfully declined.".format(level, requestor)
        
        for element in superAdminList:
            for email in element:
                # delete approval request card 
                roomMsgs = api.messages.list_direct(personEmail=email)
                for count, msg in enumerate(roomMsgs):
                    # check last 10 messages
                    if count < 10:
                        try:
                            if requestor in msg.attachments[0]["content"]["body"][0]["columns"][0]["items"][1]["text"]:
                                api.messages.delete(messageId=msg.id)
                        except:
                            continue

                api.messages.create(toPersonEmail=email, 
                                    markdown=text)
        
        log(severity=2, infoMsg="Admin access declined: {}.".format(requestor), personId=personId)  
        return ""
    
    elif m["inputs"] == "pull_report":
        today_date = date.today().strftime("%d %B %Y")
        # nr subscribers
        cur.execute("""SELECT COUNT (*) FROM testing;""")
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
        
        log(severity=1, infoMsg="Analytics report pulled.", personId=personId)  
        
        text = "Please find your detailed GoCSAP bot analytics report attached. 📊"
        personId = m["personId"]
        api.messages.create(toPersonId=personId, 
                            text=text, files=['GoCSAP_botAnalytics_'+date.today().strftime("%d%m%Y")+'.xlsx'])    
        return ""
           
    api.messages.delete(messageId=m["messageId"])
    log(severity=3, personId=personId, infoMsg="Faulty command. Please review: "+str(m["inputs"]))
    return "Sorry, I do not understand the command {} yet.".format(m["inputs"])    

def parse_msg(incoming_msg, parse, roomId, review, template, personId):
    now = datetime.now()
    msg_id = now.strftime("%d%m%Y-%H%M")
    
    parse.extend([msg_id, roomId, template])
    
    backupmessage = "Hi there! 👋 The GoCSAP bot just sent you a card."
    if str(review) == "true":
        isVisible = "true"
        if template == "1":
            attachment = notif_card_1.format(image_url=parse[0], small_title=parse[1], main_title=parse[2], 
                                        textbox_1=parse[3], textbox_2=parse[4], textbox_3=parse[5], 
                                        button1_text=parse[6], button2_text=parse[7], 
                                        button1_url=parse[8], button2_url=parse[9],
                                        msg_id=parse[10], isVisible=isVisible)   
            
            with open('parse.pkl', 'wb') as f:
                pickle.dump(parse, f)
            # send card to review
            c = create_message_with_attachment(roomId, msgtxt=backupmessage, 
                                               attachment=json.loads(attachment))                                       
            # send card for approving
            c = create_message_with_attachment(roomId, msgtxt=backupmessage, 
                                               attachment=json.loads(approve_card.format(msg_id=msg_id)))  

            log(severity=1, infoMsg="Notification submitted and sent for review.", personId=personId)
               
        elif template == "2":
            attachment = notif_card_2.format(main_title=parse[0], textbox_1=parse[1], 
                                           msg_id=parse[2], isVisible=isVisible)          

            with open('parse.pkl', 'wb') as f:
                pickle.dump(parse, f)
            # send card to review
            c = create_message_with_attachment(roomId, msgtxt=backupmessage, 
                                               attachment=json.loads(attachment))                                       
            # send card for approving
            c = create_message_with_attachment(roomId, msgtxt=backupmessage, 
                                               attachment=json.loads(approve_card.format(msg_id=msg_id)))  

            log(severity=1, infoMsg="Notification submitted and sent for review.", personId=personId)

        elif template == "own":
            attachment = parse[0] 
            attachment = '{"contentType": "application/vnd.microsoft.card.adaptive","content":' + attachment
            attachment = attachment + "}"       

            with open('parse.pkl', 'wb') as f:
                pickle.dump(parse, f)
            # send card to review
            c = create_message_with_attachment(roomId, msgtxt=backupmessage, 
                                               attachment=json.loads(attachment))                                       
            # send card for approving
            c = create_message_with_attachment(roomId, msgtxt=backupmessage, 
                                               attachment=json.loads(approve_card.format(msg_id=msg_id)))  

            log(severity=1, infoMsg="Notification submitted and sent for review.", personId=personId)            
        
        ### add new templates here
        
    else:
        isVisible = "false"
        if template == "1":
            attachment = notif_card_1.format(image_url=parse[0], small_title=parse[1], main_title=parse[2], 
                                        textbox_1=parse[3], textbox_2=parse[4], textbox_3=parse[5], 
                                        button1_text=parse[6], button2_text=parse[7], 
                                        button1_url=parse[8], button2_url=parse[9],
                                        msg_id=parse[10], isVisible=isVisible)   
        elif template == "2":
            attachment = notif_card_2.format(main_title=parse[0], textbox_1=parse[1], 
                                           msg_id=parse[2], isVisible=isVisible)  

        elif template == "own":
            attachment = parse[0]
            attachment = '{"contentType": "application/vnd.microsoft.card.adaptive","content":' + attachment
            attachment = attachment + "}"  
           
        ### add new templates here
            
        cur.execute("""SELECT roomId FROM testing;""")
        result = cur.fetchall()
        for element in result:
            for subscriberRoomId in element:
                c = create_message_with_attachment(
                    subscriberRoomId, msgtxt=backupmessage, attachment=json.loads(attachment)) 

        log(severity=2, infoMsg="Notification sent without review. Notification Id: {}".format(msg_id), personId=personId)
        
        m = get_attachment_actions(incoming_msg["data"]["id"])
        api.messages.delete(messageId=m["messageId"]) 
        text = "Notification {} was sent to bot testers! 🎉".format(msg_id)
        api.messages.create(roomId, text=text)  

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

    api.messages.create(roomId=incoming_msg.roomId, 
                text="⚠️ The bot is currently is maintenance mode. Please do not use it. Contact elandman@cisco.com for more info.") 

    fetch_infos(incoming_msg)
    db_entry = roomId
    
    request = (incoming_msg.text).split(" ")
    if "GoCSAP" in request:
        request.remove("GoCSAP")
    # if the command doesnt start with un, subscribe the user
    if request[0][0:2] != "un":
        try:
            cur.execute("""INSERT INTO testing (roomid) VALUES (%s)""", (db_entry,))
            log(severity=0, infoMsg="Tester database updated.", personEmail=incoming_msg.personEmail)
            print("Added tp DB")
        except:
            con.rollback()
            log(severity=3, infoMsg="Failed to update database of testers.", personId=personId)  
            print("could not be added to db")
        finally:
            con.commit()
            return "Thank you, you successfully subscribed to CSAP bot updates. 🥳"
    # if it starts with un, then unsubscribe the user
    else:
        try:
            cur.execute("""DELETE FROM testing WHERE roomid = (%s)""", (db_entry,))
            log(severity=0, infoMsg="Tester database updated.", personEmail=incoming_msg.personEmail) 
            print("Removed from DB")
        except:
            con.rollback()
            log(severity=3, infoMsg="Failed to update database of testers.", personId=personId)
            print("Could not be removed from DB")   
        finally:
            con.commit()
            return "Thank you, you successfully unsubscribed from CSAP bot updates. 😢"  

def help(incoming_msg):

    api.messages.create(roomId=incoming_msg.roomId, 
                text="⚠️ The bot is currently is maintenance mode. Please do not use it. Contact elandman@cisco.com for more info.") 

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

    api.messages.create(roomId=incoming_msg.roomId, 
                text="⚠️ The bot is currently is maintenance mode. Please do not use it. Contact elandman@cisco.com for more info.") 

    fetch_infos(incoming_msg)
    return "Thank you {} for using the GoCSAP bot! \n Current version is v1.0. \n Please contact elandman@cisco.com for more information or for feedback and improvement suggestions.".format(firstName)

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

    api.messages.create(roomId=incoming_msg.roomId, 
                text="⚠️ The bot is currently is maintenance mode. Please do not use it. Contact elandman@cisco.com for more info.") 

    if check_permission(email=incoming_msg.personEmail) == "Authorized":
        request = (incoming_msg.text).split(" ")
        
        if "GoCSAP" in request:
            request.remove("GoCSAP")
        
        if len(request) > 2:
            if request[2] == "1":
                template = send_notif_template_1
            elif request[2] == "2":
                template = send_notif_template_2
            elif request[2] == "own":
                template = send_notif_template_own
            ### add new templates here
            else:
                text = "Oops, I do not support template {} yet. I currently support {} templates. Please adjust your choice to one of these.".format(request[2], "2")
                return text
        else:
            template = send_notif_template_1

        person = bot.teams.people.get(incoming_msg.personId)
        personId = person.id
        attachment = template
        backupmessage = "Hi there! 👋 You requested to create a notification through the GoCSAP bot."

        c = create_message_with_attachment(incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment))  
        log(severity=1, infoMsg="Notification request made.", personEmail=incoming_msg.personEmail)
        
        return ""   
    else:
        log(severity=2, infoMsg="Notification requested without permission.", personEmail=incoming_msg.personEmail)
        text = "You do not have permission to send notifications via the GoCSAP bot. You can request admin access by typing **make admin**."
        return text

def log(severity, personId="", infoMsg="", personEmail = ""):
    # function for logging al things sent with the bot
    # severity 0, 1, 2, 3 (0=informational, ..., 3=emergency)
    now = datetime.now()
    logDate = now.strftime("%d%m%Y-%H:%M")   
    
    data = "\n{}, Severity: {}, Info: {}, personEmail: {}, personId: {}".format(logDate, severity, infoMsg, personEmail, personId)

    with open(logs, "a") as file:
        file.write(data) 

def check_permission(personId="", email="", level="admin"):
    #try:
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
    #except:
        #text = "Oops, your access level could not be verified. Please contact a GoCSAP superadmin or elandman@cisco.com."
        #return text
    
def valid_email(email):  
    if(re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]cisco[.]\w{2,3}$', email)):  
        return "valid"
          
    else:  
        return "invalid" 
    
def request_admin_access(incoming_msg):

    api.messages.create(roomId=incoming_msg.roomId, 
                text="⚠️ The bot is currently is maintenance mode. Please do not use it. Contact elandman@cisco.com for more info.") 

    request = (incoming_msg.text).split(" ")

    if "GoCSAP" in request:
        request.remove("GoCSAP")
    
    # request for someone else
    if len(request) > 2:
        reqEmail = request[2]
        if valid_email(reqEmail) == "valid":
            if request[1] == "admin":
                if check_permission(email=reqEmail, level="superadmin") == "Authorized":
                    text = "{} is already a superadmin. Use the *cancel admin* command to revoke admin rights.".format(reqEmail)
                    return text
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
                    log(severity=2, infoMsg="New admin request submitted.", personEmail=incoming_msg.personEmail)                    

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
                    backupmessage = "Hi admin! 👋 Someone requested superadmin access and your approval is required."
                    
                    # send request to all superadmins
                    for element in superAdminList:
                        for email in element: 
                            c = create_message_with_attachment(incoming_msg.roomId, 
                                                               msgtxt=backupmessage, 
                                                               attachment=json.loads(attachment), 
                                                               toPersonEmail=email)  
                    log(severity=2, infoMsg="New superadmin request submitted.", personEmail=incoming_msg.personEmail)                    

                    # send confimation to requestor
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
    # request for self
    else:
        reqEmail = incoming_msg.personEmail

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
                    log(severity=2, infoMsg="New admin request submitted.", personEmail=reqEmail)                    

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
                    log(severity=2, infoMsg="New superadmin request submitted.", personEmail=reqEmail)                     

                    # send confim ation to requestor
                    text="Thank you, your request for superadmin access has been forwarded! Once your request has been approved/declined you will receive a notification."
                    return text 
            
            else:
                return "Oops, something went wrong 😢"

        else:
            log(severity=2, infoMsg="New invalid admin request by non Cisco employee.", personEmail=reqEmail) 
            text = "Admin rights are reserved for Cisco employees with a valid Cisco email address only."
            return text

def cancel_admin_access(incoming_msg):

    api.messages.create(roomId=incoming_msg.roomId, 
                text="⚠️ The bot is currently is maintenance mode. Please do not use it. Contact elandman@cisco.com for more info.") 

    request = (incoming_msg.text).split(" ")
    
    if "GoCSAP" in request:
        request.remove("GoCSAP")

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
                
                log(severity=2, infoMsg="Admin access revoked for {}.".format(reqEmail), personEmail=incoming_msg.personEmail)

                text = "Admin access for {} has successfully been revoked.".format(reqEmail)
                return text
            else:       
                text = "{} is not an admin.".format(reqEmail)
                return text
        else:
            # not a superadmin
            log(severity=2, infoMsg="No permission to revoke admin access.", personEmail=incoming_msg.personEmail)
            text = "You do not have permission to revoke someone else's admin access. Only superadmins can grant and revoke admin access."
            return text
        
    # revoke my own access
    else:
        reqEmail = incoming_msg.personEmail
        if check_permission(email=reqEmail) == "Authorized":
            cur.execute("""DELETE FROM admins WHERE email = (%s)""", (reqEmail,))
            con.commit()
            log(severity=2, infoMsg="Admin rights revoked for {}.".format(reqEmail), personEmail=reqEmail)

            text = "Your admin access has successfully been revoked.".format(reqEmail)
            return text
        else:       
            text = "You are not an admin.".format(reqEmail)
            return text            

def admin_analytics(incoming_msg):

    api.messages.create(roomId=incoming_msg.roomId, 
                text="⚠️ The bot is currently is maintenance mode. Please do not use it. Contact elandman@cisco.com for more info.") 

    reqEmail = incoming_msg.personEmail
    if check_permission(email=reqEmail) == "Authorized":
        
        today_date = date.today().strftime("%d %B %Y")
        # nr subscribers
        cur.execute("""SELECT COUNT (*) FROM testing;""")
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

        log(severity=1, infoMsg="Analytics requested.", personEmail=reqEmail)

        c = create_message_with_attachment(
            incoming_msg.roomId, msgtxt=backupmessage, attachment=json.loads(attachment))    

        return ""       
    else:
        log(severity=2, infoMsg="Analytics requested without permission.", personEmail=reqEmail)
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
    api.messages.create(roomId=incoming_msg.roomId, 
                        text=text) 
    time.sleep(1.5)
    text = "{}".format(setup)
    api.messages.create(roomId=incoming_msg.roomId, 
                        text=text)  
    time.sleep(3)
    text = "{}".format(punchline)    
    api.messages.create(roomId=incoming_msg.roomId, 
                        text=text)
    time.sleep(1)
    return "😂"

def logfile(incoming_msg):

    api.messages.create(roomId=incoming_msg.roomId, 
                text="⚠️ The bot is currently is maintenance mode. Please do not use it. Contact elandman@cisco.com for more info.") 

    reqEmail = incoming_msg.personEmail
    if check_permission(email=reqEmail, level="superadmin") == "Authorized":  
        log(severity=1, infoMsg="Logfile requested.", personEmail=reqEmail)
        text = "Please find the GoCSAP bot logfile attached."
        api.messages.create(toPersonEmail=reqEmail, 
                            text=text, files=['logs.txt'])    
        return ""
    else:
        text = "You do not have permission to view the GoCSAP bot logfile. Please request superadmin acces by typing **make superadmin**."
        log(severity=2, infoMsg="Logfile requested without permission.", personEmail=reqEmail)
        return text
    
bot.set_greeting(greeting)
bot.add_command("attachmentActions", "*", handle_cards)
bot.add_command("help", "Help", help)
bot.add_command("contact", "Contact", contact)
bot.add_command("subscribe", "subscribe", subscribe)
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

    for webhook in api.webhooks.list():
        if webhook.id != webhook_list[-2] and webhook.id != webhook_list[-1]:
            api.webhooks.delete(webhook.id)

    # Run Bot
    bot.run()