// Copyright (c) 2019 Stromness Software Solutions.
//  
//  All rights reserved. This program and the accompanying materials
//  are made available under the terms of the Eclipse Public License v1.0
//  which accompanies this distribution, and is available at
// http://www.eclipse.org/legal/epl-v10.html
// 
// Contributors:
//    Colin Paice - Initial Contribution

// DISCLAIMER
// You are free to use this code in any way you like, subject to the
// & IBM disclaimers & copyrights. I make no representations
// about the suitability of this software for any purpose. It is
// provided "AS-IS" without warranty of any kind, either express or
// implied.

// USAGE:
// =====
// mon( a,b,c are the colums of index
//      d is the field name
//      e is the units
//      f is the long description...
//    )
// use like ( to create python constants)
// #define mon(a,b,c,d,e,f,...) 
// printf(",(\"MONITOR\",%s%s%s): ,\"%s\"\n",#a,#b,#c,#d);
// #include <monitor2.h>
// This produces
//  ,("MONITOR",0102: ,"RAM_Total_MB"


mon(0,0,00,User_CPU_pc           ,Percent,User CPU time percentage )//z
mon(0,0,01,Sys_CPU_pc            ,Percent,System CPU time percentage )//z
mon(0,0,02,CPU_Load1M            ,Hundredths,CPU load - one minute average )//z
mon(0,0,03,CPU_Load5M            ,Hundredths,CPU load - five minute average )//z
mon(0,0,04,CPU_Load15M           ,Hundredths,CPU load - fifteen minute average )//z
mon(0,0,05,RAM_Free_pc           ,Percent,RAM free percentage )//z
mon(0,0,06,RAM_Total_MB          ,MB,RAM total bytes )//z
mon(0,1,00,User_CPU_pc           ,Percent,User CPU time - percentage estimate for queue manager )//z
mon(0,1,01,Sys_CPU_pc            ,Percent,System CPU time - percentage estimate for queue manager )//z
mon(0,1,02,RAM_Total_MB          ,MB,RAM total bytes - estimate for queue manager )//z
mon(1,0,04,Trace_fs_use_MB       ,MB,MQ trace file system - bytes in use )//z
mon(1,0,05,Trace_system_free_pc  ,Percent,MQ trace file system - free space )//z
mon(1,0,06,Errors_fs_in_use_MB   ,MB,MQ errors file system - bytes in use )//z
mon(1,0,07,Errors_fs_free_pc     ,Percent,MQ errors file system - free space )//z
mon(1,0,08,FDC_file_count        ,Unit,MQ FDC file count )//z
mon(1,1,00,QM_fs_in_use_MB       ,MB,Queue Manager file system - bytes in use )//z
mon(1,1,01,QM_fs_free_pc         ,Percent,Queue Manager file system - free space )//z
mon(1,2,00,Log_in_use_MB         ,Unit,Log - bytes in use )//z
mon(1,2,01,Log_max_MB            ,Unit,Log - bytes max )//z
mon(1,2,02,Log_fs_in_use         ,Unit,Log file system - bytes in use )//z
mon(1,2,03,Log_fs_max            ,Unit,Log file system - bytes max )//z
mon(1,2,04,Log_physical_written  ,Delta,Log - physical bytes written )//z
mon(1,2,05,Log_logic_written     ,Delta,Log - logical bytes written )//z
mon(1,2,06,Log_write_latency     ,Microseconds,Log - write latency )//z
mon(1,2,07,Log_space_in_use_pc   ,Percent,Log - current primary space in use )//z
mon(1,2,08,Log_space_util_pc     ,Percent,Log - workload primary space utilization )//z
mon(1,2,09,Log_media_MB          ,MB,Log - bytes required for media recovery )//z
mon(1,2,10,Log_reusable_MB       ,MB,Log - bytes occupied by reusable extents )//z
mon(1,2,11,Log_w_archive_MB      ,MB,Log - bytes occupied by extents waiting to be archived )//z
mon(1,2,12,Log_write_size        ,Unit,Log - write size )//z
mon(2,0,00,MQCONNs_OK            ,Delta,MQCONN/MQCONNX count )//z
mon(2,0,01,MQCONNNs_failed       ,Delta,Failed MQCONN/MQCONNX count )//z
mon(2,0,02,MQCONNs_hwm           ,Unit,Concurrent connections - high water mark )//z
mon(2,0,03,MQDISC                ,Delta,MQDISC count )//z
mon(2,1,00,MQOPEN                ,Delta,MQOPEN count )//z
mon(2,1,01,MQOPEN_failed         ,Delta,Failed MQOPEN count )//z
mon(2,1,02,MQCLOSE               ,Delta,MQCLOSE count )//z
mon(2,1,03,MQCLOSE_failed        ,Delta,Failed MQCLOSE count )//z
mon(2,2,00,MQINQ                 ,Delta,MQINQ count )//z
mon(2,2,01,MQINQ_failed          ,Delta,Failed MQINQ count )//z
mon(2,2,02,MQSET                 ,Delta,MQSET count )//z
mon(2,2,03,MQSET_failed          ,Delta,Failed MQSET count )//z
mon(2,3,00,MQPUTs                ,Delta,Interval total MQPUT/MQPUT1 count )//z
mon(2,3,01,MQPUT_bytes           ,Delta,Interval total MQPUT/MQPUT1 byte count )//z
mon(2,3,02,MQPUTs_NP             ,Delta,Non-persistent message MQPUT count )//z
mon(2,3,03,MQPUTs_P              ,Delta,Persistent message MQPUT count )//z
mon(2,3,04,MQPUTs_failed         ,Delta,Failed MQPUT count )//z
mon(2,3,05,MQPUT1s_NP            ,Delta,Non-persistent message MQPUT1 count )//z
mon(2,3,06,MQPUT1s_P             ,Delta,Persistent message MQPUT1 count )//z
mon(2,3,07,MQPUT1s_failed        ,Delta,Failed MQPUT1 count )//z
mon(2,3,08,MQPUT_NP_bytes        ,Delta,Put non-persistent messages - byte count )//z
mon(2,3,09,MQPUT_P_bytes         ,Delta,Put persistent messages - byte count )//z
mon(2,3,10,MQSTATs               ,Delta,MQSTAT count )//z
mon(2,4,00,MQGETs                ,Delta,Interval total destructive get- count )//z
mon(2,4,01,MQGET_bytes           ,Delta,Interval total destructive get - byte count )//z
mon(2,4,02,MQGETs_NP             ,Delta,Non-persistent message destructive get - count )//z
mon(2,4,03,MQGETs_P              ,Delta,Persistent message destructive get - count )//z
mon(2,4,04,MQGETs_failed         ,Delta,Failed MQGET - count )//z
mon(2,4,05,MQGET_NP_bytes        ,Delta,Got non-persistent messages - byte count )//z
mon(2,4,06,MQGET_P_bytes         ,Delta,Got persistent messages - byte count )//z
mon(2,4,07,Browses_NP            ,Delta,Non-persistent message browse - count )//z
mon(2,4,08,Browses_P             ,Delta,Persistent message browse - count )//z
mon(2,4,09,Browses_failed        ,Delta,Failed browse count )//z
mon(2,4,10,Browses_NP_bytes      ,Delta,Non-persistent message browse - byte count )//z
mon(2,4,11,Browses_P_bytes       ,Delta,Persistent message browse - byte count )//z
mon(2,4,12,Expired               ,Delta,Expired message count )//z
mon(2,4,13,Purge_queue           ,Delta,Purged queue count )//z
mon(2,4,14,MQCBs                 ,Delta,MQCB count )//z
mon(2,4,15,MQCB_failed           ,Delta,Failed MQCB count )//z
mon(2,4,16,MQCTLs                ,Delta,MQCTL count )//z
mon(2,5,00,Commits               ,Delta,Commit count )//z
mon(2,5,02,Rollbacks             ,Delta,Rollback count )//z
mon(2,6,00,Create_durable_sub    ,Delta,Create durable subscription count )//z
mon(2,6,01,Alter_durable_sub     ,Delta,Alter durable subscription count )//z
mon(2,6,02,Resume_durable-sub    ,Delta,Resume durable subscription count )//z
mon(2,6,03,Create_ndurable_sub   ,Delta,Create non-durable subscription count )//z
mon(2,6,06,c/a/r_sub_failed      ,Delta,Failed create/alter/resume subscription count )//z
mon(2,6,07,Delete_durable        ,Delta,Delete durable subscription count )//z
mon(2,6,08,Delete_ndurable       ,Delta,Delete non-durable subscription count )//z
mon(2,6,09,Delete_sub_failed     ,Delta,Subscription delete failure count )//z
mon(2,6,10,MQSUBRQs              ,Delta,MQSUBRQ count )//z
mon(2,6,11,MQSUBRQ_failed        ,Delta,Failed MQSUBRQ count )//z
mon(2,6,12,Durable_sub_hwm       ,Delta,Durable subscriber - high water mark )//z
mon(2,6,13,Durable_sub_low       ,Delta,Durable subscriber - low water mark )//z
mon(2,6,14,NDurable_sub_hwm      ,Delta,Non-durable subscriber - high water mark )//z
mon(2,6,15,NDurable_sub_lwm      ,Delta,Non-durable subscriber - low water mark )//z
mon(2,7,00,Topic_puts            ,Delta,Topic MQPUT/MQPUT1 interval total )//z
mon(2,7,01,Topic_put_bytes       ,Delta,Interval total topic bytes put )//z
mon(2,7,02,Pub_to_subs           ,Delta,Published to subscribers - message count )//z
mon(2,7,03,Pub_to_sub_bytes      ,Delta,Published to subscribers - byte count )//z
mon(2,7,04,Topic_puts_NP         ,Delta,Non-persistent - topic MQPUT/MQPUT1 count )//z
mon(2,7,05,Topic_puts_P          ,Delta,Persistent - topic MQPUT/MQPUT1 count )//z
mon(2,7,06,Topic_puts_failed     ,Delta,Failed topic MQPUT/MQPUT1 count )//z
mon(3,0,00,MQOPENs               ,Delta,MQOPEN count )//z
mon(3,0,01,MQCLOSEs              ,Delta,MQCLOSE count )//z
mon(3,1,00,MQINQs                ,Delta,MQINQ count )//z
mon(3,1,01,MQSETs                ,Delta,MQSET count )//z
mon(3,2,00,MQPUTs                ,Delta,MQPUT/MQPUT1 count )//z
mon(3,2,01,MQPUTs_bytes          ,Delta,MQPUT byte count )//z
mon(3,2,02,MQPUTs_NP             ,Delta,MQPUT non-persistent message count )//z
mon(3,2,03,MQPUTs_P              ,Delta,MQPUT persistent message count )//z
mon(3,2,04,MQPUT1s_NP            ,Delta,MQPUT1 non-persistent message count )//z
mon(3,2,05,MQPUT1s_P             ,Delta,MQPUT1 persistent message count )//z
mon(3,2,06,MQPUTs_NP_bytes       ,Delta,non-persistent byte count )//z
mon(3,2,07,MQPUTs_P_bytes        ,Delta,persistent byte count )//z
mon(3,2,08,MQPUTs_avoided_pc     ,Percent,queue avoided puts )//z
mon(3,2,09,MQPUTS_avoided_bytes_pc,Percent,queue avoided bytes )//z
mon(3,2,10,MQPUTs_lock_contention_pc,Percent,lock contention )//z
mon(3,3,00,MQGETs                ,Delta,MQGET count )//z
mon(3,3,01,MQGET_bytes           ,Delta,MQGET byte count )//z
mon(3,3,02,MQGETs_NP             ,Delta,destructive MQGET non-persistent message count )//z
mon(3,3,03,MQGETS_P              ,Delta,destructive MQGET persistent message count )//z
mon(3,3,04,MQGET_NO_bytes        ,Delta,destructive MQGET non-persistent byte count )//z
mon(3,3,05,MQGET_P_bytes         ,Delta,destructive MQGET persistent byte count )//z
mon(3,3,06,Browses_NP            ,Delta,MQGET browse non-persistent message count )//z
mon(3,3,07,Browses_P             ,Delta,MQGET browse persistent message count )//z
mon(3,3,08,Browses_NP_bytes      ,Delta,MQGET browse non-persistent byte count )//z
mon(3,3,09,Browses_P_bytes       ,Delta,MQGET browse persistent byte count )//z
mon(3,3,10,Msgs_expired          ,Delta,messages expired )//z
mon(3,3,11,Queue_purged          ,Delta,queue purged count )//z
mon(3,3,12,Avg_toq               ,Microseconds,average queue time )//z
mon(3,3,13,Queue_depth           ,Unit,Queue depth )//z
