// program to be used to helping MQ administrators understand coding techniques
// MIT License
//
// Copyright (c) 2019 Stromness Software Solutions.
//
//Permission is hereby granted, free of charge, to any person obtaining a copy
//of this software and associated documentation files (the "Software"), to deal
//in the Software without restriction, including without limitation the rights
//to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//copies of the Software, and to permit persons to whom the Software is
//furnished to do so, subject to the following conditions:
//
//The above copyright notice and this permission notice shall be included in all
//copies or substantial portions of the Software.
//
//THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//SOFTWARE.
//
//* Contributors:
//*   Colin Paice - Initial Contribution
// Compile this with make file containing
#ifdef no 
cparms = -Wno-write-strings 
clibs = -I. -I../inc -I'/usr/include'  -I'/opt/mqm/inc'
lparms = -L /opt/mqm/lib64 -Wl,-rpath=/opt/mqm/lib64 -Wl,-rpath=/usr/lib64 -lmqm 
% : %.c
gcc -m64  $(cparms) $(clibs)   $< -o $@  $(lparms)
#endif
//  make putgetsample
// then use ./putgetsample qmgr putqueue getqueue
// case 1. define a  permament queue and use it - have every one share it
// case 2 use SYSTEM.DEAULT.MODEL.QUEUE - and not the queue being used
// case 3 define a remote queue ... and remove the MQOO_INPUT..
// 
// You will be asked for input twice per program run.
// Enter your full name each time
// Fix problems as the arise

#pragma csect (CODE,"SAMPLE")
#pragma csect (STATIC,"SAMPLES")

#define BUFFLEN  5000

#include <cmqc.h>
#include <string.h>
#include <stdio.h>
#include <regex.h>
#include <ctype.h>
#include <cmqstrc.h>
#include <errno.h>


int main( int argc, char *argv[])
{
	printf("Compiled %s %s.\n",__DATE__,__TIME__);
	if ( argc != 4 )
	{
		printf("Invalid number of parameters.  needs QM putQueueName getQueuename\n");
		printf("getQueueName can be = to be same as the put queue\n");
	}


	/*----------------------------------------------------------------*/
	/* Declaration of local variables used for the put1 call          */
	/*----------------------------------------------------------------*/
	MQMD     MsgDesc       = {MQMD_DEFAULT};
	MQPMO    PutMsgOpts    = {MQPMO_DEFAULT};
	MQLONG   PutMsgBuffLen = BUFFLEN;
	MQHOBJ   hObjInput;
	MQHOBJ   hObjOutput;
	MQHCONN  hconn;
	int mqcc,mqrc;
	char * pMsg;
	MQOD    ObjDescInput  = {MQOD_DEFAULT}; /* Object descriptor        */
	MQOD    ObjDescOutput = {MQOD_DEFAULT}; /* Object descriptor        */
	MQLONG  OpenOptionsOutput;              /* Options control MQOPEN   */
	MQLONG  OpenOptionsInput;              /* Options control MQOPEN   */
	/*----------------------------------------------------------------*/
	/* Declaration of local variables used for the get call           */
	/*----------------------------------------------------------------*/
	MQGMO  GetMsgOpts     = {MQGMO_DEFAULT};
	MQLONG DataLength;

	// save the queue name in the MQOD from 2nd parm
	strcpy( ObjDescOutput.ObjectName, argv[2]);

	//****** For education make changes below here ****************
#define REPLYBUFFERLENGTH 10

	OpenOptionsInput  = MQOO_INPUT_EXCLUSIVE +
			     	    MQOO_FAIL_IF_QUIESCING;
	OpenOptionsOutput =
			   MQOO_INPUT_EXCLUSIVE +
			   MQOO_FAIL_IF_QUIESCING;

	MsgDesc.MsgType = MQMT_REQUEST;
	MsgDesc.MsgType = MQMT_DATAGRAM;

	PutMsgOpts.Options = MQPMO_NO_SYNCPOINT +
			MQPMO_FAIL_IF_QUIESCING;

	MsgDesc.Expiry = 10; // 10 seconds

	GetMsgOpts.Options =
			MQGMO_NO_SYNCPOINT         +
			MQGMO_WAIT                 +
			MQGMO_FAIL_IF_QUIESCING;
	GetMsgOpts.WaitInterval = 5 * 1000; /* milliseconds */

	char * sMSGID ="MSGID6789012345678901234"; // exactly 24
	MQLONG Close_options = MQCO_DELETE_PURGE;

#define PUTSIZE 100

	//******* for education make changes above here  **************
	// 2027 type= request needs a reply to queue.
	//      use type=datagram
	/* connect to the provided queue manager  */
	MQCONN(argv[1], &hconn, &mqcc,&mqrc);
	printf ("MQ conn to %s cc %i rc %i %s\n",argv[1],mqcc,mqrc,MQRC_STR(mqrc));
	if (mqrc !=0 )  return 8;





	printf("MQ Output Queue being opened %48.48s\n",ObjDescOutput.ObjectName);
	MQOPEN( hconn,
				&ObjDescOutput,
				OpenOptionsOutput,
				&hObjOutput,
				&mqcc,
				&mqrc);
	printf("MQOPEN mqcc %i mqrc %i %s\n",mqcc,mqrc,MQRC_STR(mqrc));
	if (mqrc !=0 )  return mqrc;
	printf("MQ Queue opened name being used %48.48s\n",ObjDescOutput.ObjectName);
	printf("MQ Queue QMGR being used %48.48s\n",ObjDescOutput.ObjectQMgrName);

	if (strcmp(argv[3],"=") == 0)
				strcpy( ObjDescInput.ObjectName, ObjDescOutput.ObjectName);
	else
				strcpy( ObjDescInput.ObjectName, argv[3]);

	printf("MQ Input Queue being opened %48.48s\n",ObjDescInput.ObjectName);
	MQOPEN( hconn,
				&ObjDescInput,
				OpenOptionsInput,
				&hObjInput,
				&mqcc,
				&mqrc);
		printf("MQOPEN mqcc %i mqrc %i %s\n",mqcc,mqrc,MQRC_STR(mqrc));
		if (mqrc !=0 )  return mqrc;
		printf("MQ Input Queue name being used %48.48s\n",ObjDescInput.ObjectName);

#define LOOPCOUNT 2

	char data[1+PUTSIZE];
	char reply[REPLYBUFFERLENGTH];
	for ( int iLoop = 0;iLoop < LOOPCOUNT ;iLoop++)
	{
		memcpy( MsgDesc.MsgId,    sMSGID, sizeof( MsgDesc.MsgId ) );
		memcpy( MsgDesc.CorrelId, sMSGID, sizeof( MsgDesc.CorrelId ) );
		data[0] = 0;
		printf("Please enter your full name\n");
		fgets(data,PUTSIZE,stdin);
		int  ilen = strlen(data);
        memcpy(MsgDesc.ReplyToQ,ObjDescInput.ObjectName,48);
		MQPUT( hconn,
				hObjOutput,
				&MsgDesc,
				&PutMsgOpts,
				ilen,
				data,
				&mqcc,
				&mqrc);


		printf("Return code from put cc=%i rc=%i %s\n", mqcc,mqrc,MQRC_STR(mqrc) );
		if (mqrc !=0) return 8;
	}
	// now get the messages
	for ( int iLoop = 0;iLoop < LOOPCOUNT ;iLoop++)
	{
		// need to get the messages with our MSGID
		memcpy( MsgDesc.MsgId,    sMSGID, sizeof( MsgDesc.MsgId ) );
		memcpy( MsgDesc.CorrelId, sMSGID, sizeof( MsgDesc.CorrelId ) );

		memset( reply, ' ', sizeof( reply) );

		/*-------------------------------------------------------*/
		/* Get the reply from the queue                          */
		/*-------------------------------------------------------*/

		MQGET( hconn,
				hObjInput,
				&MsgDesc,
				&GetMsgOpts,
				REPLYBUFFERLENGTH,
				&reply,
				&DataLength,
				&mqcc,
				&mqrc );
		printf("Return code from get cc=%i rc=%i %s\n", mqcc,mqrc,MQRC_STR(mqrc) );
		if (mqrc !=0) return 8;

		printf("Get length:%i data:%*.*s.",DataLength,DataLength,DataLength, reply);

	}
	MQCLOSE( hconn,
			&hObjInput,
			Close_options,
			&mqcc,
			&mqrc);

	printf("MQCLOSE Input cc %i rc %i %s\n",mqcc,mqrc,MQRC_STR(mqrc));
	MQCLOSE( hconn,
				&hObjOutput,
				Close_options,
				&mqcc,
				&mqrc);

	printf("MQCLOSE output cc %i rc %i %s\n",mqcc,mqrc,MQRC_STR(mqrc));

	MQDISC(&hconn,&mqcc,&mqrc);
	printf("MQDISC cc %i rc %i %s\n",mqcc,mqrc,MQRC_STR(mqrc));
	return 0;
}
//   MsgDesc.MsgType = MQMT_DATAGRAM; // bug2  
