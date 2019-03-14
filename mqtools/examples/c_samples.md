# C Samples

Two samples are provided  
  1. One for putting an getting messages - with bugs to educate people on debugging MQ!
  1. One acting as a MQ server in C  

Use the makefile to compile them
* make server
* make putgetsample

## putgetsample.c
This is an almost working sample, but you need to fix some MQ coding errors before
it works.
I'll list some of the errors at the bottom of this document to show what problems 
it highlights - so if you do not want to know - dont look at the bottom

The program prompts for two input messages, and puts them to the output queue.
It then tries to get both the messages and displays them. 
There are some errors that only occur when multiple people are using the same 
queue concurrently.


Syntax
* ./putgetsample
* qm_name the queue manager name
* output_queuename - messages are put here
* input_queue name.   This is used to get messages.  It can be = to specify the same queue

### examples

* ./putgetsample QMA myqueue myqueue
* ./putgetsample QMA SYSTEM.DEFAULT.MODEL.QUEUE SYSTEM.DEFAULT.MODEL.QUEUE
  * this creates and uses a temporary dynamic queue 
* ./putgetsample QMA serverQueue SYSTEM.DEFAULT.MODEL.QUEUE 
  * this puts to a server queue, and waits for the response to come back

## server.c 
This is a working sample. The parameters are
     server qm_name input_queue <wait_time_in_seconds>

it displays a message showing number of messages processed every 1000 messages.

## Problems that need to be fixed
* missing MQOO_OUTPUT on the output queue 
* MQOO_INPUT_EXCLUSIVE is used, so the queue cannot be shared
* Expiry time is set to 1 second so the first message has expired before it is got
* Messages use the same msgid and correlid, so I can get the messages you put
* Input buffer is too small

The code that needs to be changed is all within 30 lines of code delimited by 
  * //****** For education make changes below here ****************	
  * //****** For education make changes above here  **************
