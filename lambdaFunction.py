from pymongo import MongoClient
from classes.MainClass import Main
import os
import json
import random
import string
import logging
import pymssql
import datetime

MainClass = Main()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def splitPhoneNumber(phoneNumber):
    response = {}
    if phoneNumber[0] == '+':
        phoneNumber = phoneNumber[3:]
    aux = ""
    for index, number in enumerate(phoneNumber):
        if index % 2 == 0:
            aux += str(number)
        else:
            aux += str(number) + " "
    response["phoneNumber"] = aux
    return response


def sendEmail(parameters):
    response = {}
    sent = MainClass.sendEmail(
        parameters["emailTo"], parameters["message"], parameters["subject"])
    if sent:
        response["result"] = True
        return response
    else:
        raise Exception('Action not supported')


def saveReport(details):
    response = {}
    conn = pymssql.connect(
        os.environ['server'], os.environ['user'], os.environ['password'], os.environ['db'])
    cursor = conn.cursor(as_dict=True)
    cursor.execute("""INSERT INTO calls ([numberPhone],[startCall],[endCall],[offset],[id_poc],[create_date])
    VALUES (%s, %s, null, null, 1, %s)""", (details["ContactData"]["CustomerEndpoint"]["Address"], str(datetime.datetime.now())[:-7], str(datetime.datetime.now())[:-7]))
    response["idCall"] = cursor.lastrowid
    conn.commit()
    return response


def updateReport(parameters):
    response = {}
    conn = pymssql.connect(
        os.environ['server'], os.environ['user'], os.environ['password'], os.environ['db'])
    cursor = conn.cursor(as_dict=True)
    cursor.execute("SELECT * FROM calls WHERE id = %s", parameters["id"])
    call = cursor.fetchone()
    seconds = int((datetime.datetime.now() -
                  call["startCall"]).total_seconds())
    cursor.execute("UPDATE calls set [endCall]=%s, [offset]=%s WHERE [id] =%s", (str(
        datetime.datetime.now())[:-7]), seconds)
    conn.commit()
    response["result"] = True
    return response


def dispatch(event):
    if 'Details' in event:
        if 'Parameters' in event['Details'] and "action" in event["Details"]["Parameters"]:
            action = event["Details"]["Parameters"]["action"]
            if action == "splitPhoneNumber":
                if "phoneNumber" in event["Details"]["Parameters"]:
                    return splitPhoneNumber(event["Details"]["Parameters"]["phoneNumber"])
            elif action == "sendEmail":
                if event["Details"]["Parameters"].keys() >= {"emailTo", "message", "subject"}:
                    return sendEmail(event["Details"]["Parameters"])
            elif action == "saveReport":
                return saveReport(event["Details"])
            elif action == "updateReport":
                if event["Details"]["Parameters"].keys() >= {"id"}:
                    return updateReport(event["Details"]["Parameters"])

    raise Exception('Action not supported')


def lambdaHandler(event, context):
    logger.debug('event={}'.format(json.dumps(event)))
    return dispatch(event)
