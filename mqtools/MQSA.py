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
# ./samp/bin/amqsevt -m QMA -b -q SYSTEM.ADMIN.STATISTICS.QUEUE -o  -json -w 1
#                     |python3 MQSA.py 
"""
MQSA : Format MQ Stats and accounting data in json format into
csv file

Take the oytput from
MQ program amqsevt takes data from a queue and formats it as json
Pass this into this MQSA routine
./samp/bin/amqsevt -m QMA -b -q SYSTEM.ADMIN.STATISTICS.QUEUE
                   -o json -w 1 |jq | python3 MQSA.py
to create .csv files
"""

import sys
import json
from datetime import datetime
import platform
import os
import csv

TYPE_STATISTICS_MQI = 164
TYPE_STATISTICS_QUEUE = 165
TYPE_STATISTICS_CHANNEL = 166
TYPE_ACCOUNTING_MQI = 167
TYPE_ACCOUNTING_QUEUE = 168

# We need to use eprint because print will go to json output
# and non json will confuse json parser
def eprint(*args, **kwargs):
    """ eprint - print to stderr """
    print(*args, file=sys.stderr, **kwargs)


def sum_mq(row, element):
    """ if data is an array of integers - add them and replace the
        element with the sum

        sum a  list of values for example
        opens" : [0,178,4,0,0,10,0,3,45,0,0,0,0]
        check to see if the data is a list, and the content is numeric
        if so add up up, and replace the element
        else make no changes
    """
    if element not in row:
        eprint("sum_mq element not found in the row", element)
        return
    count = row[element]
    if str(type(count)) != "<class 'list'>": # it is a single element
        return
    # elements of [] should all be integers... so report any than are not
    # and return
    if  str(type(row[element][0])) != "<class 'int'>":
        eprint("data element of ", element, " are not integers")
        return
    total = 0
    for i in row[element]:
        #  print("Infor",i)
        total += i
    # print ("replace element ", element, " with ", sum)
    row[element] = total

def MQI_Statistics(j):
    """ process the MQI statistics """
    fields = ["startDate",
              "startDateTime",
              "startTime",
              "ec.timeStamp",
              "endDate",
              "endtDateTime",
              "endTime", 
              "queueMgrName",              
              "es.objectName",
              "es.objectType",
              "puts",
              "put1s",
              "topicPuts",
              "topicPuts",
              "putBytes",
              "topicPutBytes",
              "getBytes",
              "gets",
              "opens",
              "commits",
              "backouts",
              "conns",
              "browseBytes",
              "browses",
              "browsesFailed",
              "cbs",
              "cbsFailed",
              "closes",
              "closesFailed",
              "commandLevel", 
              "commitsFailed", 
              "connsFailed",
              "connsMax",
              "ctls",
              "ctlsFailed",
              "discs",
              "ec.epoch",
              "er.name",
              "er.value",
              "et.name",
              "et.value",
              "getsFailed",
              "inqs",
              "inqsFailed",
              "interval",
              "msgsExpired",
              "msgsPurged",
              "opensFailed",
              "publishMsgBytes",
              "publishMsgCount", 
              "put1sFailed",
              "putsFailed",
              "sets",
              "setsFailed",
              "stats",
              "statsFailed",
              "subDurHighwater",
              "subDurLowwater",
              "subNdurHighwater",
              "subNdurLowwater",
              "subrqs",
              "subrqsFailed",
              "subsDur",
              "subsFailed",
              "subsNdur",
              "topicPut1sFailed", 
              "topicPutsFailed",
              "unsubsDur",
              "unsubsFailed",
              "unsubsNdur",
        ]
    jkeys = list(j.keys())
    for each_key in jkeys:
        sum_mq(j, each_key)
    mqi_s.write(j,fields)

    def Channel_Statistics(j):
        fields = [
                  "queueMgrName",
                  "channelName",
                  "channelType",                  
                  "startDate",
                  "startDateTime",
                  "startTime",                  
                  "endDate",
                  "endtDateTime",
                  "endTime",
                  "interval", 
                  "fullBatches",
                  "incompleteBatches",
                  "msgs",
                  "avgBatchSize",
                  "bytes",
                  "commandLevel",
                  "connectionName",
                  "ec.epoch",
                  "ec.timeStamp",
                  "er.name",
                  "er.value",
                  "es.objectName",
                  "es.objectType",
                  "et.name",
                  "et.value",
                  "netTimeAvg",
                  "netTimeMax",
                  "netTimeMin",
                  "objectCount",
                  "putRetries",
                  "remoteQueueMgrName",

            ]
    """ process the Channel statistics """
    channel_data = j['chlStatisticsData']  # a set of queue data
    # remove the array of channel data, then
    # process the array elements one at a time
    # and write it out, one queue record at a time
    del  j['chlStatisticsData']
    common = j # save this for reuse
    for channel in channel_data:
        temp = j
        temp.update(channel) # merge the data
        jkeys = list(temp.keys())
        for each_key in jkeys:
            sum_mq(temp, each_key)
        channel_s.write(temp,fields)


def MQI_Accounting(j):
    """ process the MQI accounting """
    fields =[
             "queueMgrName",
             "userIdentifier",
             "applName",
             "channelName", 
             "es.objectName",
             "es.objectType",                         
             "startDate",
             "startDateTime",
             "startTime",             
             "endDate",
             "endtDateTime",
             "endTime",           
             "interval",
             "putsTotal"
             "putBytesTotal"
             "getBytes",
             "gets",
             "commits",
             "backouts",
             "browseBytes",
             "browses",
             "browsesFailed",
             "cbs",
             "cbsFailed",
             "closes",
             "closesFailed",
             "commandLevel",
             "commitsFailed",
             "connDate",
             "connectionId",
             "connectionName",
             "connTime",
             "ctls",
             "ctlsFailed",
             "discDate",
             "discTime",
             "discType",
             "ec.epoch",
             "ec.timeStamp",
             "er.name",
             "er.value",

             "et.name",
             "et.value",
             "getsFailed",
             "inqs",
             "inqsFailed",
             "opens",
             "opensFailed",
             "processId",
             "puts", 
             "put1s",
             "topicPutBytes",
             "putBytes",
             "topicPuts",
             "topicPut1s",                       
             "put1sFailed", 
             "putsFailed",
             "sequenceNumber",
             "sets",
             "setsFailed",
             "stats",
             "statsFailed",
             "subrqs",
             "subrqsFailed",
             "subsDur",
             "subsFailed",
             "subsNdur",
             "threadId",
             "topicPut1sFailed",
             "topicPutsFailed",
             "unsubsDur",
             "unsubsFailed",
             "unsubsNdur",

        ]
    jkeys = list(j.keys())
    for each_key in jkeys:
        sum_mq(j, each_key)
    puts_total = 0
    put_names = {"puts", "put1s", "topicPuts", "topicPut1s"}
    for p in put_names:
        if p in j:
            puts_total += j[p]
    j["putsTotal"] = puts_total 
    put_bytes = 0
    putbytes_names = {"putBytes", "topicPutBytes"}
    for p in putbytes_names:
        if p in j:
            puts_bytes += j[p]
    j["putsBytesTotal"] = puts_bytes          
    mqi_a.write(j,fields)

def Queue_Accounting(j):
    """ Queue accounting """
    fields = [
               "queueMgrName",
               "queueName",        
               "startDate",
               "startDateTime",
               "startTime",               
               "endDate",
               "endtDateTime",
               "endTime",
               "applName",
               "putsTotal",
               "puts",
               "put1s",
               "putBytes",               
               "gets",
               "queueTimeAvg",                              
               "browseBytes",
               "browseMaxBytes",
               "browseMinBytes",
               "browses",
               "browsesFailed",
               "closeDate",
               "closes",
               "closeTime",
               "commandLevel",
               "connectionId",
               "creationDate",
               "creationTime",
               "definitionType",
               "ec.epoch",
               "ec.timeStamp",
               "er.name",
               "er.value",
               "es.objectName",
               "es.objectType",
               "et.name",
               "et.value",
               "generatedMsgs",
               "getBytes",
               "getMaxBytes",
               "getMinBytes",

               "getsFailed",
               "interval",
               "objectCount",
               "openDate",
               "opens",
               "openTime",
               "processId",
               "put1sFailed",
               "putMaxBytes",
               "putMinBytes",
               "putsFailed",
               "queueTimeMax",
               "queueTimeMin",
               "queueType",
               "sequenceNumber",
               "threadId",
               "userIdentifier",        
        ]
    queue_data = j['queueAccountingData']  # a set of queue data
    nonPersistent = 0
    Persistent = 1
    # remove the array of queue data, then
    # process the array elements one at a time
    # and write it out, one queue record at a time
    del  j['queueAccountingData']
    common = j # save this for reuse

    # to accumulate the data for P and NP we have to do some calculations to get a
    # combined figure
    for queue in queue_data:
        j = common
        # some values are not always present so need to check these
        if "queueTimeMin" in queue:
            # queue time min of 0 could be there were no gets! so we have to exclude these
            if queue["gets"][nonPersistent] > 0:
                if queue["gets"][Persistent] > 0:
                    queue["queueTimeMin"] = min(queue["queueTimeMin"][nonPersistent],
                                                queue["queueTimeMin"][Persistent]
                                               )
                else: # we only had  non persistent
                    queue["queueTimeMin"] = queue["queueTimeMin"][nonPersistent]  # gets[Persistent] = 0
            else: # we had no non persistent so check Persistent
                    queue["queueTimeMin"] = queue["queueTimeMin"][Persistent]  # gets[nonPersistent] = 0
    
            # queueTimeAvg
            get_count = queue["gets"][nonPersistent] + queue["gets"][Persistent]
    
            if get_count == 0:
                queue["queueTimeAvg"] = 0
            else:
                queue["queueTimeAvg"] = (queue["queueTimeAvg"][nonPersistent] * 
                                         queue["gets"][nonPersistent] +
                                         queue["queueTimeAvg"][Persistent] * 
                                         queue["gets"][Persistent]
                                        ) /get_count
            queue["queueTimeMax"] = max(queue["queueTimeMax"][nonPersistent],
                                                queue["queueTimeMax"][Persistent]
                                               )                                        
                                        
        j.update(queue)
        jkeys = list(j.keys())
        for each_key in jkeys:
            sum_mq(j, each_key)
        puts_total = 0
        put_names = {"puts","put1s"}
        for p in put_names:
            if p in j:
                 puts_total += j[p]
        j["putsTotal"] = puts_total              
        q_a.write(j,fields)
      
def Queue_Statistics(j):
    """ process queue statistics"""
    fields = [
               "queueMgrName",               
               "avgQueueTime",
               "browseBytes",
               "browses",
               "browsesFailed",
               "commandLevel",
               "creationDate",
               "creationTime",
               "definitionType",
               "ec.epoch",
               "ec.timeStamp", 
               "er.name",
               "er.value",
               "es.objectName",
               "es.objectType",
               "et.name",
               "et.value",
               "getBytes",
               "gets",
               "getsFailed",
               "interval",
               "msgsExpired",
               "msgsNotQueued",
               "msgsPurged",
               "objectCount",
               "put1s",
               "put1sFailed",
               "putBytes",
               "puts",
               "putsFailed",
               "queueMaxDepth",
               "queueMinDepth",
               "queueName",
               "queueType",
               "startDate",
               "startDateTime",
               "startTime",
               ]
    queue_statistics_data = j['queueStatisticsData']
    del  j['queueStatisticsData']
    for queue in queue_statistics_data:
        temp = j
        temp.update(queue)
        #j['queue']=queue
        jkeys = list(temp.keys())
        for each_key in jkeys:
            sum_mq(temp, each_key)
        q_s.write(temp,fields)


def flatten(level, short):
    """ make 2nd level items into top level items by adding a prefix to them """
    if not level in json_data:
        return
    element = json_data[level]
    del json_data[level]
    for jkeys in list(element.keys()):
        if short == "":
            json_data[jkeys] = element[jkeys]
        else:
            json_data[short + "." +jkeys] = element[jkeys]


class write_csv:
    def __init__(self, data_type):
        self.file = None
        self.csv = None
        self.last_date = None
        self.data_type = data_type
        self.record_data = None
        self.file_name = None
    def write(self, data,fields):
        # is this record for the current file?
        # print("write",data)
        #kk = data.keys()
        #for k in kk:    
        #    s=    '"' +k + '",'
        #    print(self.data_type,s)
        if self.record_data != record_date:
            if self.file is not None:
                self.file.close()
                self.file = None
                self.file_name = None
                self.csv = None

            if self.file is None:
                fn = {"yyyy":yyyy,
                      "mm":mm,
                      "dd":dd,
                      "qmgr":qmgr,
                      "recordType":self.data_type}
                self.file_name = filename_format.format(**fn)
                file_exists = os.path.exists(self.file_name)
                self.file = open(self.file_name, "a", newline="")
                self.csv = csv.writer(self.file)
                self.csv = csv.DictWriter(self.file,fieldnames=fields)
                if not file_exists: # write the header
                   #print("==headerdata==", data.keys())
                   # header = (list(data['eventSource'].keys())+
                   #          list(data['eventType'].keys())+
                   #          list(data['eventData'].keys())
                   #          )
                    self.csv.writeheader()  # header row
                    

        #data['eventData']['startTime'] = data['eventData']['startTime'].replace('.', ':')
        #data['eventData']['endTime'] = data['eventData']['endTime'].replace('.', ':')
        #data_row = (list(data['eventSource'].values())+
        #       list(data['eventType'].values())+
        #       list( data['eventData'].values())
        #      )
        self.csv.writerow(data)  # header row



python_level = platform.python_version()
if python_level < '3.6.0':
    print("The prereq level of python is 3.6.0.  Your level is", python_level)
    sys.exit(0)

#  data like  = {"type":"MQI_Q","qm":"QMA","yy":2019, "mm":2 ,"dd":1  }

filename_format = '{recordType}_{qmgr}_{yyyy:04d}_{mm:02d}_{dd:02d}.csv'

mqi_s = write_csv("mqi_s")
mqi_a = write_csv("mqi_a")
q_s = write_csv("q_s")
channel_s = write_csv("channel_s")
q_a = write_csv("q_a")

report_count = 0
while True:
    line = sys.stdin.readline()
    if not line: 
        break
    report_count += 1
    if report_count %1000 == 0:
        eprint("Messages processes so far", report_count)
    try:
        json_data = json.loads(line)
    except:
        print("Unexpected error parsing json:", sys.exc_info()[0])
        print("line was:", line, ".")
        raise
    # flatten and rename so
    # "eventSource" : { "objectName": "SYSTEM.ADMIN.STATISTICS.QUEUE",
    #                "objectType" : "Queue" },
    # becomes "es.objectName", and "es.objectType"
    # etc
    flatten("eventSource", "es")
    flatten("eventReason", "er")
    flatten("eventCreation", "ec")

    # flatten and rename with null HLQ
    # so "eventData" : {
    #  "queueMgrName" : "QMA"}
    # becomes "queueMgrName"
    flatten("eventData", "")
    flatten("eventType", "et")
    if 'startDate' in json_data:
        # build combined date + time - then parse it to create a datetime object
        startDateTime = datetime.strptime(json_data['startDate'] +
                                          "/"+
                                          json_data['startTime'], "%Y-%m-%d/%H.%M.%S")
        endDateTime = datetime.strptime(json_data['endDate'] +
                                        "/" +
                                        json_data['endTime'], "%Y-%m-%d/%H.%M.%S"
                                       )
        # calculate the interface duration in seconds
        interval = (endDateTime -startDateTime).total_seconds()

        json_data['startDateTime'] = startDateTime.isoformat('T')
        json_data['endtDateTime'] = startDateTime.isoformat('T')
        json_data['interval'] = interval
        record_date = endDateTime.date()
        # these are available for us in the output file name 
        yyyy = record_date.year
        mm = record_date.month
        dd = record_date.day

    else:
        print("startDate not found",json_data)
        record_data = None

    qmgr = json_data["queueMgrName"] # used in the output file name    
    eventValue = json_data['et.value']

    if eventValue == TYPE_STATISTICS_QUEUE:
        Queue_Statistics(json_data)

    elif eventValue == TYPE_STATISTICS_MQI:
        MQI_Statistics(json_data)
    
    elif eventValue == TYPE_STATISTICS_CHANNEL:
        Channel_Statistics(json_data)

    elif eventValue == TYPE_ACCOUNTING_MQI:
        MQI_Accounting(json_data)

    elif eventValue == TYPE_ACCOUNTING_QUEUE:
        Queue_Accounting(json_data)
    else:
        print("Unknown data record of type", eventValue)
        exit(8)
    #o = json.dumps(json_data)
    #  e.eprint("before print",json_data)
    #print(o,flush=True)
    ##  e.eprint("after print",o)
