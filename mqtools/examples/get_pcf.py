"""
Program to get and process PCF messages from an IBM MQ Queue

Input parameters:
-qm queue_manager_name
<-channel channel name>
<-conname 'ipaddress(1414)' >
<-userid  userid> 
<-password <Password_value> >  if password_value not specificied then it prompts
-queue   q_name  the name of the queue to be processed

Output:
json formatted output to stdout, which can be piped to other programs such as python3 pretty_json

"""

import pymqi
import mqtools.mqpcf as MQPCF
import json
import argparse
import sys
import getpass

parser = argparse.ArgumentParser()
parser.add_argument('-qm',required=True,default="QMA")
parser.add_argument('-channel', required=False, default=None)
parser.add_argument('-conname', required=False, default=None)
parser.add_argument('-queue', required=True, default='SYSTEM.ADMIN')
parser.add_argument('-userid', required=False, default='')
parser.add_argument('-password', required=False, default=None)
args = parser.parse_args()



    



queue_name = 'SYSTEM.ADMIN.QMGR.EVENT'


if args.conname is None:
    try:
        qmgr = pymqi.connect(args.qm)
    except  pymqi.MQMIError as e:
        print("pymqi.MQMIError:",e)
        print("pymqi.connect(qm)",args.gm)
        raise
elif userid == '': # non specified 
    try:
        qmgr = pymqi.connect(args.qm,
                            args.channel,
                            args.conname)
    except  pymqi.MQMIError as e:
        print("pymqi.MQMIError:",e)
        print("pymqi.connect(qm,channel,conname)",
              args.gm, args.channel, args.conname)
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
        print("pymqi.MQMIError: ",e)
        print("pymqi.connect(qm,channel,conname,userid,password)",
              args.gm, args.channel, args.conname, args.userid,"********")
        raise

mqpcf = MQPCF.mqpcf()
# open the events queues
queue = pymqi.Queue(qmgr, args.queue)

od = pymqi.OD()

od.ObjectName=b'SYSTEM.ADMIN.QMGR.EVENT'

input_open_options = pymqi.CMQC.MQOO_INPUT_EXCLUSIVE
input_queue = pymqi.Queue(qmgr,od, input_open_options)


#mqpcf = MQPCF.MQPCF()

md = pymqi.MD()
gmo = pymqi.GMO()
md = pymqi.MD()
gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
gmo.WaitInterval = 1000 # 5 seconds

try:
   while True: 
      md = pymqi.MD()
      msg = input_queue.get(None, md, gmo )
      newMD = MQPCF.format_MQMD(md)
      header, data =mqpcf.parse_data(buffer=msg, strip="yes", debug="no")
      ret= {"reason":header["sReason"],
              "MQMD":newMD,
              "header":header,
              "data":data,
              }
   
      js = json.dumps(ret)
      print(js,flush=True) # needed so the next stage gets complete json

except pymqi.MQMIError as e:
    if (e.reason) != 2033: 
      MQPCF.eprint("exception :",e, e.comp, e.reason)
    else: MQPCF.eprint("message not found")
    

input_queue.close()
 
qmgr.disconnect()


