import sys
from ruamel.yaml import YAML
import json

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



yaml=YAML()



print (sys.version_info)
for x in range(100):
 line = sys.stdin.readline()

 if not line: break
 # print("==line==",line,"!")
 j = json.loads(line) 
 print(json.dumps(j, indent=2,separators=(',', ':')))
 
 
