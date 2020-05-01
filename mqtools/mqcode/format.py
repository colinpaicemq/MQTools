"""
Format MQ control blocks
"""
import mqtools.smqpcf as SMQPCF
import json
import string
import struct

def format(buffer, strip="yes", debug=0):
    debug = debug
    if debug > 0:
        print("TYPE",type(buffer),len(buffer))
    
    if "StrucId" in buffer:
        if buffer["StrucId"] == b'RFH ':
            buffer = format_RFH(buffer,strip="yes", debug=0) 
        else:       
            print("==Formatting is not supported yet", buffer["StrucId"])
    else: 
         print("==Control block is not recognised")
    return buffer            
   
def format_RFH(rfh,strip="yes", debug=0):
    """
    format_RFH(rfh) formats an RFH  replacing bytestrings with 0x0... if necessary
    
    We need to do this as json cannont handle \x00 etc in stringss
    """ 
    for r in rfh:
        rfh[r] = _printable(rfh[r],strip=strip)
    return rfh  
            
       
def format_MQMD(md,strip="yes", debug=0):
    """
    format_MQMD(md) formats an MD replacing bytestrings with 0x0... if necessary
    
    We need to do this as json cannont handle \x00 etc in strings
    """

    mdlist = {"Report":"MQRO",
            "MsgType":"MQMT",
            "Feedback":"MQFB",
            "Persistence":"MQPER",
            "PutApplType":"MQAT"
    
             }
    if debug > 0:
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
        if debug > 0:
               print("formatMQMD:",x,xx,type(xx)) 
        if isinstance(newMD[x],bytes):
            z = bytearray(newMD[x])
            # check to see if the whole string is printable 
            printable = all(char in printable_chars for char in z)
            if debug > 0:
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


def _get4():
    """
    Get the next 4 bytes from buffer(offsetData) and move the pointer
    """
    if data_offset + 4 > buffer_length:
        print("_get4:", data_offset, buffer_length)
        raise ValueError("MQPCF Trying to get past the end of the buffer")
    longi = struct.unpack('i', buffer[data_offset:data_offset + 4])
    data_offset = data_offset + 4
    # unpack always returns a tuple - so just get the first one
    return longi[0]

def _printable(instring,strip="yes"):
    if not isinstance(instring,bytes):
        return instring
    printable_chars = set(bytes(string.printable, 'ascii'))
    z = bytearray(instring)
    # check to see if the whole string is printable 
    printable = all(char in printable_chars for char in z)
    #if debug > 0:
    #   print("format:Printable",printable) 
    if printable == True:
        outstring =instring.decode() # convert to string
        if strip != "no":
            oustring= outstring.rstrip()     
    else:
        outstring = "0x"+instring.hex() # convert it to hex
    return outstring