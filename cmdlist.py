import pandas
from array import *
import numpy
import re
import os.path
from PIL import Image
from discord import *

df = pandas.read_csv('db.csv')

colordic = {
    'Red': 0xe74c3c, 
    'Blue': 0x3498db, 
    'Red/Blue': 0x1abc9c,
    'Green': 0x2ecc71, 
    'Yellow': 0xe67e22, 
    'Purple': 0x800080, 
    'Brown': 0x8b4513,
    'White': 0xffffff,
    'Black': 0x000000,
    'White/Black': 0x546e7a,
    'None': 0x95a5a6,


     }

def findByCode(num):
    #scrub database to find the card with given code
    cc = df[(df['card_code'] == str(num))]
    #if it doesn't exist, return an error
    if (len(cc) == 0):
        return(0)
    #Clean the formatting and return the card info
    card = {}
    card["set"] = str(cc.iloc[0,1])
    card["name"] = re.sub('%', ',', str(cc.iloc[0,4]))
    card["card_code"] = str(cc.iloc[0,2])
    card["cost"] = ( str(cc.iloc[0,5]) + '(' + re.sub('-', '0', str(cc.iloc[0,6])) + ')' )
    card["job"]=  str(cc.iloc[0,8])
    card["color"] = str(cc.iloc[0,9])
    card["color"] = re.sub('#', '/', card.get("color"))
    card["gender"] = re.sub('-', 'None', str(cc.iloc[0,10]))
    card["weapon"] = str(cc.iloc[0,11])
    card["type"] = re.sub('-', 'None', str(cc.iloc[0,12]))
    card["type"] = re.sub('#', '/', card.get("type"))
    card["attack"] = str(cc.iloc[0,13])
    card["support"] = str(cc.iloc[0,14])
    card["range"] = str(cc.iloc[0,15])
    card["effect"] =  re.sub('%', ',', str(cc.iloc[0,16]))
    card["effect"] =  re.sub('\$', '\n', card.get("effect"))
    card["effect"] =  re.sub('@', '|', card.get("effect"))
    card["support_effect"] =  re.sub('%', ',', str(cc.iloc[0,17]))
    card["support_effect"] =  re.sub('\$', '\n', card.get("support_effect"))
    card["support_effect"] =  re.sub('@', '|', card.get("support_effect"))
    card["skin"] = colordic.get(card.get("color"))
    return(card)

def RandChar(userNum):
    userID = str(userNum)
    userPATH = 'drafts/' + userID + '.csv'
    #scrub database to find the card with given code
    cc = df.sample(n=1)
    #if it doesn't exist, return an error
    if (len(cc) == 0):
        return(0)
    #Clean the formatting and return the card info
    card = findByCode(cc.iloc[0,2])
    check = os.path.isfile(userPATH)
    if (check == True):
        saveToBinder(cc, userPATH)
    return(card)


def findByTag(cardTag, msg, path):
    data = pandas.read_csv(path)
    #check if tag exists
    if ((str(cardTag).lower() not in data.columns)):
        return(1,0)
    #scrub db for card names
    if (cardTag == 'support' or data[cardTag].astype(str).str.isdigit().all()):
        print('Passed int check')
        cc = data[(data[cardTag].astype(str).str.match(msg.capitalize()))]
    else:
        cc = data[(data[str(cardTag)].str.contains(re.sub('/', '#', str(msg)), flags=re.IGNORECASE, regex = True))]
    print(cc)
    if (len(cc) == 0):
        return(2,0)
    return (cc)

def appendToString(cc):
    cardlist = []
    for x in range(len(cc)):
        cardlist.append(str(cc.iloc[x, 2]) + " " + re.sub('%', ',', str(cc.iloc[x,4])) + " \n")
    listlen = len(cardlist)
    return(cardlist, listlen)   

def dropBinder(userNum):
    userID = str(userNum)
    userPATH = 'drafts/' + userID + '.csv'
        #check if it exists
    check = os.path.isfile(userPATH)
    if (check == False):
        return(0)
    os.remove(userPATH)
    return(1)

def binderchk(cardTag, msg, userNum, chk):
    #are we searching the whole cardpool or just the user's binder?
    if (chk == True):
        #grab userDB path
        userID = str(userNum)
        userPATH = 'drafts/' + userID + '.csv'
        #check if it exists
        check = os.path.isfile(userPATH)
        if (check == False):
            return(0,0)
        (a, b) = appendToString(findByTag(cardTag, msg, userPATH))
        return(a, b)
    else:
        (a, b) = appendToString(findByTag(cardTag, msg, 'db.csv'))
        return(a, b)

def openPack(setName, userNum):
    userID = str(userNum)
    userPATH = 'drafts/' + userID + '.csv'
    (a, b) = packGen(findByTag('set', setName, 'db.csv'), userPATH)
    return(a, b)

def customPack(cardTag, msg, userNum):
    userID = str(userNum)
    userPATH = 'drafts/' + userID + '.csv'
    (a, b) = packGen(findByTag(cardTag, msg, 'db.csv'), userPATH)
    return(a, b)

def randPack(userNum):
    cc = df.sample(n=10)
    userID = str(userNum)
    userPATH = 'drafts/' + userID + '.csv'
    (a, b) = packGen(cc, userPATH)
    return(a, b)
    

def packGen(cc, userPATH):
    cardlist = ''
    width = 240
    height = 336
    picArray = []
    if (len(cc) == 0):
        return(0, 0)
    #grab up to 10 random cards from the set
    if (len(cc) < 10):
        rand = cc.sample(n=len(cc))
    else:
        rand = cc.sample(n=10)
    #check if userDB exists
    check = os.path.isfile(userPATH)
    if (check == False):
        rand['amount'] = 1
        rand.to_csv(userPATH, index = False)
    else:
        #add cards to user db
        saveToBinder(rand, userPATH)

    for x in range(len(rand)):
        cardlist +=  str(rand.iloc[x,2]) + ' ' + re.sub('%', ',', str(rand.iloc[x,4])) + " \n "
        #(./img/(B17)B17-019.jpg)
        b = cutDown(x)
        picArray.append(Image.open("./img/" + "(" + str(rand.iloc[x,1]) + ")" + str(rand.iloc[x,2]) + ".jpg"))
        #card size: 240 x 336
        #240, 480, 960,
        #row 0: 1 3 5 7 9
        #row 1: 2 4 6 8 10
    fArray = numpy.hstack(numpy.asarray(picArray))
    picFile = Image.fromarray(fArray)
    picPath = "pack.jpg"
    picFile.save(picPath, "JPEG")
    return(cardlist, picPath)

def saveToBinder(rand, userPATH):
    for x in range(len(rand)):
            #check updated db
            userDB = pandas.read_csv(userPATH)
            #clone database for editing
            clone = userDB.copy()
            #find card in user db
            card = userDB[(userDB['card_code'] == rand.iloc[x, 2])]
            if (len(card) == 0):
                #if card is not there, create and append the card to the file
                pd = rand[(rand['card_code']) == rand.iloc[x, 2]]
                pd['amount'] = 1
                pd.to_csv(userPATH, mode = 'a', header = False, index = False)
            else:
                #if card is there, update the amount on CLONE, then, update() userDB based on clone
                clone.loc[userDB['card_code'] == rand.iloc[x, 2], 'amount'] += 1 
                userDB.update(clone)
                userDB.to_csv(userPATH, index = False)

def cutDown(n):
    if (n > 5):
        return(n - 5)
    return(n)

def callBinder(userNum):
    userID = str(userNum)
    userPATH = 'drafts/' + userID + '.csv'
    #check if db exists
    check = os.path.isfile(userPATH)
    if (check == False):
        return(0, 0, 0)
    userDB = pandas.read_csv(userPATH)    
    cardlist = []
    #append db to string for Discord
    for x in range (len(userDB)):
        #B17-019 Chrom (x3)
        cardlist.append(str(userDB.iloc[x, 2]) + " " + re.sub('%', ',', str(userDB.iloc[x,4])) + " (x" + str(userDB.iloc[x, 20]) + ") \n")
    #Find topmost card
    picPath = "./img/" + "(" + str(userDB.iloc[0,1]) + ")" + str(userDB.iloc[0,2]) + ".jpg"
    listlen = len(cardlist)
    cardlist.sort()
    return(cardlist, picPath, listlen)

def trade(user1, user2, card1, card2):
    #grab users
    user1ID = str(user1)
    user1PATH = 'drafts/' + user1ID + '.csv'
    u1DB = pandas.read_csv(user1PATH)
    user2ID = str(user2)
    user2PATH = 'drafts/' + user2ID + '.csv'
    u2DB = pandas.read_csv(user2PATH)
    cc1 = u1DB[(u1DB['card_code'] == str(card1))]
    cc2 = u2DB[(u2DB['card_code'] == str(card2))]
    saveToBinder(cc2, user1PATH)
    saveToBinder(cc1, user2PATH)
    return (0)


def stripID(msg):
    msg = re.sub('<', '', msg)
    msg = re.sub('@', '', msg)
    return(msg)

def makeCSV(code, userID):
    cc = df[(df['card_code'] == str(code).upper())]
    cc.to_csv('.drafts/' + userID + '.csv', index = False)
    print('completed')
    return()

def getUser(user):
    return(user)

def verifyBinder(userNum):
    userID = str(userNum)
    userPATH = 'drafts/' + userID + '.csv'
    #check if db exists
    check = os.path.isfile(userPATH)
    if (check == False):
        return(0)