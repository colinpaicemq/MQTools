import pymqi
import mqtools.mqpcf as mqpcf
import mqtools.MQ as MQ # for formatMQMD
#import formatMQMD as formatMQMD
import json

import sys

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-qm',required=True,default="QMA")
parser.add_argument('-channel', required=True, default="QMACLIENT")
parser.add_argument('-conname', required=True, default='localhost(1415)')
parser.add_argument('-queue', required=True, default='SYSTEM.ADMIN')
#parser.add_argument('-userid', required=False, default='')
#parser.add_argument('-password', required=False, default=None)
args = parser.parse_args()


queue_manager = args.qm
channel = args.channel
conn_info = args.conname
queue_name = args.queue

pcf = mqpcf.mqpcf()

try:
    qmgr = pymqi.connect(queue_manager,channel,conn_info)
except  pymqi.MQMIError as e:
    print(queue_manager, channel, conn_info)  
    print("pymqi.MQMIError: ",e)
    raise

#  Set up the queue for putting to the admin queue
hAdmin = pcf.get_h_admin_queue(qmgr)
# get the reply to queue - uses model queue if non specified
hReply = pcf.get_h_reply_queue(qmgr)

message= pcf.create_request("INQUIRE_Q"
                            ,{"Q_NAME":queue_name}
                           
                  
                   )
# to check what was sent - decode the string
# header, data =mqpcf.parseData(buffer=message,strip="no",debug=0 )

# Prepare a Message Descriptor for the request message.
# Set the required fields
md = pcf.create_admin_MD(hReplyToQ=hReply) 

# issue the request
hAdmin.put(message, md)

# we now need to get the replies
md = pymqi.MD()
gmo = pymqi.GMO()
gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING | pymqi.CMQC.MQGMO_CONVERT
gmo.WaitInterval = 1000 # 1 seconds

try:
    # loop around looking for messages
    # Once a message has been got, get the rest of messages with the same msgid
    # and correlid
    # if no more messages, then need to clear these fields to get next available
    # messages 
    # for i in range(100): 
    while True:
        data = hReply.get(None,md, gmo )
        md.set(MsgId=b'') # clear this so we get rest of messages in group
        header, data = pcf.parse_data(buffer=data, strip="yes", debug=0)
        print("header=",header)
        if (header["Reason"] != 0):
            mqpcf.eprint("Reason mqcode:",pcf.header["sReason"])
            mqpcf.eprint("error return:",header)
            
        if header["Control"] == "LAST":
            md.set(MsgId=b'')
            md.set(CorrelId=b'')
        newMD = MQ.format_MQMD(md)
        ret = {}  
        ret["header"]= header
        ret["data"] = data
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
