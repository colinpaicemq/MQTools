#
# Copyright (c) 2018 Stromness Software Solutions.
# 
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# 
# * Contributors:
# *   Colin Paice - Initial Contribution
# 
# Use this file to process the output from runmqsc DIS QSTATUS(queue) to summarise
# the userids and appltags using the queue.
# For example on Linux
# echo "dis QSTATUS(CP000*) type(handle) all" |runmqsc QMA |python appltag.py
# produces
# (',q=CP0000,user=colinpaice,appltag=fromQMAJMS', 43)
# (',q=CP0000,user=colinpaice,appltag=oemput', 1)
# (',q=CP0002,user=colinpaice,appltag=COLINMDBCF', 36)
# (',q=CP0002,user=colinpaice,appltag=oemput', 1)
#
#  echo "dis conn(*) all  all "|runmqsc QMA |python appltag.py 
# produces
# (',user=colinpaice,appltag=COLINMDBCF', 98)
# ...
# (',user=colinpaice,appltag=fromQMAJMS', 52)
# (',user=colinpaice,appltag=runmqchi', 1)
# (',user=colinpaice,appltag=runmqsc', 1)

#
# The code for pid has been commented out, as with clients this is just an MQ
# program.  So this is not very useful

from sys import stdin
data=dict();
q=""; # queue name
u=""; # userid
a=""; # appl tag
p=""; # pid 
input = "";
# we write out the data after we have processed the first record 
doneFirst = False;
# get rid of stuff at the front until first AMS message
for line in stdin:  
  if line.startswith("AMQ"): break;

# read the file until we hit the end.  The end has 
# One MQSC command read.
# No commands have a syntax error.
# All valid MQSC commands were processed.
# So stop when we have All.
# This has been tested on python 3.6
#

for line in stdin:
  # AMQ at the beginning of the line means we have a new definition, so 
  # process the previous one
  if ( line.startswith("AMQ") & doneFirst == True) | line.startswith("All"):
     # split it into words like "INPUT(NO)" as a word
     x= input.split(" ")   
     for i in x:
        if i.startswith("USERID("):
          u=",user="+i.replace('(',' ').replace(')',' ').split()[1] ;
        if i.startswith("QUEUE("):
          q=",q="+ i.replace('(',' ').replace(')',' ').split()[1] ;
        if i.startswith("APPLTAG("):
          a=",appltag="+i.replace('(',' ').replace(')',' ').split()[1] ;
     # if i.startswith("PID"):
     # p=",pid="+i.replace('(',' ').replace(')',' ').split()[1] ;
     # 
     #  We have parsed the entities data, now accumulate it in a dictionary
     key = q + u + p + a;
     # if it exists increment it
     # else add it
     if (key in data):
        data[key]+=1;          
     else: 
       data[key]=1;
     # reset the variables
     q="";
     u="";
     a="";
     p="";
     input="";
  # otherwise just add line to end of current buffer
  else: input = input + line
  if line.startswith("All") :break; # end of data 
  if ( line.startswith("AMQ")): doneFirst = True;
#  We have got to the end of the input

# sort it by queue etc
sortedData = sorted(data)
# and print it out
for item in sortedData:
   print(item, data[item]);


