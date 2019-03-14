// C program to act as a simple MQ server.
// It reads messages from a queue, and puts a reply to the replyto queue in the message
//
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


#pragma csect (CODE,"SERVER")
#pragma csect (STATIC,"SERVERS")

#include <string.h>
#include <stdio.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <cmqc.h>
#include <cmqstrc.h>
// Overview
// This program acts as a simple MQ server.
// It requires as parameters QueueManageName ServerInputQueue
// with optional parameter the MQGETWAIT time in seconds.  If no messages are
// returned within this time the server ends.
/*
 It does the following
   Connects to
   Open the server queue
   Loop:
      MQGET
	  MQPUT
	  MQCMIT If message was persistent
   End:
  If the MQGET message buffer is too small it allocates a buffer big enough
  for the message.
  For the next message, if the message fits into the original buffer (4KB)
  it frees the big buffer.
 */


int  main(int argc, char *argv[]){
	MQHOBJ serverHandle;

	MQOD serverOD = {MQOD_DEFAULT};
	MQOD replyOD  = {MQOD_DEFAULT};
	MQLONG serverOptions=MQOO_INPUT_AS_Q_DEF + MQOO_FAIL_IF_QUIESCING;
	//                     +MQOO_INQUIRE
	//                     +MQOO_SAVE_ALL_CONTEXT
	//                     +MQOO_INPUT_AS_Q_DEF;
	MQGMO mqgmo={MQGMO_DEFAULT};

	long messageSize;
	MQLONG messageLength;

	MQMD mqmd = {MQMD_DEFAULT};    /* Message descriptor      */
	MQMD staticMQMD = {MQMD_DEFAULT};    /* Message descriptor      */
	MQPMO mqpmo = {MQPMO_DEFAULT}; /* Put-Message Options    */
	MQHOBJ requestHandle;
	long bufferLen;
	char buffer[160];
	long loopCount = 0;
	long waitTime = 0;
	long reget = 0; // needed for message buffer to small and we want same message

	/* Message buffer */
	long bufferLength;
	long rcode;
	char * p4KBuffer; // normal buffer
	long   l4KBuffer; // size of this buffer
	char * pBuffer  ; // for doing the puts and gets
	long   lBuffer  ; //
	long message_count = 0;

	char * pBigBuffer = 0;
	MQHCONN     hConn;
	int mqcc,mqrc;
	l4KBuffer  = 4096;
	p4KBuffer = (char *) malloc(l4KBuffer);
    pBuffer = p4KBuffer;
    lBuffer = l4KBuffer;


	printf("Compiled %s %s.\n",__DATE__,__TIME__);
	if ( argc <= 2 )
	{
		printf("Invalid number of parameters.  needs QM QueueName <wait_time_in_seconds>\n");
	}
	if (argc >=4 )
		waitTime = atol(argv[3]) *1000; // convert to seconds
	if (waitTime == 0) waitTime = 3600 * 1000 ;// 1 hour
	printf("Get Wait time %li seconds\n",waitTime/1000);

	MQCONN(argv[1], &hConn, &mqcc,&mqrc);
	printf ("MQ conn to %s cc %i rc %i %s\n",argv[1],mqcc,mqrc,MQRC_STR(mqrc));
	if (mqrc !=0) return 8;


	strncpy(serverOD.ObjectName,argv[2],sizeof(serverOD.ObjectName));
	MQOPEN(hConn,
			&serverOD,
			serverOptions,
			&serverHandle,
			&mqcc,
			&mqrc);
	switch (mqcc)
	{
	case MQCC_OK:
		break;
	default:;
	printf("Return code from MQOPEN to %s is cc %d rc %d,%s\n",
			serverOD.ObjectName,mqcc,mqrc,MQRC_STR(mqrc))	;
	return(mqrc);


	}
	mqgmo.WaitInterval = waitTime ; /* preset wait      */
	for ( long i = 0;;i++)
	{
		message_count ++;
		if ( message_count% 1000 == 0)
			printf("messages loop counter %ld\n",message_count);
		mqgmo.Options   =   MQGMO_SYNCPOINT_IF_PERSISTENT
				+ MQGMO_FAIL_IF_QUIESCING
				+ MQGMO_CONVERT
				+ MQGMO_WAIT;

		memcpy(&mqmd,&staticMQMD,sizeof(MQMD)); // need to clear this every loop
		retry_get:;                             // but this uses same msgid
		MQGET(hConn,
				serverHandle,
				&mqmd,
				&mqgmo,
				lBuffer,
				pBuffer,
				&messageLength,
				&mqcc,
				&mqrc);
		switch (mqrc )
		{
		case MQCC_OK:
			if ( lBuffer > l4KBuffer &&  messageLength < l4KBuffer )
			{
				free(pBuffer);
				pBuffer = p4KBuffer;
				lBuffer = l4KBuffer;
			}
			break;
		case MQRC_NO_MSG_AVAILABLE:
			if (reget > 0) // we asked for msg with msgid and corredid -
				// someone else may have got it
			{
				printf("after getting bigger buffer, message not found on retry\n");
				reget = 0;
				continue; // go and get the next available message
			}
			printf("SERVER MQGET timed out, queue %-48.48s\n",serverOD.ObjectName);
			return(mqcc);

		case MQRC_TRUNCATED_MSG_FAILED:
			if (lBuffer > l4KBuffer) // so we had done a malloc for a bigger buffer
				free(pBuffer);
			lBuffer =  messageLength;
			pBuffer = malloc(lBuffer);
			if ( pBuffer == 0){
				printf("Malloc for %ld bytes failed\n",lBuffer);
				return(8);
			}
			printf("Allocated a bigger buffer %ld bytes\n",lBuffer);
			reget = 1; // so we can check if this message was processed by another thread
			goto retry_get;

		default:
			printf("MQGET get cc %d rc %d %s\n",mqcc,mqrc,MQRC_STR(mqrc));
			return(8);
		}

		memcpy( replyOD.ObjectName ,
				mqmd.ReplyToQ,
				MQ_Q_NAME_LENGTH );

		memcpy( replyOD.ObjectQMgrName ,
				mqmd.ReplyToQMgr ,
				MQ_Q_MGR_NAME_LENGTH );

		mqmd.MsgType = MQMT_REPLY ;
		memcpy(&mqmd.CorrelId,&mqmd.MsgId   ,sizeof( mqmd.MsgId   ));

		mqmd.Report = MQRO_NONE ;
		if (mqmd.Persistence  ==  MQPER_NOT_PERSISTENT )
		{
			mqpmo.Options =         MQPMO_NO_SYNCPOINT +
					MQPMO_FAIL_IF_QUIESCING;
		}
		else
			mqpmo.Options =         MQPMO_SYNCPOINT +
			MQPMO_FAIL_IF_QUIESCING;

		MQPUT1( hConn,
				&replyOD ,
				&mqmd ,
				&mqpmo,
				messageLength,
				pBuffer,
				&mqcc,
				&mqrc );
		switch (mqcc)
		{
		case MQCC_OK:
			;
			break;

		default:
			printf("MQPUT1 %48.48s cc %d rc %d %s\n", mqmd.ReplyToQ, mqcc,mqrc,MQRC_STR(mqrc));
			return(mqcc);
		}
		if (mqpmo.Options &&  MQPMO_SYNCPOINT == MQPMO_SYNCPOINT)
		{
			MQCMIT(hConn,&mqcc,&mqrc);
			if ( mqcc != 0) printf("MQCMIT failed cc %d rc %d %s\n",mqcc,mqrc,MQRC_STR(mqrc));
		}
	}
}
