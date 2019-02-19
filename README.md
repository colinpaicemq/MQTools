# MQTools
A repository of useful bits of Python code for processing IBM MQ.

These tools covers

* **mqpcf** - MQ PCF Processor  for creating MQ PCF requests,  and a parser to decode the
response and store it in a dict.   This builds on top of pymqi.

* **formatMQMD** for converting a MD from pymqi into a dict with values converted 
to strings

* Examples 
  * **events** - uses mqpcf to read from the events queue and prints the data in json format.
    * **events2** pipe output from _python3 events.py |python3 events2_ produces summary 
      of the events such as 
      ```
       create Q_NAME DQUEUE DQUEUE
       difference Q_NAME DQUEUE DQUEUE Q_DESC  newDesc 
       difference Q_NAME DQUEUE DQUEUE MAX_Q_DEPTH 5000 10
       Delete Q_NAME DQUEUE DQUEUE
       Create Q_NAME D2 D2
       difference Q_NAME D2 D2 MAX_Q_DEPTH 5000 40
       Delete CHANNEL_NAME CH1 CH1
       ```
  * **getqueues** connects to MQ, issues a PCF command to query queues and write
    json output to print
    * **getqueues2** takes the json output and writes it to files in the queues/ directory
    in yaml format  
    * **diff** takes a list of *.yaml files (eg for queues) and compares the options
      so you can see what attributes are different.
      ```
      ./queues/CP0000.yml ./queues/CP0001.yml : Q_NAME CP0000 / CP0001
      ./queues/CP0000.yml ./queues/CP0001.yml : Q_DESC Main queue / 
      ./queues/CP0000.yml ./queues/CP0001.yml : MAX_Q_DEPTH 2000 / 5000
      ./queues/CP0000.yml ./queues/CP0001.yml : Q_DEPTH_HIGH_EVENT ENABLED / DISABLED
      ```
    * **standards** reads the specified *.yaml files and checks the parameters to 
      ensure they meet the specified standards
      ```
      queues/CP00000.yml MAX_MSG_LENGTH 4000 Field in error.  It should be greater than 4194304
      queues/CP00000.yml MAX_Q_DEPTH 5000 Field in error.  It should be greater than 9999
      ```

  * **appltag**. This summarises the output of the dis qstatus(queue*) type(handle) and 
     give a count of unique queue,  userid, applytag.


# MQ PCF processor

This code builds on pymqi  allows you to process a message in PCF format. 

## Processing MQ PCF data into a dict

You use pymqi to get data from an MQ Queue, then mqpcf can parse this data to create a 
dict with the data from
the different structures, and with internal numbers converted to strings 
where applicable.

The output would be

### Header

```
  {'Type': 'COMMAND', 
    'StrucLength': 36, 
    'Version': 1, 
    'Command':'INQUIRE_CHLAUTH_RECS', 
    'MsgSeqNumber': 1, 
    'Control': 'LAST', 
    'CompCode': 0, 
    'Reason': 0,
    'ParameterCount': 1, 
   'sReason': 'NONE'
  }
```
Where the mqpcf code has change the returned the command value of 204 to MQCMD_INQUIRE_CHLAUTH_RECS and 
returned  "INQUIRE_CHLAUTH_RECS"
 
*
### Data

```
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
```
Where the mqpcf code has changed the values returned in the message to "ADDRESSMAP" etc.

This can process messages on from queues such as 
SYSTEM.ADMIN.*.QUEUE and SYSTEM.ADMIN.*.EVENT.  See the code in the examples directory,
these produces json output which you can then pipe into other supplied samples
to do useful things with it.  See above



## Issuing PCF commands
You can create a PCF message and then use pymqi to put it to the 
SYSTEM.ADMIN.COMMAND.QUEUE for example

```
  message=pcfset.request(  "INQUIRE_CHLAUTH_RECS" 
                          ,{"CHANNEL_NAME":"*"}                 
                        )
```
or
```
  message=pcfset.request("INQUIRE_Q_STATUS"
                         ,{"Q_NAME":"AMQ*"}
                         ,{"CURRENT_Q_DEPTH":("EQ",0)}
                         ,{"OPEN_TYPE":"INPUT"}                  
                        )
```

You specify strings instead fo 

appltag 
=======
Use this python script to process the output from runmqsc DIS QSTATUS(queue) 
to summarise the userids and appltags using the queue.

For example on Linux  

echo "dis QSTATUS(CP000\*) type(handle) all" |runmqsc QMA |python appltag.py  

produces
```
    *(',q=CP0000,user=colinpaice,appltag=fromQMAJMS', 43)*  
    *(',q=CP0000,user=colinpaice,appltag=oemput', 1)*  
    *(',q=CP0002,user=colinpaice,appltag=COLINMDBCF', 36)*  
    *(',q=CP0002,user=colinpaice,appltag=oemput', 1)*  
```

echo "dis conn(\*) all  "|runmqsc QMA |python appltag.py   

produces  
```
    *(',user=colinpaice,appltag=COLINMDBCF', 98)*  
    *...*  
    *(',user=colinpaice,appltag=fromQMAJMS', 52)*  
    *(',user=colinpaice,appltag=runmqchi', 1)*  
    *(',user=colinpaice,appltag=runmqsc', 1)*  
```

The code for processid id (pid) has been commented out, as with 
clients this is just an MQ
program. This is not very useful


