import pymqi
import mqtools.mqpcf as mqpcf
#import formatMQMD as formatMQMD
import json
from ruamel.yaml import YAML
import sys

def dumpData(data):
   
        if "Q_NAME"  in data:
            qname = data["Q_NAME"]
            fn = "./queues/"+qname+".yml"
   
            with open(fn, 'w') as outfile:
                print("file name",fn)
                yaml.dump(data, outfile)
        elif "CHANNEL_NAME"  in data:
            name = data["CHANNEL_NAME"]
            fn = "./channel/"+name+".yml"

     
            with open(fn, 'w') as outfile:
                print("file name",fn)
                yaml.dump(data, outfile)

        else: yaml.dump(data, sys.stdout)


queue_manager = 'QMA'
channel = "QMACLIENT"
conn_info = "127.0.0.1(1414)"

yaml=YAML()
yaml.indent(mapping=4, sequence=6, offset=3)

 
pcf = mqpcf.mqpcf()

try:
    qmgr = pymqi.connect(queue_manager,channel,conn_info)
#  qmgr = pymqi.connect(queue_manager, channel, conn_info, userid, password)  
except  pymqi.MQMIError as e:
    print(queue_manager, channel, conn_info)  
    print("pymqi.MQMIError: ",e)
    raise

#  Set up the queue for putting to the admin queue
hAdmin = pcf.get_h_admin_queue(qmgr)
# get the reply to queue - uses model queue if non specified
hReply = pcf.get_h_reply_queue(qmgr)

message= pcf.create_request(#"INQUIRE_Q_STATUS"
                             # ,{"Q_NAME":"AMQ*"}
                             #       ,{"CURRENT_Q_DEPTH":("EQ",0)}
                             # ,{"OPEN_TYPE":"ALL"}
                             "INQUIRE_CHLAUTH_RECS" 
                             ,{"CHANNEL_NAME":"*"} 
                             #       "INQUIRE_CHANNEL"
                             #     ,{"CHANNEL_NAME":("*")}
                             #     ,{"CHANNEL_NAME":("GT","A")}
                  
                   )
# to check what was sent - decode the string
# header, data =mqpcf.parseData(buffer=message,strip="no",debug= 0)

# Prepare a Message Descriptor for the request message.
# Set the required fields
md = pcf.create_admin_MD(hReplyToQ=hReply) 

# issue the request
hAdmin.put(message, md)

# we now need to get the replies
md = pymqi.MD()
gmo = pymqi.GMO()
gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
gmo.WaitInterval = 1000 # 1 seconds

try:
    # loop around looking for messages
    # Once a message has been got, get the rest of messages with the same msgid
    # and correlid
    # if no more messages, then need to clear these fields to get next available
    # messages 
    for i in range(100): 
        data = hReply.get(None,md, gmo )
        md.set(MsgId=b'') # clear this so we get rest of messages in group
        header, data = pcf.parse_data(buffer=data, strip="yes", debug= 0)
        if (header["Reason"] != 0):
            mqpcf.eprint("Reason code:",pcf.header["sReason"])
            mqpcf.eprint("error return:",header)
            
        if header["Control"] == "LAST":
            md.set(MsgId=b'')
            md.set(CorrelId=b'')
        newMD = mqpcf.format_MQMD(md)
        ret = {}  
        ret["Header"]= header
        ret["Data"] = data
        ret["MD"] = newMD
        
        js = json.dumps(ret)
        print(js,flush=True)
        
        # dumpData(data) 
except pymqi.MQMIError as e:
    if (e.reason) != 2033: 
        print("exception :",e, e.comp, e.reason)

hAdmin.close()
hReply.close()
 
qmgr.disconnect()
