import mqtools.smqpcf as SMQPCF
import json
import string
def format_MQMD(md,strip="yes", debug="no"):
    """
    format_MQMD(md) formats and MD replacing bytestrings with 0x0... if necessary
    
    We need to do this as json cannont handle \x00 etc in strings
    """

    mdlist = {"Report":"MQRO",
            "MsgType":"MQMT",
            "Feedback":"MQFB",
            "Persistence":"MQPER",
            "PutApplType":"MQAT"
    
             }
    if debug != "no":
        print("formatMQMD:strip=",strip)
    newMD = md.get()
    # print("newmd",newMD)
    # convert integers to strings for those fields that need it
    # as define above in mdlist
    for l in mdlist:
        newMD[l]= SMQPCF.sMQLOOKUP.get((mdlist[l], newMD[l]), newMD[l])
    
    printable_chars = set(bytes(string.printable, 'ascii'))
    for x in newMD:
        xx = newMD[x] # copy each field across
        if debug != "no":
               print("formatMQMD:",x,xx,type(xx)) 
        if isinstance(newMD[x],bytes):
            z = bytearray(newMD[x])
            # check to see if the whole string is printable 
            printable = all(char in printable_chars for char in z)
            if debug != "no":
               print("formatMQMD:Printable",printable) 
            if printable == True:
                newMD[x] =xx.decode() # convert to string
                if strip != "no":
                    newMD[x]= newMD[x].rstrip()     
            else:
                newMD[x] = "0x"+newMD[x].hex() # convert it to hex
        else:
            pass        
    return newMD    

def oldformat_MQMD(md, strip="yes", debug="no"):
    mdlist = {"Report":"MQRO",
            "MsgType":"MQMT",
            "Feedback":"MQFB",
            "Persistence":"MQPER",
            "PutApplType":"MQAT"
    
             }
    newMD = md.get()
    # print("newmd",newMD)
    print("DEBUG",debug)
    if debug != "no":
         print("formatMQMD strip:",strip)
    for l in mdlist:
        newMD[l]= SMQPCF.sMQLOOKUP.get((mdlist[l], newMD[l]), newMD[l])
    printable_chars = set(bytes(string.printable, 'ascii'))
    for x in newMD:
        xx = newMD[x]
        if debug != "no":
           print("formatMQMD:",x,xx,type(xx))   
        if isinstance(newMD[x],bytes):
            z = bytearray(newMD[x])
            printable = all(char in printable_chars for char in z)
            if printable == True:
                newMD[x] =xx.decode()
            else:
                newMD[x] = "0x"+newMD[x].hex()
        elif isinstance(newMD[x],str):
             if strip == "yes":
                newMD[x] = newMD[x].rstrip()                       

                      
    #newMD["MsgId"]=newMD["MsgId"].__str__()
    #newMD["CorrelId"]=newMD["CorrelId"].hex() 
    #newMD["AccountingToken"]=newMD["AccountingToken"].__str__()
    
    return newMD
