import sys
import json

while True: 
   line = sys.stdin.readline()
   if not line: break
   j = json.loads(line) 
   if not "data1" in j:
      print(line)
   data1 = j["data1"]
   otype = j["data1"]["OBJECT_TYPE"]+"_NAME"
   oname = j["data1"][otype]
   # print(json.dumps(j, indent=2,separators=(',', ':')))
   if j["reason"] == "CONFIG_CHANGE_OBJECT":
    
     
      if "data2" in j:
         data2 = j["data2"]
         #otype = data1["OBJECT_TYPE"]+"_NAME" 	
         for i in data1:
            if (data1[i]!=data2[i]):
               print("difference",otype,oname,data2[otype],i,data1[i],data2[i]) 
   elif j["reason"] == "CONFIG_CREATE_OBJECT":
       #print line
       print("Create",otype,oname,data1[otype])
   else:
     print("Delete",otype,oname,data1[otype])
 #     #    pass
 #  else: 
 #     pass
# print(j)  
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
