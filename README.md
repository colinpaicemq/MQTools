# MQTools
A repository of useful bits of code.

1.appltag. This summarises the output of the dis qstatus(queue*) type(handle) and give a count of  unique
queue,  userid, applytag  


appltag 
=======
Use this python script to process the output from runmqsc DIS QSTATUS(queue) to summarise
the userids and appltags using the queue.
For example on Linux  
echo "dis QSTATUS(CP000\*) type(handle) all" |runmqsc QMA |python appltag.py  
produces  
    *(',q=CP0000,user=colinpaice,appltag=fromQMAJMS', 43)*  
    *(',q=CP0000,user=colinpaice,appltag=oemput', 1)*  
    *(',q=CP0002,user=colinpaice,appltag=COLINMDBCF', 36)*  
    *(',q=CP0002,user=colinpaice,appltag=oemput', 1)*  

echo "dis conn(\*) all  "|runmqsc QMA |python appltag.py   
produces  
    *(',user=colinpaice,appltag=COLINMDBCF', 98)*  
    *...*  
    *(',user=colinpaice,appltag=fromQMAJMS', 52)*  
    *(',user=colinpaice,appltag=runmqchi', 1)*  
    *(',user=colinpaice,appltag=runmqsc', 1)*  


The code for processid id (pid) has been commented out, as with clients this is just an MQ
program. This is not very useful


