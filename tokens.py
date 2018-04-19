import urllib
import json
class tokens(object):
   name = ""
   adress = ""
   decimal = ""

   # The class "constructor" - It's actually an initializer 
   def __init__(self, name, adress, decimal):
       self.name = name
       self.adress = adress
       self.decimal = decimal

def getTokens():
    edtokens = "https://raw.githubusercontent.com/forkdelta/forkdelta.github.io/master/config/main.json"
    edTokenResponse = urllib.urlopen(edtokens)
    edTokendata = json.load(edTokenResponse)   
    edTokendata = edTokendata['tokens'] 
    
    allTokens={}
    allTokens['0x0000000000000000000000000000000000000000'] = tokens('ETH', '0x0000000000000000000000000000000000000000', 18)
    for i in range(len(edTokendata)):
      allTokens[edTokendata[i]['addr']] = tokens(edTokendata[i]['name'], edTokendata[i]['addr'], edTokendata[i]['decimals'])
    return allTokens
