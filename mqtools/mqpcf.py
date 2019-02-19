import pymqi as pymqi
from .  import smqpcf as SMQPCF
from .  import mqpcfget as mqpcfget
from . import  mqpcfset as mqpcfset
from sys import stderr
import string

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

"""
q090210_.htm

MQIA_* (Integer Attribute Selectors)
MQIACF_* (Command format Integer Parameter Types)
MQIACH_* (Command format Integer Channel Types)
MQIAMO_* (Command format Integer Monitoring Parameter Types)
MQIAMO64_* (Command format 64-bit Integer Monitoring Parameter Types)


selectTypeS= {
  "ACCOUNTING_TOKEN": ("MQBACF",7010),
  "ALTERNATE_SECURITYID": ("MQBACF",7019),
  "CF_LEID": ("MQBACF",7014),

sLookupToI = {

,("MQACTP","FORWARD"): 1 
,("MQACTP","NEW"): 0 
,("MQCA","APPL_DESC"): 3174 

sLookupTypes ={
  20:"MQQT" 
, 134:"MQMON" 
, 123:"MQMON" 
, 128:"MQMON" 
, 4:"MQOO" 
, 57:"MQIT" 
, 9:"MQQA_IG"

sMQLOOKUP = {
,("MQBT",1): "OTMA" 
,("MQCA",3134): "ACTIVITY_DESC" 
,("MQCA",3172): "ADMIN_TOPIC_NAMES
,("MQCMD",9): "CLEAR_Q" 
,("MQCMD",184): "CLEAR_TOPIC_STRING" 
,("MQCMD",99): "COMMAND_EVENT" 
,("MQRC",2386): "AUTH_INFO_TYPE_ERROR" 
,("MQRC",2003): "BACKED_OUT" 
,("MQRC",2362): "BACKOUT_THRESHOLD_REACHED" 
,("MQRC",2303): "BAG_CONVERSION_ERROR" 
,("MQRC",2326): "BAG_WRONG_TYPE" 
 

"""


class mqpcf(object):

    """PCF()
    Process IBM MQ PCF objects.  Create messages with commands and parse data
    
    MQPCFSET  is used to create the PCF message
    MQPCFGET is used to parse a passed in message in PCF format
    
    """

    def __init__(self):
        self.pcfset = mqpcfset.mqpcfset()        
        self.pcfget = mqpcfget.mqpcfget()
       
    def create_request(self,request,*args):
        """ Call the MQPCFSET to do the work"""
        ret= self.pcfset.create_request(request, *args)   
        return ret
    
    def parse_data(self, buffer='', strip="no", debug="no"):
        """ Call the MQPCFGET to do the work"""
        ret = self.pcfget._parse_data(buffer, strip, debug)
        return ret
    
    def getAllData(self):
        """
        return the all the parsed data
        """
        return self.all_data
    
    def get_h_admin_queue(self,qmgr=None,queue=b'SYSTEM.ADMIN.COMMAND.QUEUE'):
        admin = pymqi.OD()
        #   print("getAdminQueue",type(qmgr),type(queue))
        if not isinstance(queue,bytes):
            queue = queue.encode()
        if qmgr is None:
            raise ValueError("QMGR name must be specified")
        admin.ObjectName = queue
        hAdmin = pymqi.Queue(qmgr, admin, pymqi.CMQC.MQOO_OUTPUT)
        return hAdmin
        #
        # get replyqueue - by default create a dynamic queue
        #    
    def get_h_reply_queue(self,qmgr=None,queue=None):
        """ create a queue object using passed, or default queue name"""
        if (queue is None):
            queue=b'SYSTEM.MQSC.REPLY.QUEUE'
        hReply = pymqi.Queue(qmgr,queue,pymqi.CMQC.MQOO_INPUT_SHARED|
                             pymqi.CMQC.MQOO_INQUIRE)
        return hReply
     
        #def getAdminMD(self):
        #    """
        #    Create an MQMD for reply to queue
        #    """
        #    md = pymqi.MD()
        #    md.ReplyToQ = b'CP0000'
        #    md.MsgType = pymqi.CMQC.MQMT_REQUEST
        #    md.Feedback = pymqi.CMQC.MQFB_NONE
        #    md.Format = pymqi.CMQC.MQFMT_ADMIN
        #   return md
    

        
    def create_admin_MD(self,hReplyToQ=None):
        """
        Create an MQ for reply to queue, and fillin the replyto queue
        """
                   
        md = pymqi.MD() # create an MD
        if hReplyToQ is None:
            raise ValueError("You must specify the hReplOD in getAdminMD, to provide the reply to queue")
        qname = hReplyToQ.inquire(pymqi.CMQC.MQCA_Q_NAME)
        # and fill in the fields
        md.ReplyToQ = qname
        md.MsgType = pymqi.CMQC.MQMT_REQUEST
        md.Feedback = pymqi.CMQC.MQFB_NONE
        md.Format = pymqi.CMQC.MQFMT_ADMIN
        return md
        
    def resetMD(self,md=None):
        """
        Clear the msgid and correlid fields in the MD
        """        
        if md is None:
            raise ValueError("You must specify the MD to reset")
        md.MsgId = b'' 
        md.Correlid = b''
        md.MsgType = pymqi.CMQC.MQMT_REQUEST
        md.Feedback = pymqi.CMQC.MQFB_NONE
        md.Format = pymqi.CMQC.MQFMT_ADMIN
        return md    
        
def format_MQMD(md):
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
    newMD = md.get()
    # print("newmd",newMD)
    # convert integers to strings for those fields that need it
    # as define above in mdlist
    for l in mdlist:
        newMD[l]= SMQPCF.sMQLOOKUP.get((mdlist[l], newMD[l]), newMD[l])
    
    printable_chars = set(bytes(string.printable, 'ascii'))
    for x in newMD:
        xx = newMD[x] # copy each field across
        if isinstance(newMD[x],bytes):
            z = bytearray(newMD[x])
            # check to see if the whole string is printable 
            printable = all(char in printable_chars for char in z)
            if printable == True:
                newMD[x] =xx.decode() # convert to string
            else:
                newMD[x] = "0x"+newMD[x].hex() # convert it to hex
    return newMD    
    
def lookup_reason(reason):
    """ Lookup reason code from number of string """
    return  SMQPCF.sMQLOOKUP.get(("MQRCCF", reason), reason)
# in case this is executed on its own    
if (__name__ == '__main__'):
    pass