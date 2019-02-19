"""
Check standards of MQ Objects

A list of files is passed in. The files are in YAML format, one attribute
per line.
Each attribute is checked against a list, and differences are reported.
These attributes could be in a file (in YAML format) so you can externalise
these checks
"""
from ruamel.yaml import YAML
import sys
 
yaml=YAML()

ignore = ["ALTERATION_DATE","ALTERATION_TIME","CREATION_DATE","CREATION_TIME"]

less_than = {"CURRENT_Q_DEPTH":50,
            }
greater_than  = {"MAX_MSG_LENGTH":4194304,
                 "MAX_Q_DEPTH":9999,
                } 
not_equal      = {"INHIBIT_PUT":"PUT_ALLOWED",
                  "INHIBIT_GET":"GET_ALLOWED",
                  "SHAREABILITY":"SHAREABLE",
                 }

for q_name in sys.argv[1:]: # for all of the other parameters
   file  = open(q_name, 'r')            # open the file
   data = yaml.load(file)           # read it in
 
   for field_name in less_than:
      if not data[field_name] < less_than[field_name]:
         print(q_name,
               field_name,
               data[field_name],
               "Field in error.  It should be less than",less_than[field_name])

   for field_name in greater_than:
      if not data[field_name] > greater_than[field_name]:
         print(q_name,
               field_name,  # #f
               data[field_name],
               "Field in error.  It should be greater than",
               greater_than[field_name])


   for field_name in not_equal:
      if data[field_name] != not_equal[field_name] :
         print(q_name,
               field_name,
               data[field_name],
               "field is not equal to",
               not_equal[field_name])





