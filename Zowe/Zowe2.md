# Starting Zowe

There are many parts to Zowe.   The guide below will start from a minimum configuration and add facilities.

## Pre-reqs

## Create a starting configuration.

Make a copy of your configuration for example cp zowe.yaml zowe.yaml.Jan142025

Edit the zowe.yaml file

    network: 
        server: 
            tls: 
            attls: false 
            # TLS settings only apply when attls=false 
            # Else you must use AT-TLS configuration for TLS customization. 
            minTls:  TLSv1.2 
            maxTls:  TLSv1.3 
        client: 
            tls: 
            attls: false 
            minTls:  TLSv1.2 
            maxTls:  TLSv1.3 

TLS v1.2 is more common than TLSv1.3.  Check the configuration works with TLSv1.2, then change minTls to TLSv1.3

Find components: in column 1
The component names are in column 3.  
Change *enabled: true* to *enabled: false* for 

- gateway
- zaas
- discovery
- caching-services
- app-server
-
- explorer-jes
- explorer-mvs

but keep zss enabled.   Note the port for zss
    zss: 
      enabled: true 
      port: 7557 

Find *certficate:* in column 3.   Check your certificate definitions.  For example

      certificate: 
        keystore: 
          type: JCERACFKS 
          file: safkeyring:////IZUSVR/CCPKeyring.IZUDFLT 
          alias: CONN2.IZUDFLT 
        truststore: 
          type: JCERACFKS 
          file: safkeyring:////IZUSVR/CCPKeyring.IZUDFLT 
                                                                    

### Start the common services started task

   s ZWWSISTC

This displays output like

    IEF403I CCPSISTC - STARTED - TIME=07.54.25                               
    ZWES0001I ZSS Cross-Memory Server starting, version is 3.1.0+20250108    
    IEF761I CCPSISTC CCPSISTC PARMLIB ZWESIS DD IS ALREADY ALLOCATED AND     
    WILL BE USED BY THIS TASK.                                               
    IEE252I MEMBER ZWESIP00 FOUND IN IBMUSER.ZWEV3.CUST.PARMLIB              
    ZWES0105I Core server initialization started 689                         
    ZWES0109I Core server ready 690                                          
    ZWES0200I Modify commands: 691                                           
            DISPLAY  OPTION_NAME  - Print service information             
                OPTION_NAME:                                                
                CONFIG - Print server configuration information (defau    
            FLUSH   - Print all pending log messages                      
            LOG <COMP_ID> <LOG_LEVEL> - Set log level                     
                COMP_ID:                                                    
                CMS   - Cross memory server                               
                CMSPC - PC routines                                       
                STC   - STC base                                          
                LOG_LEVEL:                                                  
                SEVERE                                                    
                WARNING                                                   
                INFO                                                      
                DEBUG                                                     
                DEBUG2                                                    
                DEBUG3                                                    

Once this has started successfully start the main task

    s ZWESLSTC

It generates messages like

    +ZWEL0021I Zowe Launcher starting                                       
    IRR812I PROFILE * (G) IN THE STARTED CLASS WAS USED 698                 
            TO START BPXAS WITH JOBNAME BPXAS.                              
    ...                              
    BPXP024I BPXAS INITIATOR STARTED ON BEHALF OF JOB ZWESLSTC RUNNING IN   
    ASID ... 
    +ZWEL0018I Zowe instance prepared successfully                  
    +ZWEL0006I starting components                                  
    +ZWEL0001I component zss started 

Check it works by using a web browser to HTTPS://...:7557/plugins

If the browser has been configured for more than one client certificate, you will be prompted for a choice of certificate.   Pick a certificate and you should get data like "pluginDefinitions":[{"identifier":"org.zowe.configjs","apiVersion":"2.0.0",*{luginVersion":"3.0.0+20240925",...*

If it starts successfully you can shut it down using.

    P ZWESLSTC

When you start Zowe it spawns threads into BPXAS address spaces, which show up as jobs with the same name (ZWESLSTC) but you cannot look at their output in the spool.   

### Problem determination

Check for messages on the system log.
Check within ZWESLSTC started task output for error messages.

You can enable trace in the zowe.yaml file

    launchScript: 
      #set to "debug" or "trace" to display extra debug information 
      logLevel: "info" 

If the zss fails to start, check in the logs directory of the instance directory for the zss... log file, such as 
 */u/tmp/zowec/logs/zssServer-2025-02-03-08-15.log*

 This had

    ZWES1061I TLS settings: keyring 
    'IZUSVR/CCPKeyring.IZUDFLT2', label 'CONN2.IZUDFLT', 
    password '(no password)', stash '(no stash)' 
    ZWES1060W Failed to init TLS environment, rc=1(Handle is not valid) 

If the system starts, but you cannot connect from a web browser, 

    zss: 
    enabled: true 
    port: 7557 
    crossMemoryServerName: ZWESIS_STD 
    agent: 
        jwt: 
        fallback: true 
        64bit: true 
        https: 
        trace: true  

This will produce a trace file like

    logs/zssServer-2025-02-03-17-36.log.tlstrace 

which you can format with

    gsktrace logs/zssServer-2025-02-03-17-36.log.tlstrace     >gsk.txt    