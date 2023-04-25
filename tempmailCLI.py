# 23.04.2023

# temp mail server
# using mail.tm

import logging
import string
import requests
import json
import random
import sys
import schedule
import time
from bs4 import BeautifulSoup

logging.basicConfig( level=logging.WARNING)

urlBaseLst=['https://api.mail.tm','https://api.mail.gw']
urlBase=urlBaseLst[random.randrange(2)]
# urlBase='https://api.mail.tm'
urlAccounts=urlBase+'/accounts'
urlMe=urlBase+'/me'
urlDomain=urlBase+'/domains'
urlMsg=urlBase+'/messages'
ulrSrc=urlBase+'/sources'
urlToken=urlBase+'/token'

emailLen=16
passLen=10
MsgInServer=0

def GetDomain():
    try:
        resp=requests.get(urlDomain+'?page=1')
        resp.raise_for_status()
        ans=json.loads (str(resp.text))  
        return ans['hydra:member'][0]['domain'] 
    except requests.exceptions.HTTPError as e:
        logging.error('GetDomain Error '+str(e))
        return "0"
    
def RegAccount(email,usrpass):
    myobj = {'address': email,"password":usrpass}
    try:
        resp=requests.post(urlAccounts,json=myobj)
        resp.raise_for_status()
        ans=json.loads (str(resp.text))
        return ans
    except requests.exceptions.HTTPError as e:
        logging.error('GetAccount Error '+str(e))
        return "0"
    
def GetToken(email,usrpass):
    myobj = {'address': email,"password":usrpass}
    try:
        resp=requests.post(urlToken,json=myobj)
        resp.raise_for_status()
        ans=json.loads (str(resp.text))
        return ans['token']
    except requests.exceptions.HTTPError as e:
        logging.error('GetToken Error '+str(e))
        return "0"

def GetDetailMsg(msgID):
    try:
        resp=requests.get(urlMsg+'/'+msgID,headers=hdr)
        resp.raise_for_status()
        ans=json.loads (str(resp.text))  
        # print(str(ans)) 
        soup = BeautifulSoup(ans['text'], 'html.parser') # convert HTML to text
        return soup.get_text() 
    except requests.exceptions.HTTPError as e:
        logging.error('GetDeatailMsg Error '+str(e))
        return "0"
    
def GetMsg(hdr):
    try:
        resp=requests.get(urlMsg+'?page=1',headers=hdr)
        resp.raise_for_status()
        ans=json.loads (str(resp.text))      
        rtn=[]
        if ans['hydra:totalItems'] > 0 :
            for x in ans['hydra:member']:    
                xMsgDict={}             
                xMsgDict.update({'msg_id':x['id']})
                xMsgDict.update({'from':x['from']['address']})
                xMsgDict.update({'subject':x['subject']})
                xMsgDict.update({'intro':x['intro']})
                xMsgDict.update({'hasAttachments':x['hasAttachments']})
                xMsgDict.update({'createdAt':x['createdAt']})
                xMsgDict.update({'body':GetDetailMsg(x['id'])})
                rtn.append(xMsgDict)
            return rtn
    except requests.exceptions.HTTPError as e:
        logging.error('GetMsg Error '+str(e))
        return "0"

def DelAccount(Aid,hdr):
    try:
        resp=requests.delete(urlAccounts+'/'+Aid,headers=hdr)
        resp.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        logging.error('DelAccount Error '+str(e))
        return False

def GetMe(hdr):
    try:
        resp=requests.get(urlMe,headers=hdr)
        resp.raise_for_status()
        return json.loads (str(resp.text)) 
    except requests.exceptions.HTTPError as e:
        logging.error('DelAccount Error '+str(e))
        return '0'

print("\033[93m {}\033[00m" .format('Temporary email address CLI'))    

# 1 get valid domains
domn=GetDomain()
if not domn=='0':
    UsrMail = ''.join(random.sample(string.ascii_lowercase+string.digits,emailLen))+'@'+str(domn) 
    print("\033[96m {}\033[00m" .format('EMAIL: '+UsrMail))
else: sys.exit()

# 2 register account
UsrPass=''.join(random.sample(string.ascii_letters+string.digits,passLen))
account=RegAccount(UsrMail,UsrPass)
if not account=='0':
    accountID=account['id']
    print('Account id: '+accountID)
else: sys.exit()

# 3 get token
UsrToken=GetToken(UsrMail,UsrPass)
if not UsrToken=='0':
    # print('TOKEN:'+UsrToken)
    pass
else: sys.exit()

# 4 update header for JWT token
hdr = {'Authorization':'Bearer '+UsrToken}

def PrintMsg(msgs):
        print('total messages: '+str(len(msgs))+'\n'+'-'*20)
        global MsgInServer
        MsgNo=len(msgs) - MsgInServer
        MsgInServer = len(msgs)
        if not MsgNo == 0:
            for N in range(MsgNo):
                print ('from: '+msgs[N]['from'])
                print('subject: '+msgs[N]['subject'])
                print('Body: '+msgs[N]['body'])
                print('Has attachment: '+str(msgs[N]['hasAttachments']))
                print('Craeted '+msgs[N]['createdAt'])
                print("\033[95m {}\033[00m" .format('-'*20))

def CheckMsgNo(msgs):
    try:
        if len(msgs) > MsgInServer:
            return True
        else:
            return False
    except:
        return False

def CheckMsg():
    msgs=GetMsg(hdr)
    if not msgs=='0':
        if CheckMsgNo(msgs):
            PrintMsg(msgs)
        else:
            logging.info('No New messages')
    else: sys.exit()

schedule.every(10).seconds.do(CheckMsg)

while True:
# start infinate loop
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt as e:
        print(' Ctrl-C presses\nExiting program\nDeleting account')
        accountID=GetMe(hdr)['id']
        if DelAccount(accountID,hdr):
            print("\033[91m {}\033[00m" .format('--Account deleted--'))
        break
