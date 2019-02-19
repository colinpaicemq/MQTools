from ruamel.yaml import YAML
import sys
"""
Compares the MQ Object definitons in YAML format files and prints the differnces
ignoring irrelevant fields
"""
 
yaml=YAML()

q1 = sys.argv[1]

ignore = ["ALTERATION_DATE","ALTERATION_TIME","CREATION_DATE","CREATION_TIME"]
    
in1 =  open(q1, 'r')  # open the first queue 
queue_info1 = yaml.load(in1)  # and read the contents in


for i in range(2,len(sys.argv)): # for all of the other parameters
  
  q2=sys.argv[i]                 # get the name of the file
  in2 = open(q2, 'r')            # open the file
  queue_info2 = yaml.load(in2)   # read it in
 

  for e in queue_info1:          # for each parameter in file 1
     x1 = queue_info1[e]         # get the value from file 1
     x2 = queue_info2[e]         # get the value from the other file
     if not e in ignore:         # some parameters we want to ignore
       if x1 != x2:              # if the parameters are different
          print(q1,q2,":",e,x1,"/",x2)   # print out the queuenames, keywork and values

 



