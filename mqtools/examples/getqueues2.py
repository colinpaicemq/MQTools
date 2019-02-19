import sys
import json
from ruamel.yaml import YAML

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
yaml.indent(mapping=4, sequence=6, offset=3)

 


while True: 
   line = sys.stdin.readline()
   if not line: break
   j = json.loads(line) 
   dumpData(j['data'])
   
