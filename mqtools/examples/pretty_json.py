"""
pretty_json routine to print out nicely formatted json
"""
import sys
import json

while True:
 line = sys.stdin.readline()

 if not line: 
     break
 j = json.loads(line) 
 print(json.dumps(j, indent=2,separators=(',', ':')))
 
 
