import pymqi
import mqtools.mqpcf as MQPCF
from ruamel.yaml import YAML
import sys
import json
 
queue_manager = 'QMA'

queue_name = 'SYSTEM.ADMIN.STATISTICS.QUEUE'

try:
  qmgr = pymqi.connect(queue_manager,"QMACLIENT","127.0.0.1(1414)")

except  pymqi.MQMIError as e:
  print(queue_manager, channel, conn_info)  
  print("pymqi.MQMIError: ",e)
  raise
mqpcf = MQPCF.mqpcf()
# open the events queues
queue = pymqi.Queue(qmgr, queue_name)

# Dynamic queue's object descriptor.
od = pymqi.OD()

od.ObjectName=b'SYSTEM.ADMIN.CONFIG.EVENT'

input_open_options = pymqi.CMQC.MQOO_INPUT_EXCLUSIVE
ReplyQ = pymqi.Queue(qmgr,od, input_open_options)


#mqpcf = MQPCF.MQPCF()

md = pymqi.MD()
gmo = pymqi.GMO()
md1 = pymqi.MD()
md2  = pymqi.MD()
gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
gmo.WaitInterval = 1000 # 5 seconds

try:
  for i in range(100):
  #while True: 
    md1 = pymqi.MD()
    msg1 = ReplyQ.get(None,md1, gmo )
    newMD1 = MQPCF.format_MQMD(md1)
    header1, data1 =mqpcf.parse_data(buffer=msg1,strip="yes",debug="no")
    # ret= {"MQMD":newMD,"Header":header1,"Data":data1}
    if header1["sReason"] == "CONFIG_CHANGE_OBJECT" and header1["Control"] !=  "LAST":
        # we need to get the second message
        #MQPCF.eprint("msgid1:",md1.get())
        # md2 = md1
        md1d = md1.get()
        md2  = pymqi.MD()
        md2.set(CorrelId = md1d["CorrelId"])
        # md2.set(MsgId=b'')        
        msg2 = ReplyQ.get(None,md2, gmo)
        #MQPCF.eprint("msgid2:",md2.get())
        header2, data2 = mqpcf.parse_data(buffer=msg2,strip="yes",debug="no")
        newMD2 = MQPCF.format_MQMD(md2)
        ret= {"reason":header1["sReason"],
              "MQMD1":newMD1,
              "header1":header1,
              "data1":data1,
              "MQMD2":newMD2,
              "header2":header2,
              "data2":data2}
    else: # not change
        ret= {"reason":header1["sReason"],
              "MQMD1":newMD1,
              "header1":header1,
              "data1":data1,
              }
   
    js = json.dumps(ret)
    print(js,flush=True)
    #md2 = pymqi.MD()
#    print(md2)
   # gmo.WaitInterval = 1000 # 5 seconds
    #MQPCF.eprint("get2")
    #msg2 = ReplyQ.get(None,md2, gmo )
    #MQPCF.eprint("after get2")
    #correlid1=md1["CorrelId"]
    #correlid2=md2["CorrelId"]
    #if (correlid1 != correlid2): print("Correlid do not match")
    #header2, data2 = mqpcf.parse_data(buffer=msg2,strip="yes",debug="no")
    #if (header2["Reason"] != 0):
    #   MQPCF.eprint("Reason code:",header2["sReason"])
    #   MQPCF.eprint("error return:",header2)    
 #  # l = list(data1)
 #   print("L",l[0],l)
   #
   # otype = data1["OBJECT_TYPE"]+"_NAME" 
    #for i in data1:
   #     if (data1[i]!=data2[i]): MQPCF.eprint("difference",otype,data1[otype],data2[otype],i,data1[i],data2[i])
 
except pymqi.MQMIError as e:
    if (e.reason) != 2033: 
      MQPCF.eprint("exception :",e, e.comp, e.reason)
    else: MQPCF.eprint("message not found")
    

ReplyQ.close()
 
qmgr.disconnect()


