#!/usr/bin/python
import urllib
import json
import tokens
import datetime
import argparse

def getDecimals(amount, precision):
  i = precision - len(amount)
  if i > 0:
    k=0
    while k<i:
      amount = "0"+ amount
      k=k+1

  length = len(amount) 
  subst = length  - precision
  ret = amount[0:subst] + "," + amount[subst:7]
  if ret[0:1] ==",":
    ret = "0"+ret
    
  if ret[-1:]==',':
    ret= ret[:-1]
  return ret
  
def calcPrice(a, b):
  c = float(a.replace(',','.'))
  d = float(b.replace(',','.'))
  if d>0:
    ret = repr(c / d)
  else:
    ret = repr(c / 1)
  return ret.replace('.',',') 
  
def fileOpen(name, mode):
  csv = open(name, mode) 
  csv.write("BLOCK")   
  csv.write(";")      
  csv.write("TXID") 
  csv.write(";")
  csv.write("TYPE")
  csv.write(";")
  csv.write("TRADE")
  csv.write(";")
  csv.write("TIMESTAMP")  
  csv.write(";")
  csv.write("PAIR")
  csv.write(";")
  csv.write("PRICE");
  csv.write(";")
  csv.write("AMOUNT");
  csv.write(";")
  csv.write("AMOUNT ETH");
  csv.write(";")
  csv.write("PROCEEDS")
  csv.write(";")
  csv.write("PROCEEDS COIN")
  csv.write(";")
  csv.write("BUYER")
  csv.write(";")
  csv.write("SELLER")
  csv.write("\n")  
  return csv

def getTradesInBlockRange(url, f, my):
  try:
    page = json.loads(urllib.urlopen(url).read())
    result = page['result']
    #loop all possible transaction in block range
    for i in result:
    #is anywhere my adress mentioned?
      if my in i['data']:
      
        blockNumberRaw = i['blockNumber']
        timeStampRaw   = i['timeStamp']
        txid           = i['transactionHash']
        data           = i['data'][2:]
        gasPriceRaw    = i['gasPrice']
        gasUsedRaw     = i['gasUsed']
        
        blockNumber     = str(int(blockNumberRaw,16)) 
        timeStamp       = int(timeStampRaw,16) 
        
        timeStampstring = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')
        tokenGet        = '0x' + data[24:64]
        amountGetRaw    =        data[65:128]
        tokenGive       = '0x' + data[152:192]
        amountGiveRaw   =        data[193:256]
        maker           = '0x' + data[280:320]
        taker           = '0x' + data[343:384]
        print "Trade in block " + blockNumber +" detected"
        
        try:
           tokenGetName    = edTokens[tokenGet].name
           tokenGetDecimal = edTokens[tokenGet].decimal
        except Exception, e:
           tokenGetName = tokenGet
           tokenGetDecimal = 1
        try:
           tokenGiveName = edTokens[tokenGive].name
           tokenGiveDecimal = edTokens[tokenGive].decimal
        except Exception, e:
           tokenGiveName = tokenGive   
           tokenGiveDecimal = 1      
        
        amountGive = int(amountGiveRaw,16)
        amountGet  = int(amountGetRaw, 16)
        
        amountGive = getDecimals(str(amountGive), tokenGiveDecimal)
        amountGet  = getDecimals(str(amountGet), tokenGetDecimal) 
        
        if my in taker:
          type = 'TAKER'
        else:
          type = 'MAKER'
          
        if my in taker:
          if tokenGetName !='ETH':
            order = 'SELL'
            buyer = maker
            seller= taker
            zweig = '1'
          else:
            order = 'BUY'
            buyer = taker
            seller= maker
            zweig = '2'
        else:
          if tokenGetName !='ETH':
            order = 'BUY'
            buyer = maker
            seller= taker
            zweig = '3'
          else:
            order = 'SELL'
            buyer = taker
            seller= maker
            zweig = '4'
        
        if tokenGetName =='ETH':
          price = calcPrice(amountGet,amountGive)
          amountETH = str(amountGet)
          amountAlt = str(amountGive)
          pair = tokenGiveName + "/ETH"
        else:
          price = calcPrice(amountGive,amountGet)
          amountETH = str(amountGive)
          amountAlt = str(amountGet)
          pair = tokenGetName + "/ETH"
        
        if order == 'BUY':
          turnover    = "-"+amountETH 
          turnoverAlt = amountAlt        
        else:
          turnover = amountETH   
          turnoverAlt = "-"+amountAlt  
           
        f.write(blockNumber)   
        f.write(";")      
        f.write(txid) 
        f.write(";")
        f.write(type)
        f.write(";")
        f.write(order)      
        f.write(";")
        f.write(timeStampstring)  
        f.write(";")
        f.write(pair)
        f.write(";")
        f.write(price);
        f.write(";")
        f.write(amountAlt);
        f.write(";")
        f.write(amountETH);
        f.write(";")
        f.write(turnover)
        f.write(";")
        f.write(turnoverAlt)
        f.write(";")
        f.write(buyer)
        f.write(";")
        f.write(seller)   
        f.write("\n")
        f.flush() 
  except Exception, e:
    f.write("ERROR")
    f.write(";")
    f.write(e)
   
def getTrades(p_fromBlock, p_toBlock, ethereumAdress):
  file = fileOpen("trades_" +ethereumAdress+".csv", "a")
  p_static_iteration =10
  
  p_url = "https://api.etherscan.io/api?module=logs&action=getLogs&fromBlock=$1&toBlock=$2&address=0x8d12a197cb00d4747a1fe03395095ce2a5cc6819&topic0=0x6effdda786735d5033bfad5f53e5131abcced9e52be6c507b62d639685fbed6d&apikey=PWYCPV9Y82AE9HC9YVMQ7RGJZ7TS3E15MB"
  
  fromBlock = p_fromBlock - p_static_iteration -1
  toBlock   = p_fromBlock
  while True:
    if toBlock >= p_toBlock:
      break
    fromBlock = fromBlock + p_static_iteration + 1
    toBlock   = fromBlock + p_static_iteration
    if toBlock > p_toBlock:
      toBlock = p_toBlock
      
    fromBlock = str(fromBlock)
    toBlock   = str(toBlock)
    
    print "reading blocks from " + fromBlock + " to " + toBlock
    call = p_url.replace("$1", fromBlock).replace("$2", toBlock) 
    getTradesInBlockRange(call, file,ethereumAdress[2:])
  file.close()

parser = argparse.ArgumentParser()
parser.add_argument("fromBlock", help="from block", type=int)
parser.add_argument("toBlock", help="to block", type=int)
parser.add_argument("ETHAdress", help="your ethereum address")
args = parser.parse_args()

edTokens           = tokens.getTokens()
getTrades(args.fromBlock,args.toBlock, args.ETHAdress)