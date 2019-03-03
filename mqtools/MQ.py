import mqtools.smqpcf as SMQPCF
from   . code   import formatMQMD  as mqmd
from   . code   import format  as fo2 
#import mqtools.code.fromMQMD as mqmd

# from code import formatMQMD 	  as mqmd
def format_MQMD(md,strip="yes", debug=0):
    md = mqmd.format_MQMD(md,strip = strip,debug = debug)
    return md
    pass

def format(md,strip="yes", debug=0):
    md = fo2.format(md,strip = strip,debug = debug)
    return md
    pass
