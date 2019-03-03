"""
 Python MQ PCF processing.   This module takes data from IBM MQ PCF
 messages, and converts it into Python Dict with constants changed
 to English terms where possibl
 Author: Colin Paice(colinpaiceMQ@gmail.com)


 DISCLAIMER
 You are free to use this code in any way you like, subject to the
 Python & IBM disclaimers & copyrights. I make no representations
 about the suitability of this software for any purpose. It is
 provided "AS-IS" without warranty of any kind, either express or
 implied.
"""

import struct
import string
import pymqi as pymqi
from . import smqpcf as SMQPCF
from . import mqpcf  as mqpcf
from sys import stderr


class mqpcfget(object):
    """PCF(**kw)
    Take an IBM MQ PCF string and convert the different structures within
    it to be a list of Python dicts
    It can be printed as json and so processed by baby script
    """
#delete
    """
    not used?

    def _parse_data_type(self, k):
        #  Process the command
        if self.debug > 0 :
            print("_parse_data_type", k)
        if isinstance(k, str):
            print("K=", k)
            data_type, key_value = SMQPCF.selectTypeS.get(k)
   #      else:  raise ValueError("MQPCF parameters in wrong format. ",k, v )
            if key_value is None:
                raise ValueError("MQPCF parameters not found: ", k)
        if self.debug > 0 :
            print("input is", k, "type is", data_type, " key is ", key_value)
        return data_type, key_value
        # we have a valid data type
        #      print("command is instance list...", isinstance(v,list))
    """

    def __init__(self,debug=0):
        ## super(MQPCF.MQPCF, self).__init__()
        self.trace = 0
        self.strip = "no"
        self.debug = debug
        self.all_data = []
        self.data_offset = 0
        self.structure_offset = 0
        self.buffer = b""
        self.buffer_length = 0
        self.structure_length = 0

    def _parse_data(self, buffer='', strip="no", debug=0):
        """
        Parse the data into the a dictionary of component

        For example with INQUIRE_Q there will be sections on Q_NAME
        """
        self.buffer = buffer
        self.strip = strip
        self.debug = debug
        self.data_offset = 0
        self.structure_offset = 0
        self.all_data = [] # reset it
        self.buffer_length = len(buffer)
        if len(buffer) < 36:
            raise ValueError("The buffer is too small,"
                             " the size should be >= 36: "
                             , len(buffer))
        header = self._parse_header()
        # dont print this out as reason - 2635 means change event!
        #if header['Reason'] != 0:
        #    print("Return code from request:", header['Reason'])
    #      return header, ''
        if header["ParameterCount"] == 0:
            return header, ""
        data = self._parse_detail(offset=self.data_offset, count=header["ParameterCount"])
        return header, data

    def _parse_header(self):
        """
        _parse_header

        Process the header section and return a dictionary with the values.
        """
        # The data is returned into this any values are overwritten
        header_opts = [["Type", pymqi.CMQCFC.MQCFT_COMMAND, pymqi.MQLONG_TYPE],
                       ['StrucLength', pymqi.CMQCFC.MQCFH_STRUC_LENGTH, pymqi.MQLONG_TYPE],
                       ['Version', pymqi.CMQCFC.MQCFH_VERSION_1, pymqi.MQLONG_TYPE],
                       ['Command', pymqi.CMQCFC.MQCMD_NONE, pymqi.MQLONG_TYPE],
                       ['MsgSeqNumber', 1, pymqi.MQLONG_TYPE],
                       ['Control', pymqi.CMQCFC.MQCFC_LAST, pymqi.MQLONG_TYPE],
                       ['CompCode', pymqi.CMQC.MQCC_OK, pymqi.MQLONG_TYPE],
                       ['Reason', pymqi.CMQC.MQRC_NONE, pymqi.MQLONG_TYPE],
                       ["ParameterCount", 0, pymqi.MQLONG_TYPE]
                      ]
       
        header = self._unpack(tuple(header_opts)) # build the structure from the data
        if self.debug > 1:
            print("Header:type", header["Type"],
                  "Command:", header["Command"],
                  "Reason:", header["Reason"]) 
        # Convert the integer values to text values
        header["Type"] = SMQPCF.sMQLOOKUP.get(("MQCFT", header["Type"]), header["Type"])
        header["Command"] = SMQPCF.sMQLOOKUP.get(("MQCMD", header["Command"]), header["Command"])
        #-1 is special code for MQCMDS
        header["Control"] = SMQPCF.sMQLOOKUP.get(("MQCFC", header["Control"]), header["Control"])
        #-2 is special code for Control
        header["CompCode"] = mqpcf.lookup_reason(header["CompCode"])
        header["sReason"] = SMQPCF.sMQLOOKUP.get(("MQRC", header["Reason"]), header["Reason"])
        self.structure_length = header['StrucLength']
#        print("Header:", header)
        self._move_to_next_structure()
        return header

    def _parse_detail(self, offset, count):
        """
        process each section and extract the data from the fields

        Each section of PCF has fields
           Type
           StrucLength = length of head and it data
           Parameter
           and none or more of
           CodedCharSetId
           Count
           string_length
           data
           or data,data...

        In this section the self.structure_offset is the start of the section in the buffer.
        At the end of the section processing we add the Structlength
        to get the position of the next section
        data_offset is used when moving though fields within a section
        """
        self.data_offset = offset
        self.structure_offset = offset
        i = 0
        returned = {}
        while i < count:   # passed count
            section_type = self._get4()
            self.structure_length = self._get4()
            if self.debug > 5 :
                print("mqpcfget dump 153: length:",self.structure_length,
                      "offset:",self.structure_offset,
                      file=stderr)
                print(self.buffer[self.structure_offset:self.structure_offset+16].hex(),file=stderr)
                print(self.buffer[self.structure_offset+16:self.structure_offset+32].hex(),file=stderr)
                print(self.buffer[self.structure_offset+32:self.structure_offset+48].hex(),file=stderr)
                print(self.buffer[self.structure_offset+48:self.structure_offset+64].hex(),file=stderr)
            if self.debug > 2 :
                print("mqpcfget: type:", section_type,"length:", self.structure_length,
                      "offset:", self.structure_offset,
                      "buffer length:", self.buffer_length,
                      file=stderr)
            if self.structure_offset + self.structure_length > self.buffer_length:
                raise ValueError("MQPCF buffer too short: Structure length",self.structure_length)
            if section_type == pymqi.CMQCFC.MQCFT_STRING:
                data, value, longdata = self._get_string()
            elif section_type == pymqi.CMQCFC.MQCFT_STRING_LIST:
                data, value, longdata = self._get_string_list()
            elif section_type == pymqi.CMQCFC.MQCFT_INTEGER:
                data, value, longdata = self._get_integer()
            elif section_type == pymqi.CMQCFC.MQCFT_INTEGER_LIST:
                data, value, longdata = self._get_integer_list()
            elif section_type == pymqi.CMQCFC.MQCFT_INTEGER_FILTER:
                data, value, longdata = self._get_integer_filter()
            elif section_type == pymqi.CMQCFC.MQCFT_GROUP:
                data, value, longdata = self._get_group()
            elif section_type == pymqi.CMQCFC.MQCFT_INTEGER64_LIST:
                data, value, longdata = self._get_integer_64_list()
            elif section_type == pymqi.CMQCFC.MQCFT_INTEGER64:
                data, value, longdata = self._get_integer_64()
            elif section_type == pymqi.CMQCFC.MQCFT_BYTE_STRING:
                data, value, longdata = self._get_byte_string()
            elif section_type == pymqi.CMQCFC.MQCFT_BYTE_STRING_FILTER:
                data, value, longdata = self._get_byte_string_filter()
            elif section_type == pymqi.CMQCFC.MQCFT_STRING_FILTER:
                data, value, longdata = self._get_string_filter()
            else:
                raise ValueError("MQPCF Unsupported parameter:"
                                 , section_type)
            if self.debug > 0 :
                print("element:", i, data,"value:",value)
            #  MQPCF.eprint("___Type",section_type,data,value)
            #    elif section_type == pymqi.CMQCFC.MQCFT_GROUP:
            #    data, value, longdata = self._get_group()
            # elif section_type == pymqi.CMQCFC.MQCFT_INTEGER6
            returned[data] = value
            self.all_data.append(longdata)
            if self.debug > 5 :
                print(">>mqpcfget: 202 moveto type:", section_type,"length:", self.structure_length,
                      "offset:", self.structure_offset,
                      "buffer length:", self.buffer_length,
                      file=stderr)
            # need to be careful not to move ahead twice from the end of group.
            # the field within it moved to the next structure, so if group do not 
            # move on    
            if not section_type == pymqi.CMQCFC.MQCFT_GROUP:    
                self._move_to_next_structure()
            i = i+1
        return returned

    def _get_group(self):
        #          ["Type",pymqi.CMQCFC.MQCFT_INTEGER,pymqi.MQLONG_TYPE],
        #          ['StrucLength',0,pymqi.MQLONG_TYPE],
        #          ["Parameter",  0,pymqi.MQLONG_TYPE],
        #          ["ParameterCount", 0,pymqi.MQLONG_TYPE],
        #          [data...]

        parameter = self._get4()
        parameter_count = self._get4()
        # a group is a section of common records so we call the parser recursively   
        #print("==GROUP",parameter,parameter_count)
        group_data = self._parse_detail(offset=self.data_offset, count=parameter_count)
        key = SMQPCF.sMQLOOKUP.get(("MQGA", parameter), parameter)
        if self.debug > 5 :
            print("_get_group",key)
        data = {"Type":"MQCFT_Group",
                "Parameter":parameter,
                "ParameterCount":parameter_count,
                "Value":group_data}
        value = group_data
        return key, value, data

    def _get_string(self):
        parameter = self._get4()
        CCSID = self._get4()
        string_length = self._get4()
        value = self.buffer[self.data_offset:self.data_offset + string_length].decode()
        if self.strip != "no":
            value = value.rstrip(' \0')
        key = SMQPCF.sMQLOOKUP.get(("MQCA", parameter), parameter)
        # key = self._lookup_value("MQCFT_STRING", parameter)
        data = {"Value":value,
                "Parameter":key,
                "Type":"MQCFT_STRING",
                "string_length":string_length}
        if self.debug > 0 :
            print("==String data:", data)
        return key, value, data

    def _get_string_filter(self):  # save as string but with no conversion
        #  typedef struct tagMQCFSF {
        #  MQLONG  Type;               /* Structure type */
        #  MQLONG  StrucLength;        /* Structure length */
        #  MQLONG  Parameter;          /* Parameter identifier */
        #  MQLONG  Operator;           /* Operator identifier */
        #  MQLONG  CCSID
        #  MQLONG  FilterValueLength;  /* Filter value length */
        #  MQBYTE  FilterValue[1];     /* Filter value -- first byte */
        # } MQCFBF;
        parameter = self._get4()
        operator = self._get4()
        CCSID = self._get4()
        string_length = self._get4()
        operator = SMQPCF.sMQLOOKUP.get(("MQCFOP", operator), operator)
        value = self.buffer[self.data_offset:self.data_offset + string_length].decode()
        if self.strip != "no":
            value = value.rstrip(' \0')
        key = SMQPCF.sMQLOOKUP.get(("MQCA", parameter), parameter)
        if self.debug > 5 :
            print("_get_string_filter",key)
        data = {"Operator":operator,
                "Type":"MQCFT_STRING_FILTER",
                "Parameter":key,
                "Value":value}
        return key, (operator, value), data

    def _get_string_list(self):
        parameter = self._get4()
        CCSID = self._get4()
        count = self._get4()
        string_length = self._get4()
        slist = []
        # iterate along the buffer cutting out the data
        for i in range(count):
            sdata = self.buffer[self.data_offset:self.data_offset + string_length].decode()
            if self.strip != "no":
                sdata = sdata.rstrip(' \0')
            slist.append(sdata)
            self.data_offset = self.data_offset+string_length
        key = SMQPCF.sMQLOOKUP.get(("MQCA", parameter), parameter)
        if self.debug > 5 :
            print("_get_string_list",key)
        value = slist
        data = {"Type":"MQCFT_STRING",
                "Parameter":key,
                "Value":slist,
                "CodedCharSetId":CCSID,
                "Count":count,
                "string_length":string_length}
        return key, value, data

    def _get_byte_string(self):  # save as string but with no conversion
        parameter = self._get4()
        string_length = self._get4()
        value = self.buffer[self.data_offset:self.data_offset+string_length]
        # if it is printable then covert to string else convert to 0x.... format
        # so json can process it etc
        printable_chars = set(bytes(string.printable, 'ascii'))
        ba_value = bytearray(value)
            # check to see if the whole string is printable 
        printable = all(char in printable_chars for char in ba_value)
        
        if printable == True:
                value  =value.decode() # convert to string
                if strip != "no":
                    value = value.rstrip(' \0')     
        else:
            value = "0x"+value.hex() # convert it to hex
        
        
        key = SMQPCF.sMQLOOKUP.get(("MQBA", parameter), parameter)
        if self.debug > 0 :
            print("==ByteString data:", value,key)
        data = {"Type":"MQCFT_BYTE_STRING",
                "Parameter":key,
                "Value":value}
        return key, value, data

    def _get_byte_string_filter(self):  # save as string but with no conversion
        #  typedef struct tagMQCFBF {
        #     MQLONG  Type;               /* Structure type */
        #     MQLONG  StrucLength;        /* Structure length */
        #     MQLONG  Parameter;          /* Parameter identifier */
        #     MQLONG  Operator;           /* Operator identifier */
        #     MQLONG  FilterValueLength;  /* Filter value length */
        #     MQBYTE  FilterValue[1];     /* Filter value -- first byte */
        # } MQCFBF;
        parameter = self._get4()
        operator = self._get4()
        string_length = self._get4()

        operator = SMQPCF.sMQLOOKUP.get(("MQCFOP", operator), operator)
        value = self.buffer[self.data_offset:self.data_offset + string_length]
        
        # no decode as it is alread  byte string
        if self.debug > 0 :
            print("==ByteString data:", value)
        key = SMQPCF.sMQLOOKUP.get(("MQBA", parameter), parameter)
        data = {"Operator":operator,
                "Type":"MQCFT_BYTE_STRING_FILTER",
                "Parameter":key,
                "Value":value}
        return key, (operator, value), data


    def _get_integer(self):
        """
        get an integer from the Integer Structure
        """
        parameter = self._get4()
        value = self._get4()
        key = SMQPCF.sMQLOOKUP.get(("MQIA", parameter), parameter)
        # decode a value... eg 7 is CLNTCONN for a channel
        old_value = value
        value = _lookup_int_to_string(parameter, value)
        if self.debug > 0 :
            print("==_get_integer parameter:", parameter,
                  "value:",old_value,
                  "key:",key,
                  "new value:",value) 
        data = {"Value":value,
                "Type":"MQCFT_INTEGER",
                "Parameter":key}
        return key, value, data

    def _get_integer_filter(self):
        """
        get an integer from the Integer Structure filter
        """
        parameter = self._get4()
        operator = self._get4()
        value = self._get4()
        operator = SMQPCF.sMQLOOKUP.get(("MQCFOP", operator), operator)
        key = SMQPCF.sMQLOOKUP.get(("MQIA", parameter), parameter)
        # decode a value... eg 7 is CLNTCONN for a channel
        value = _lookup_int_to_string(parameter, value)
        data = {"Value":value,
                'Operator':operator,
                "Type":"MQCFT_INTEGER_FILTER",
                "Parameter":key}
        return key, (operator, value), data


    def _get_integer_list(self):
        """ process the list of integers"""
        parameter = self._get4()
        count = self._get4()
        integer_list = []
        i = 0
        while i < count:   # count
            value = self._get4()
            integer_list.append(value)
            i = i + 1
        key = SMQPCF.sMQLOOKUP.get(("MQIA", parameter), parameter)
        
        value = integer_list
        if self.debug > 0 :
            print("==_get_integer_list parameter:", parameter,                 
                  "key:",key) 
        data = {"Type":"MQCFT_INTEGER_LIST",
                "Parameter":key,
                "Value":value}
        return key, value, data

    def _get_integer_64(self):
        """ process a structure of a 64 bit numbers eg monitoring
        """
        parameter = self._get4()
        value = self._get8()
        key = SMQPCF.sMQLOOKUP.get(("MQIA", parameter), parameter)
        # value = self._lookup_int_to_string(parameter, value) # not for 64 bits
        if self.debug > 0 :
            pass
        print("==_get_integer64 parameter:", parameter,
                  "value:",value,
                  "key:",key,
                 ) 
        if self.debug > 0 :
            print("==_get_integer_64 parameter:", parameter,
                  "key:",key,
                  "new value:",value) 
        data = {"Value":value,
                "Type":"MQCFT_INTEGER64",
                "Parameter":key}
        return key, value, data

    def _get_integer_64_list(self):
        """ process a structure of a list of 64 bit numbers
        """
        parameter = self._get4()
        count = self._get4()
        key = SMQPCF.sMQLOOKUP.get(("MQIA", parameter), parameter)
        integer_list = []
        i = 0
        while i < count:   # count
            value = self._get8()
            integer_list.append(value)
            i = i + 1
        if self.debug > 0 :
            print("==_get_integer_64_list parameter:", parameter,
                  "key:",key)     
        data = {"Type":"MQCFT_INTEGER64_LIST",
                "Parameter":key,
                "Value":integer_list}
        return key, integer_list, data


    def _move_to_next_structure(self):
        """
        move to the next structure in the data

        We have the start of the structure, and its total length
        so move the points to the end of this one- ( and start of the
        next one - if any)
        """
        if self.debug > 5 :
            print("mqpcfget 467: old length:",self.structure_length,
                      "old offset:",self.structure_offset,
                      file=stderr)
            print(self.buffer[self.structure_offset:self.structure_offset+16].hex(),file=stderr)
            print(self.buffer[self.structure_offset+16:self.structure_offset+32].hex(),file=stderr)
            print(self.buffer[self.structure_offset+32:self.structure_offset+48].hex(),file=stderr)
            print(self.buffer[self.structure_offset+48:self.structure_offset+64].hex(),file=stderr)
        self.structure_offset = self.structure_offset + self.structure_length # move to next structure
        self.data_offset = self.structure_offset # reset the start of the data
        return

    def _get4(self):
        """
        Get the next 4 bytes from buffer(offsetData) and move the pointer
        """
        if self.data_offset + 4 > self.buffer_length:
            print("_get4:", self.data_offset, self.buffer_length)
            raise ValueError("MQPCF Trying to get past the end of the buffer")
        longi = struct.unpack('i', self.buffer[self.data_offset:self.data_offset + 4])
        self.data_offset = self.data_offset + 4
        # unpack always returns a tuple - so just get the first one
        return longi[0]

    def _get8(self):
        """
        Get the next 8 bytes from buffer(offsetData) and move the pointer
        """
        if self.data_offset + 8 > self.buffer_length:
            raise ValueError("MQPCF Trying to get past the end of the buffer")
        longlong = struct.unpack('Q', self.buffer[self.data_offset:self.data_offset + 8])
        self.data_offset = self.data_offset + 8
        return longlong[0] # unpack always returns a tuple - so just get the first one

    def _unpack(self, memlist):
        """_unpack(buff)
        Unpack a 'C' structure 'buff' into self."""
        __list = memlist[:]
        __format = ''
        # extract the data type from the passed list and add to the list
        for i in memlist:
            __format = __format + i[2]
        size = struct.calcsize(__format)
        unpacked = struct.unpack(__format, self.buffer[self.data_offset:self.data_offset+size])
        ret_locator = 0
        ret = {}
        for i in __list:
            pymqi.check_not_py3str(unpacked[ret_locator])  # Python 3 bytes check
            ret[i[0]] = unpacked[ret_locator] # the passed name ... gets the value from unpack
            ret_locator = ret_locator + 1
        self.data_offset = self.data_offset + size # point past the list
        return ret


    def getAllData(self):
        """ return the all the parsed data
        """
        return self.all_data


def _lookup_int_to_string(_value_type, value):
    """ 
    convert from number into string eg 0 is GET_DISABLED
    
    We need to find out the prefix of the constants so look up the 
    value_type.   20 maps to "MQQT" in sLookupTypes
    
    We can then look up MQQT and 2 via
    MQQT_MODEL is  2, so so return MODEL
    
    """
    _lookup_key = SMQPCF.sLookupTypes.get(_value_type)
    if _lookup_key is None:
        return value
    _lookup_value = SMQPCF.sMQLOOKUP.get((_lookup_key, value), value)
    return _lookup_value
