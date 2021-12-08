import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Main():
    def __init__(self):
        self.username = os.environ['mailFrom']
        self.password = os.environ['mailFromPassword']
        self.mailFrom = os.environ['mailFrom']

    def getSlots(self, intentRequest):
        return intentRequest['currentIntent']['slots']

    def close(self, sessionAttributes, fulfillmentState, message):
        response = {
            'sessionAttributes': sessionAttributes,
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': fulfillmentState,
                'message': message
            }
        }
        return response

    def elicitSlot(self, sessionAttributes, intentName, slots, slotToElicit, message):
        return {
                'recentIntentSummaryView': [
                    {
                        'intentName': intentName,
                        'slots': slots,
                        'dialogActionType': 'ElicitSlot',
                        'fulfillmentState': 'Fulfilled',
                        'slotToElicit': slotToElicit,
                    }
                ],
                'sessionAttributes': sessionAttributes,
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'intentName': intentName,
                    'slots': slots,
                    'slotToElicit': slotToElicit,
                    'message': {
                        'contentType': 'PlainText',
                        'content': message
                    },
                }
            }
    
    def delegate(self, sessionAttributes, slots):
        return {
            'sessionAttributes': sessionAttributes,
            'dialogAction': {
                'type': 'Delegate',
                'slots': slots
            }
        }

    def sendEmail(self, email, message, subject):
        if email and message and subject:
            mimemsg = MIMEMultipart()
            mimemsg['From']= self.mailFrom
            mimemsg['To'] = email
            mimemsg['Subject']= subject
            mimemsg.attach(MIMEText(message, 'plain'))
            connection = smtplib.SMTP(host='smtp.office365.com', port=587)
            connection.starttls()
            connection.login(self.username,self.password)
            connection.send_message(mimemsg)
            connection.quit()
            return True
        else:
            return False

    def parseInt(self, n):
        try:
            return int(n)
        except ValueError:
            return float('nan')