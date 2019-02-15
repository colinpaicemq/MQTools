# MQTools
A repository of useful bits of code.

1.MQ PCF Processor

2.appltag. This summarises the output of the dis qstatus(queue*) type(handle) and 
give a count of unique queue,  userid, applytag.


MQ PCF processor
===============

This code allows you to process a message in PCF format. 

Processing PCF data into a dict
_______________________________

It returns a list of dict with the data from
the different structures, and with internal numbers converted to strings 
where applicable.

You use pymqi to get a message, then you can use this code to process it.

The output would be

Header
_____
{'Type': 'COMMAND', 
  'StrucLength': 36, 
  'Version': 1, 'Command': 
  'INQUIRE_CHLAUTH_RECS', 
  'MsgSeqNumber': 1, 
  'Control': 'LAST', 
  'CompCode': 0, 
  'Reason': 0,
  'ParameterCount': 1, 
  'sReason': 'NONE'
}

Data
____
{'CHANNEL_NAME': 'SYSTEM.ADMIN.SVRCONN',
 'CHLAUTH_TYPE': 'ADDRESSMAP',
 'CHLAUTH_DESC': 'Default rule to allow MQ Explorer access',
 'CUSTOM': '', 
 'CONNECTION_NAME': '*',
 'USER_SOURCE': 'CHANNEL',
 'CHECK_CLIENT_BINDING': 'AS_Q_MGR',
 'ALTERATION_DATE': '2018-08-16',
 'ALTERATION_TIME': '13.32.16'
}

This can process messages on from queues such as 
SYSTEM.ADMIN.*.QUEUE and SYSTEM.ADMIN.*.EVENT



Issuing PCF commands
You can create a PCF message and then use pymqi to put it to the 
SYSTEM.ADMIN.COMMAND.QUEUE

message=pcfset.request(  "INQUIRE_CHLAUTH_RECS" 
                        ,{"CHANNEL_NAME":"*"}                 
                      )
or
message=pcfset.request("INQUIRE_Q_STATUS"
                       ,{"Q_NAME":"AMQ*"}
                       ,{"CURRENT_Q_DEPTH":("EQ",0)}
                       ,{"OPEN_TYPE":"INPUT"}                  
                      )


appltag 
=======
Use this python script to process the output from runmqsc DIS QSTATUS(queue) 
to summarise the userids and appltags using the queue.

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


The code for processid id (pid) has been commented out, as with 
clients this is just an MQ
program. This is not very useful


