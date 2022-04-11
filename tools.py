# Imports
import json, yaml, datetime
from math import floor, log
from decimal import *
from ei import *


def load(which):
    """Load Configuration Information"""
    with open("bot.yaml", "r") as botConfig:
        bot = yaml.safe_load(botConfig)
        return(bot[which])
        

# Define a couple 'global' things to use throughout the bot.
botPrefix = load("botPrefix")
botName = load("botName")

########################################################################################################################
   
def getEB(backup):
    """Pull all relavent EB data from backup"""
    backup = backup["backup"]
    researchList = backup["game"]["epicResearch"]
    soulFood = 0
    prophecyBonus = 0
    for research in researchList:
        if research["id"] == "soul_eggs":
            soulFood = research["level"]
        if research["id"] == "prophecy_bonus":
            prophecyBonus = research["level"]
    prophecyEggs = backup["game"]["eggsOfProphecy"]
    soulEggs = backup["game"]["soulEggsD"]
    
    returndict = {
        "soulFood" : soulFood,
        "prophecyBonus" : prophecyBonus,
        "soulEggs" : soulEggs,
        "prophecyEggs" : prophecyEggs
    }
    return returndict


def human_format(number: Decimal):
    units = ['', 'k', 'm', 'b', 'T', 'q', 'Q', 's', 'S', 'o', 'N', 'd', 'U', 'D', 'Td', 'qd', 'Qd', 'sd', 'Sd', 'Od', 'Nd', 'V', 'uV', 'dV', 'tV', 'qV', 'sV', 'SV', 'OV', 'NV', 'tT']
    k = Decimal(1000.0)
    magnitude = int(floor(log(number, k)))
    return '%.3f%s' % (number / k**magnitude, units[magnitude])


def formatLargeNumber(largeNumber: str):
    if largeNumber == "0":
        return "E1"
    if largeNumber.endswith("k"):
        largeNumber = (largeNumber[:-1]) 
        largeNumber = largeNumber * 1000    
    elif largeNumber.endswith("m"):
        largeNumber = Decimal(largeNumber[:-1]) 
        largeNumber = largeNumber * 1000000
    elif largeNumber.endswith("b"):
        largeNumber = Decimal(largeNumber[:-1]) 
        largeNumber = largeNumber * 1000000000
    elif largeNumber.endswith('t'):
        largeNumber = Decimal(largeNumber[:-1]) 
        largeNumber = largeNumber * 1000000000000
    elif largeNumber.endswith('q'):
        largeNumber = Decimal(largeNumber[:-1]) 
        largeNumber = largeNumber * 1000000000000000
    elif largeNumber.endswith('Q'):
        largeNumber = Decimal(largeNumber[:-1]) 
        largeNumber = largeNumber * 1000000000000000000
    elif largeNumber.endswith('s'):
        largeNumber = Decimal(largeNumber[:-1]) 
        largeNumber = largeNumber * 1000000000000000000000
    elif largeNumber.endswith('S'):
        largeNumber = Decimal(largeNumber[:-1]) 
        largeNumber = largeNumber * 1000000000000000000000000  
    elif largeNumber.endswith('o'):
        largeNumber = Decimal(largeNumber[:-1]) 
        largeNumber = largeNumber * 1000000000000000000000000000
    elif largeNumber.endswith('N'):
        largeNumber = Decimal(largeNumber[:-1]) 
        largeNumber = largeNumber * 1000000000000000000000000000000
    else:
        largeNumber = Decimal(largeNumber)
    return largeNumber


def calculateEB(soulEggs: Decimal, prophecyEggs: Decimal, prophecyBonus: Decimal, soulFood: Decimal, human: bool):
    try:
        prophecyEggBonus = (Decimal(1) + Decimal(0.05) + (Decimal(0.01) * Decimal(prophecyBonus)))**Decimal(prophecyEggs) * (Decimal(10) + Decimal(soulFood))
        EB = Decimal(prophecyEggBonus) * Decimal(soulEggs)
        if human == True:
            EB = human_format(EB)
        return EB
    except:
        return False


def addAccount(eid, nickname, discordId):
    with open("user.json", "r+") as usersJson:
        try:
            data = json.load(usersJson)
            backup = firstContactRequest(eid)
            info = getEB(backup)
            newPerson = info 
            newPerson["nickname"] = nickname
            newPerson['discord'] = discordId
            data[eid] = newPerson
            usersJson.seek(0)
            json.dump(data, usersJson, indent=2)
            usersJson.truncate()
            return True
        except:
            return False


def deleteAccount(eid, discordID):
    with open("user.json", "r+") as usersJson:
        users = json.load(usersJson)
        try:
            verificationThing = users[eid]
        except KeyError:
            return False
        if verificationThing["discord"] == discordID:
            try:
                users.pop(eid)
                usersJson.seek(0)
                json.dump(users, usersJson, indent=2)
                usersJson.truncate()
                return True
            except:
                return False
        else:
            return False


def searchByDiscordID(discordID):
    with open("user.json", "r+") as usersJson:
        accounts = json.load(usersJson)
        results = {}
        for eid, account in accounts.items():
            if account["discord"] == discordID:
                sampleDict = {
                    "soulFood": account["soulFood"],
                    "prophecyBonus": account["prophecyBonus"],
                    "soulEggs": account["soulEggs"],
                    "prophecyEggs": account["prophecyEggs"],
                }
                results[eid] = sampleDict
        return results


def updateLeaderboard():
    with open ("user.json", 'r+') as usersJson:
        data = json.load(usersJson) # Load the data
        n = 0 # declare the number
        peopleList = []
        for user in data.values():
            n += 1
            eb = calculateEB(user["soulEggs"], user["prophecyEggs"], user["prophecyBonus"], user["soulFood"], False)
            username = user["nickname"]
            sampleDict = {
                "eb" : str(eb),
                "nickname" : username,
                "rank" : getOom(eb),
                "discord" : user['discord'],
                "pe" : user["prophecyEggs"]
            }
            peopleList.append(sampleDict)

        peopleList = sorted(peopleList, key = lambda i: Decimal(i['eb']), reverse=True)

        return peopleList


def updateSoulLeaderboard():
    with open ("user.json", 'r+') as usersJson:
        data = json.load(usersJson) # Load the data
        n = 0 # declare the number
        peopleList = []
        for user in data.values():
            n += 1
            sampleDict = {
                "soulEggs" : str(user["soulEggs"]),
                "discord" : user['discord']
            }
            peopleList.append(sampleDict)

        peopleList = sorted(peopleList, key = lambda i: Decimal(i['soulEggs']), reverse=True)

        return peopleList


def updateAllUsers():
    with open("user.json", "r+") as usersJson:
        data = json.load(usersJson)
        for eid, person in data.items():
            try:
                backup = firstContactRequest(eid)
                personInfo = getEB(backup)
                personInfo["nickname"] = person["nickname"]
                personInfo["discord"] = person["discord"]
                data[eid] = personInfo
            except:
                print(f"{eid} failed to update at {datetime.datetime.now()}")

        usersJson.seek(0)
        json.dump(data, usersJson, indent=2)
        usersJson.truncate()


def getOom(eb: Decimal):
    units = ['Farmer','Farmer','Farmer', 'Farmer', 'Farmer', 'Farmer',  'Kilofarmer', 'Kilofarmer', 'Kilofarmer', 'Megafarmer', 'Megafarmer', 'Megafarmer', 'Gigafarmer', 'Gigafarmer', 'Gigafarmer', 'Terafarmer', 'Terafarmer', 'Terafarmer', 'Petafarmer', 'Petafarmer', 'Petafarmer', 'Exafarmer', 'Exafarmer', 'Exafarmer', 'Zettafarmer', 'Zettafarmer', 'Zettafarmer', 'Yottafarmer', 'Yottafarmer', 'Yottafarmer', 'Xennafarmer', 'Xennafarmer', 'Xennafarmer', 'Weccafarmer', 'Weccafarmer', 'Weccafarmer', 'Vendafarmer', 'Vendafarmer', 'Vendafarmer', 'Uadafarmer', 'Uadafarmer', 'Uadafarmer', 'Treidafarmer', 'Treidafarmer', 'Treidafarmer', 'Quadafarmer', 'Quadafarmer', 'Quadafarmer', 'Pendafarmer', 'Pendafarmer', 'Pendafarmer', 'Exedafarmer', 'Exedafarmer', 'Exedafarmer'] 
    magnitude = len(str(round(eb)))
    if magnitude >= 55:
        return 'Infinifarmer'
    return units[magnitude]
