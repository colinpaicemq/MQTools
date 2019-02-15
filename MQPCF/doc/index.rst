MQPCF
=====
.. toctree::
   :maxdepth: 2
   :caption: Contents:

Introduction
============


MQ PCF processor
===============

MQ PCF is a set of Python modules for processing MQ PCF data, and creating
IBM MQ PCF requests.
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

You would normally use this code with PyMQI.

PyMQI is a production-ready Python extension for IBM's messaging &  queuing middleware,
IBM MQ (formerly know as WebSphere MQ and MQSeries). This allows Python programs to make
calls to connect to queue managers, send messages to, get messages off queues
and issue administrative calls, e.g. to create channels or change queues definitions.


How do you use it
=================

Processing PCF messages in queues.
_________________________________

Setup

    import MQPCFGET as MQPCFGET
    pcfget = MQPCFGET.MQPCFGET()

use PyMQI to get a message from the queue 

    data = hReply.get(None,md, gmo )

process it

    header, data =pcfget.parseData(buffer=data,strip="yes",debug="no")

    print("Header:", header)
    print("Data:", data)

and that's it!
The internal decimal value have been mapped to words, so the data with internal 
value 3501 is mapped to its constant MQCACH_CHANNEL_NAME, and the prefix
if removed to give "CHANNEL_NAME".

Where possible it maps internal values to strings, so 
'CHECK_CLIENT_BINDING' with value of 4, is mapped from MQCHK_AS_Q_MGR =4, 
and the prefix is removed to give AS_Q_MGR and so the result is
   'CHECK_CLIENT_BINDING': 'AS_Q_MGR' 


Creating PCF messages
___________________

Setup

  import MQPCFSET as  MQPCFSET
  pcfset = MQPCFSET.MQPCFSET()

create the message


  message=pcfset.request( "INQUIRE_CHLAUTH_RECS" 
                          ,{"CHANNEL_NAME":"*"}                 
                        )
or
  message=pcfset.request("INQUIRE_Q_STATUS"
                        ,{"Q_NAME":"AMQ*"}
                        ,{"CURRENT_Q_DEPTH":("GT",0)}
                        ,{"OPEN_TYPE":"INPUT"}                  
                      )

process it using PyMQI to put the message to SYSTEM.ADMIN.COMMAND.QUEUE.  
Of course you need to specify the ReplyToQueue


hAdmin.put(message, md)

then use MQPCF to process the returned message.




