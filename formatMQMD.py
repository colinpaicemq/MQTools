import mqtools.mqpcf.smqpcf as SMQPCF
import json
import string

def formatMQMD(md):
    mdlist = {"Report":"MQRO",
            "MsgType":"MQMT",
            "Feedback":"MQFB",
            "Persistence":"MQPER",
            "PutApplType":"MQAT"
    
             }
    newMD = md.get()
    # print("newmd",newMD)
    for l in mdlist:
        newMD[l]= SMQPCF.sMQLOOKUP.get((mdlist[l], newMD[l]), newMD[l])
    printable_chars = set(bytes(string.printable, 'ascii'))
    for x in newMD:
        xx = newMD[x]
        if isinstance(newMD[x],bytes):
            z = bytearray(newMD[x])
            printable = all(char in printable_chars for char in z)
            if printable == True:
                newMD[x] =xx.decode()
            else:
                newMD[x] = "0x"+newMD[x].hex()

                      
    #newMD["MsgId"]=newMD["MsgId"].__str__()
    #newMD["CorrelId"]=newMD["CorrelId"].hex() 
    #newMD["AccountingToken"]=newMD["AccountingToken"].__str__()
    
    return newMD
