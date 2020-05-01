import struct
import pymqi as pymqi
from . import smqpcf as SMQPCF

class mqpcfset(object):
    # class MQPCFSET(MQPCF.MQPCF):

    """PCF()
      Construct a PCFD Structure with default values as per MQI. The
      default values may be overridden by the optional keyword arguments
      'kw'."""

    def __init__(self,debug=0):
        ##   super(MQPCF.MQPCF, self).__init__()
        self.trace = 0
        self.strip = "no"
        self.debug = debug
        self.all_data = []
        self.data_offset = 0
        self.structure_offset = 0
        self.buffer = b""
        self.buffer_length = 0
        self.struc_length = 0
pip3 -v install git+http://github.com/colinpaicemq/MQTools/ 
    def create_request(self, request, *args):
        """
        Process the command and data

        There is a command like "INQUIRE_Q", followed by 0 more
        sections like ("Q_NAME","CP000")
        The input can be a string "INQUIRE_Q" or the numeric value"

        We simplify the logic by assuming every thing is a filter - those
        which are not.. have "eq" added to make it a filter
        We provide a list of names- where the count may be just one element
        """
        if self.debug > 0 :
            print("command", request, args)
        user_command = request
        if not isinstance(request, int):
            # look up and get the integer value for the string
            # it returns  (MQCMD,99)
            if ("MQCMD", request) in SMQPCF.sLookupToI:
                user_command = SMQPCF.sLookupToI.get(("MQCMD", request))# needs tuple
            # user_command = SMQPCF.sMQCMD.get(request) # (MQCMD,number)
            #f user_command is None:
            else:
                raise ValueError("MQPCF command was invalid", request)
            #xvalue returned  is (MQCMD,number)
            # user_command = user_command[1] # select the number from it

        bparms, iparms = self.do_args(args)

        bcommand = struct.pack('iiiiiiiii',
                               pymqi.CMQCFC.MQCFT_COMMAND,
                               pymqi.CMQCFC.MQCFH_STRUC_LENGTH,
                               pymqi.CMQCFC.MQCFH_VERSION_1,
                               user_command,
                               1, # Message sequence number starts with 1
                               pymqi.CMQCFC.MQCFC_LAST,   # Control options
                               0, # Completion code
                               0, # Reason code qualifying completion code
                               iparms  # * Count of parameter structures
                              )
        # create the final string header ||data sections
        bcommand = b''.join([bcommand, bparms])
        return bcommand

    def do_args(self, args):
        """ process the parms data and the parms and count of the parms
        """
        bparms = b''
        iparms = 0
        # args are like {"Q_NAME": "SYSTEM.*" },{'Q_STATUS_TYPE': 'Q_HANDLE'}...
        # so do each section first, then for the (only) key get the value
        for arg in args: # The {"Q_NAME","SYSTEM.*"}
            if isinstance(arg, dict):
                for each_arg in arg: # There should only be one key
                    arg_value = arg.get(each_arg)
                    typeit = "????"
                    if isinstance(each_arg, str): #"Q_NAME"
                        typeit, code = self._parse_data_type(each_arg)
                        # we now have the data type ie MQIA, and number
                    #    print("----64:",typeit,code,each_arg)
                    elif isinstance(each_arg, int):
                        code = each_arg # used the passed in value
                    else:
                        raise ValueError(
                            "MQPCF parameters are in wrong format "
                            "should be 'string' or integer"
                            , arg)
                    if self.debug > 0 :
                        print("mqpcfset typeit arg",arg,"type",typeit,"value",arg_value )    
                    # Pass the type of data (MQIA, the mqcode <for INQUIRE_Q> and value
                    # we can have {QNAME,("EQ","CP*"} - a filter
                    #  or {"QNAME","CP*} - if so treat this as above and insert "EQ"
                    operator = 0
                    if not isinstance(arg_value, tuple):
                        l_data = 0
                    else:
                        l_data = len(arg_value) # get the size of it

                    if l_data == 0:  # not a tuple
                        #operator = pymqi.CMQCFC.MQCFOP_EQUAL #  equals operator
                        pass

                    elif l_data == 1:  # tuple with one data
                        arg_value = arg_value[1] # make extract from the tuple
                    #   operator = pymqi.CMQCFC.MQCFOP_EQUAL #  equals operator
                    elif l_data == 2:  # tuple with two data could be "eq",Value
                        # check to see if it is a valid operator
                        operator = SMQPCF.sLookupToI.get(("MQCFOP", arg_value[0]), 0)
                        if operator > 0: # it was valid
                            arg_value = arg_value[1]# extract the value
                        else: #it was not an operator .. so treat as a tuple of data
                            operator = 0
                    else:  # tuple with many values
                        operator = 0

                    if typeit == "MQIAMO64":
                        val = self.set_integer64(code, operator, arg_value)
                    elif typeit[0:4] == "MQIA": # Integer but integer 64 was caught above
                        val = self.set_integer(code, operator, arg_value, each_arg)
                        # key, operator (0 is none), tuple
                    elif typeit[0:4] == "MQCA": # character (string)
                        val = self.set_string(code, operator, arg_value)
                        # key, operator (0 is none), tuple
                    elif typeit[0:4] == "MQBA": # Byte string
                        val = self.set_byte_string(code, operator, arg_value)
                        # key, operator (0 is none), tuple
                    else:
                        raise ValueError("Unknown data type:", typeit)

                    #  val = self._set_request_data(typeit, mqcode, arg_value)
                    if val is None:
                        raise ValueError("MQPCF command code not found ", each_arg, arg_value)
                    bparms = b''.join([bparms, val])
                    iparms = iparms + 1
            else:
                raise ValueError(        
                    "MQPCF parameters are in wrong format should be"
                    "{ command : data } not {'command','data'}. Data is"
                    , arg, "Check the : in between")
                
        # print("----Type",type(user_command),type(iparms))
        # build the header, ( which includes the number of data sections, so we have to
        # do it after the data sections
        return bparms, iparms

    def _parse_data_type(self, k):
        """ Process the command """
        if self.debug > 0 :
            print("_parse_data_type", k)
        # the dict has  "ACCOUNTING_TOKEN": ("MQBACF",7010),
        # so look for the first word.. ACCOUNTING_TOKEN and return "MQBACF",7010
        if isinstance(k, str):
            if k in SMQPCF.selectTypeS:
                data_type, key_value = SMQPCF.selectTypeS.get(k)
            # else:  raise ValueError("MQPCF parameters in wrong format. ",k, v )
            else:
                raise ValueError("MQPCF parameters not found: ", k)
        if self.debug > 0 :
            print("input is", k, "type is", data_type, " key is ", key_value)
        return data_type, key_value


    def set_string(self, code, operator, value):
        """
        Create the structure to handle strings.

        The data passed in can be
        code,operator=0,   value      for simple string
        code,operator!=0, value      for string filter
        code,opertor= 0, (tuple)      for list of strings
        """

        if operator == 0 and not isinstance(value, tuple):
            attr = value.encode()
            length_attr = len(attr)
            # the length of the structure must be in units of 4
            length_structure = 5 * 4 + length_attr
            new_length_structure = ((length_structure+3)//4)*4 # round it
            delta_length = new_length_structure - length_structure
            returned = struct.pack("iiiii",
                                   pymqi.CMQCFC.MQCFT_STRING,
                                   # Type
                                   new_length_structure,
                                   code,
                                   # What sort eg decimal MQCA_Q_NAME value
                                   pymqi.CMQC.MQCCSI_DEFAULT,
                                   length_attr)# length of string

        elif operator != 0 and not isinstance(value, tuple): # we have a filter
            attr = value.encode()
            length_attr = len(attr)
            # the length of the structure must be in units of 4
            length_structure = 6 * 4 + length_attr
            new_length_structure = ((length_structure+3)//4)*4
            delta_length = new_length_structure - length_structure

            returned = struct.pack("iiiiii",
                                   pymqi.CMQCFC.MQCFT_STRING_FILTER, # Type string filter
                                   new_length_structure, # length of this structure
                                   code,         # What sort eg decimal MQCA_Q_NAME value
                                   operator,     # eg value for eq
                                   pymqi.CMQC.MQCCSI_DEFAULT,
                                   length_attr)          # length of string
        else: # we have a list of strings
            # we need to find the length of the longest string once encoded
            # so build a list of the encoded strings
            # then pad each one to the maximum length
            count = len(value)
            len_encoded = [] # empty list
            for val in value:
                len_encoded.append(val.encode())
            max_length = 0
            for val in len_encoded:
                max_length = max(len(val), max_length)
            attr = b''
            #build up the string of concatenated values, padded to the max length
            for val in len_encoded:
                attr = b''.join([attr, val.ljust(max_length)])
            # we now have the encoded strings padded to max length
            length_attr = len(attr)
            # the length of the structure must be in units of 4
            length_structure = 6 * 4 + length_attr
            new_length_structure = ((length_structure+3)//4)*4 # round it
            delta_length = new_length_structure - length_structure
            returned = struct.pack("iiiiii",
                                   pymqi.CMQCFC.MQCFT_STRING_LIST, # Type
                                   new_length_structure, # length of this structure
                                   code,         # What sort eg decimal MQCA_Q_NAME value
                                   pymqi.CMQC.MQCCSI_DEFAULT,
                                   count,        # of elements
                                   max_length)

        if delta_length == 0:
            returned = b''.join([returned, attr])       # 0
        elif delta_length == 1:
            returned = b''.join([returned, attr, b' '])  # 1
        elif delta_length == 2:
            returned = b''.join([returned, attr, b'  ']) # 2
        elif delta_length == 3:
            returned = b''.join([returned, attr, b'   ']) # 3


        return returned
    def set_byte_string(self, code, operator, value):
        """
        Create the structure to handle bytes strings.

        very similar to set_string
          No encode
          no CCSID

        The data passed in can be
        code,operator=0,   value      for simple string
        code,operator!=0, value      for string filter
        code,opertor= 0, (tuple)      for list of strings
        """

        if operator == 0 and not isinstance(value, tuple):
            #attr = value.encode()
            attr = value
            length_attr = len(attr)
            # the length of the structure must be in units of 4
            length_structure = 4 * 4 + length_attr
            new_length_structure = ((length_structure+3)//4)*4 # round it
            delta_length = new_length_structure - length_structure
            returned = struct.pack("iiii",
                                   pymqi.CMQCFC.MQCFT_BYTE_STRING,
                                   # Type
                                   new_length_structure,
                                   code,
                                   # What sort eg decimal MQCA_Q_NAME value
                                   length_attr)# length of string

        elif operator != 0 and not isinstance(value, tuple): # we have a filter
            #attr = value.encode()
            attr = value
            length_attr = len(attr)
            # the length of the structure must be in units of 4
            length_structure = 5 * 4 + length_attr
            new_length_structure = ((length_structure+3)//4)*4
            delta_length = new_length_structure - length_structure

            returned = struct.pack("iiiii",
                                   pymqi.CMQCFC.MQCFT_BYTE_STRING_FILTER, # Type string filter
                                   new_length_structure, # length of this structure
                                   code,         # What sort eg decimal MQCA_Q_NAME value
                                   operator,     # eg value for eq
                                   # pymqi.CMQC.MQCCSI_DEFAULT, not for byte strings
                                   length_attr)          # length of string
        else: # we do not have listsof bytes strings
            pass

        if delta_length == 0:
            returned = b''.join([returned, attr])       # 0
        elif delta_length == 1:
            returned = b''.join([returned, attr, b' '])  # 1
        elif delta_length == 2:
            returned = b''.join([returned, attr, b'  ']) # 2
        elif delta_length == 3:
            returned = b''.join([returned, attr, b'   ']) # 3
        return returned

    def _keyword_sub_value_to_int(self, code, value, arg):
        if self.debug > 0 :
            print("_keyword_sub_value_to_int code=",code,"value=",value,"arg=",arg)
        val = value
        if isinstance(value, str):
            if code in SMQPCF.sLookupTypes: #coverrt  1023 to MQQSOT
                vcode = SMQPCF.sLookupTypes.get(code)
                tup = (vcode, value)
                if tup in SMQPCF.sLookupToI:
                    val = SMQPCF.sLookupToI.get(tup)
                else:
                    raise ValueError("MQPCF parameter not found in sLookupToI ", vcode, value)
            else:
                raise ValueError("MQPCF parameter not found in sLookupTypes", code)
        return val

    def set_integer(self, code, operator, value, arg):
        """

        Create the structure to handle integer(s).

        The data passed in can be
        code,operator =0, value      for simple string/integer
        code,operator!=0, value      for string filter
        code,opertor = 0, (tuple)    for list of strings/integer
        """

        if operator == 0 and not isinstance(value, tuple):
            length_structure = 4 * 4
            val = self._keyword_sub_value_to_int(code, value, arg)
            # convert to byte string
            returned = struct.pack("iiii",
                                   pymqi.CMQCFC.MQCFT_INTEGER, #  Type
                                   length_structure,           # length of this structure
                                   code,               # What sort eg decimal MQCA_Q_NAME value
                                   val)                     # converted value
            return returned
        elif operator != 0 and not isinstance(value, tuple): # we have aninteger filter
            length_structure = 5 * 4
            val = self._keyword_sub_value_to_int(code, value, arg)
            # convert to byte string
            returned = struct.pack("iiiii",
                                   pymqi.CMQCFC.MQCFT_INTEGER_FILTER, #  Type
                                   length_structure,           # length of this structure
                                   code,               # What sort eg decimal MQCA_Q_NAME value
                                   operator,     # eg value for eq
                                   val)                     # converted value
            return returned
        else: # we have a list of integers
            count = len(value)
            values = b''
            # build up the structure with 4 byte numbers
            for vv in value:
                val = self._keyword_sub_value_to_int(code, vv, arg)
                values = b''.join([values, struct.pack("i", val)])
            length_structure = 4 * 4 + 4 * count
            returned = struct.pack("iiii",
                                   pymqi.CMQCFC.MQCFT_STRING_LIST, # Type
                                   length_structure, # length of this structure
                                   code,         # What sort eg decimal MQCA_Q_NAME value
                                   count)        # of elements
            return b''.join([returned, values])

    def set_integer64(self, code, operator, value):
        """
        Create the structure to handle integer 64(s).

        The data passed in can be
        code,operator=0,   value      for simple string
        # code,operator!=0, value      for string filter
        code,opertor= 0, (tuple)      for list of strings
        """
        # no filtering
        #
        if not isinstance(value, tuple):
            length_structure = 4 * 4 + 8 # 4 long fields + long field
            val = value
            if isinstance(value, str):
                val = SMQPCF.selectTypeS.get(value)
                val = val[1]
                if val is None:
                    raise ValueError("MQPCF parameter invalid", value)

            # convert to byte string
            returned = struct.pack("iiiiQ", # Q is 8 byte number
                                   pymqi.CMQCFC.MQCFT_INTEGER64, #  Type
                                   length_structure,           # length of this structure
                                   code,               # What sort eg decimal MQCA_Q_NAME value
                                   operator,     # eg value for eq
                                   val)                     # converted value
            return returned

        else: # we have a list of integers
            count = len(value)
            values = b''
            for vv in value:
                if isinstance(vv, str):
                    val = SMQPCF.selectTypeS.get(vv)
                    val = val[1]
                    if val is None:
                        raise ValueError("MQPCF parameter invalid", value)
                else: val = vv # number
                values = b''.join([values, struct.pack("Q", val)])
            for vv in value:
                values = b''.join([values, vv])
            length_structure = 4 * 4 + 8 * count
            returned = struct.pack("iiii",
                                   pymqi.CMQCFC.MQCFT_INTEGER64_LIST, # Type
                                   length_structure, # length of this structure
                                   code,         # What sort eg decimal MQCA_Q_NAME value
                                   count)        # of elements
            return b''.join([returned, values])


def zget_h_admin_queue(qmgr=None, queue=b'SYSTEM.ADMIN.COMMAND.QUEUE'):
    """
    create an MQ OD for the command (or user specified) queue
    """
    admin = pymqi.OD()
 #   print("getAdminQueue",type(qmgr),type(queue))
    if not isinstance(queue, bytes):
        queue = queue.encode()
    if qmgr is None:
        raise ValueError("QMGR name must be specified")
    admin.ObjectName = queue
    hAdmin = pymqi.Queue(qmgr, admin, pymqi.CMQC.MQOO_OUTPUT)
    return hAdmin

# get replyqueue - by default create a dynamic queue
def zget_h_reply_queue(qmgr=None, queue=None):
    """
    Create an PyMQI Queue object either for passed queue or
    for a model queue.
    """
    if queue is None:
        queue = b'SYSTEM.MQSC.REPLY.QUEUE'
    #      options = pymqi.CMQC.MQOO_INPUT_EXCLUSIVE|pymqi.CMQC.MQOO_INQUIRE
    #reply = pymqi.OD()
    #reply.ObjectName = queue
    h_reply = pymqi.Queue(qmgr,
                          queue,
                          pymqi.CMQC.MQOO_INPUT_SHARED
                          |pymqi.CMQC.MQOO_INQUIRE)
    return h_reply
