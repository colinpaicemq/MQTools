"""
Program to get and process PCF messages from an IBM MQ Queue

Input parameters:
-qm queue_manager_name
<-channel channel name>
<-conname 'ipaddress(1414)' >
<-userid  userid> 
<-password <Password_value> >  if password_value not specificied then it prompts
-queue   q_name  the name of the queue to be processed
< -debug n value from 0 to 9 

Output:
json formatted output to stdout, which can be piped to other programs such as python3 pretty_json

Note:
Trying to use local bindings you get 
pymqi.MQMIError: MQI Error. Comp: 2, Reason 2058: FAILED: MQRC_Q_MGR_NAME_ERROR

as pymqi has been build with client libraries
Disallow 

"""

import pymqi
import mqtools.mqpcf as MQPCF
import datetime
import json
import argparse
import sys
import getpass
import struct
import string
import mqtools.MQ as MQ # for formatMQMD

valid_queues = ''.join(("Specify the queue to be processed.  System queues include:",
                    "SYSTEM.ADMIN.ACCOUNTING.QUEUE, ",
                    "SYSTEM.ADMIN.ACTIVITY.QUEUE, ",
                    "SYSTEM.ADMIN.CHANNEL.EVENT, ",
                    "SYSTEM.ADMIN.COMMAND.EVENT, ",
                    "SYSTEM.ADMIN.CONFIG.EVENT, ",
                    "SYSTEM.ADMIN.LOGGER.EVENT, ",
                    "SYSTEM.ADMIN.PERFM.EVENT, ",
                    "SYSTEM.ADMIN.PUBSUB.EVENT, ",
                    "SYSTEM.ADMIN.QMGR.EVENT, ",
                    "SYSTEM.ADMIN.STATISTICS.QUEUE, ",
                    "SYSTEM.ADMIN.TRACE.ACTIVITY.QUEUE", 
                    "SYSTEM.ADMIN.TRACE.ROUTE.QUEUE, "))
parser = argparse.ArgumentParser()
parser.add_argument('-qm',required=True,default="QMA")
parser.add_argument('-channel', required=True, default=None)
parser.add_argument('-conname', required=True, default=None)
parser.add_argument('-queue', required=True, default=None, help=valid_queues)
parser.add_argument('-userid', required=False, default=None)
parser.add_argument('-password', required=False, default=None)
parser.add_argument('-count', required=False, default=999999,type=int,
                    help="count of messages to process")
parser.add_argument('-wait', required=False, default=5,type=int,
                    help="MQGETWait time in seconds")
parser.add_argument('-debug', required=False, default=0,type=int,
                    help="For internal debugging")
args = parser.parse_args()

if args.queue == "?":
    MQPCF.eprint("Possible SYSTEM.* queues include:",valid_queues )
    exit(0)     



queue_name = 'SYSTEM.ADMIN.QMGR.EVENT'

#
#if args.conname is None:
#    raise ValueError('You must connect using client connection and connname was not specfied')
#    try:
#        qmgr = pymqi.connect(args.qm)
#    except  pymqi.MQMIError as e:
#        MQPCF.eprint("==== pymqi.connect(qm)",args.qm)
#        MQPCF.eprint("pymqi.MQMIError:",e)
#        raise
#elif userid == '': # non specified 
if args.userid is None: # non specified 
    try:
        qmgr = pymqi.connect(args.qm,
                            args.channel,
                            args.conname)
    except  pymqi.MQMIError as e:
        MQPCF.eprint("pymqi.MQMIError:",e)
        MQPCF.eprint("pymqi.connect(qm,channel,conname)",
              args.qm, args.channel, args.conname)
        raise
else:
    try:
        password = args.password
        if password is None:
            password =  getpass.getpass()
        qmgr = pymqi.connect(args.qm,
                            args.channel,
                            args.conname,
                            args.userid,
                            password)                   
    except  pymqi.MQMIError as e:
        MQPCF.eprint("pymqi.connect(qm,channel,conname,userid,password)",
              args.qm, args.channel, args.conname, args.userid,"********")
        MQPCF.eprint("pymqi.MQMIError: ",e)
        raise

mqpcf = MQPCF.mqpcf()
# open the events queues

od = pymqi.OD()
od.ObjectName = args.queue.encode() # passed value was a string - needs to be b''
input_open_options = pymqi.CMQC.MQOO_INPUT_EXCLUSIVE
input_queue = pymqi.Queue(qmgr,od, input_open_options)


#mqpcf = MQPCF.MQPCF()

md = pymqi.MD()
gmo = pymqi.GMO()
md = pymqi.MD()
gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
gmo.WaitInterval = args.wait * 1000 # 20  seconds
start = ''
try:
    for i in range(args.count):
        md = pymqi.MD()
        rfh = []
        mqpcf.resetMD(md=md)
#       msg = input_queue.get_rfh2(None, md, gmo,rfh )
        msg = input_queue.get_rfh2(None, md, gmo)
        now = datetime.datetime.now()
        if start == "":
           start = now  
        delta = now - start  
        #MQ.format(rfh)
        rfh2s = []
       
       
        newMD = MQ.format_MQMD(md)
        if args.debug > 0:
            MQPCF.eprint("MQMD:",newMD )
      
        if newMD["Format"] == "MQADMIN":

            if len(msg) < 36:
               header = {"sReason":"Missing data"}
               data = {}
            else:
                PCFheader, PCFdata =mqpcf.parse_data(buffer=msg, strip="yes", debug=args.debug)
            ret= {"reason":PCFheader["sReason"],
                "MQMD":newMD,
                "PCFheader":PCFheader,
                "PCFData":PCFdata,
                "time":now.__str__(),
                "delta":delta.__str__()
                }

        elif newMD["Format"] == "MQHEPCF":  # embedded PCF
            if args.debug > 0:
                MQPCF.eprint("MQHEPCF:",msg[0:4])
            lData   = struct.unpack('i', msg[8:8+4])
       
            if args.debug > 0:
                MQPCF.eprint("MQHEPCF length:",lData[0]," buffer length",len(msg))
            msg     = msg[32:lData[0]]; # from ... offset 32 - to the end
            if args.debug > 0:
                MQPCF.eprint("MQHEPCF msg size now :",len(msg))

            if len(msg) < 36:
               header = {"sReason":"Missing data"}
               data = {}
            else: 
                header, data =mqpcf.parse_data(buffer=msg, strip="yes", debug=args.debug)       
            ret= {"reason":header["sReason"],
                  "MQMD":newMD,
                  "PCFheader":header,
                  "PCFData":data,
                  "time":now.__str__(),
                  "delta":delta.__str__()
                 }
        elif newMD["Format"] == "MQSTR":  # embedded PCF
             print("==============================",type(newMD["Format"]))
             print(newMD)
           #  print("problem with ",msg)
             msg = msg.decode("UTF-8")
             header = {"sReason":"????"}
             data =  {"body":msg}
             ret= {"reason":header["sReason"],
                  "MQMD":newMD,
                  "msg":msg,
                  "time":now.__str__(),
                  "delta":delta.__str__()
                 }
        else: 
             print("==============================",type(newMD["Format"]))
             print(newMD)
             print("problem with ",msg)
             printable_chars = set(bytes(string.printable, 'ascii'))

             if isinstance(msg,bytes):
                z = bytearray(msg)
                # check to see if the whole string is printable 
                printable = all(char in printable_chars for char in z)
                if printable == True:
                   msg =msg.decode() # convert to string
                  
                else:
                   msg = "0x"+msg.hex() # convert it to hex
            

         
            
             data =  {"body":msg}
             ret= {"sReason":"????",
                  "MQMD":newMD,
                  "msg":data,
                  "time":now.__str__(),
                  "delta":delta.__str__()
                 }
                 
   
        js = json.dumps(ret)
        print(js,flush=True) # needed so the next stage gets complete json

except pymqi.MQMIError as e:
    if (e.reason) != 2033: 
      MQPCF.eprint("exception :",e, e.comp, e.reason)
    else: MQPCF.eprint("message not found")
    

input_queue.close()
 
qmgr.disconnect()


