# Zowe planning and installation instructions


# Planning to install and configure Zowe.
See [Preparing for instalation](https://docs.zowe.org/stable/user-guide/installandconfig/)
for detailed information on the structure of Zowe files and data sets.

## Required  products 

-  Z/OS 2.5 or later
-  Java 17 IBM® Semeru Runtime Certified Edition for z/OS® version 17
- Node.js version v18.or later.  See [here](https://docs.zowe.org/stable/user-guide/systemrequirements-zos/#nodejs).

## Optional products

- z/OSMF.   This is used for Authentication and REST API services.
-  SDSF.   This is used to issue console commands, and capture the output

## Disk storage

- For the Zowe product.   This typically is in a directory 
like /usr/lpp/zowe.   It needs about 1300 MB, or  1600 Cyl.
- For each instance use Primary 118, Secondary 18 Cylinders.
- For the .pax file 440 MB
- Some PDSs are generated.  Together they use about 20 Cyl of DASD
## CPU 
???

## Intefaces

A TCP/IP configuration can have multiple IP addesses.  When Zowe initiates a connection to one of its components, it needs the correct IP address.

This is configured in *zowe.externalDomains* and can be a domain name or 
IP address.

## Ports 

The default ports in the configuration are 

- gateway 7554
- zaas 7552
- discovery 7553
- caching services 7555
- app server  7556
- zss 7557
- infinispan in memory caching, port 7600
- infinispan in memory caching key exchange, port 7600

These ports can be used by clients outside of z/OS, and between 
the Zowe started tasks.   You need to configure your network 
and firewalls to allow traffic on these ports.


# Understanding the configuration process

## z/OS system configuration

As part of the installation, one of the first steps is to run a script
which extracts PDS from the Zowe files.

There are two load libraries which will need to be APF authorised.

Two started task procedures will be created.
One started task is a server which can run authorised code.
The other is a Java program.
When Zowe starts up it spawns threads that run as BPXAS address 
spaces.   The names of the spawned threads are like ZWE1AD.   The prefix ZWE1 can be 
changed in the configuration file.

A member is created to be put into the parmlib concatentation.

The Zowe default dataset names have a prefix IBMUSER.ZOWEV3.   
You can use your own names, such as PP.ZOWEV3 ( for Program Products)

### Workload manager definitions
You should set up WorkLoad Manager definitions for the address spaces.
Note: that if a definitions has discretionary, any Java work will not run 
of GCPs if the ZIIPS are busy, so you need care in specifying which rule applies to the address spaces.

## Security definitions

You should protect the data sets produced by Zowe configuration; 
the sample library is not sensitive, but the load libraries are APF 
authorised, and these APF authorised libraries should be protected from 
being changed by an unauthorised user. 

As part of the configuration, security definitions are created.  


- Some changes are global, enabling some system wide facilities.  
Most systems will typically have these already enabled, but if not, 
you may want to configure them early to give plenty of time to 
test them.
  
  - Activate classes STARTED and FACILITY
  - Define FACILITY BPX.DAEMON 
  - Define FACILITY BPX.SERVER 
  - Define FACILITY BPX.JOBNAME 
  - Define FACILITY IRR.RUSERMAP 
  - Define FACILITY IRR.IDIDMAP
  - Define FACILITY IRR.RAUDITX

- Some changes are Zowe related, such as userid for Zowe.   This defaults to ZWEUSR
and group ZWEGRP.

  - Add group  ZWEADMIN 
  - Add userid definitions for ZWESVUSR and ZWESIUSR
  - Defines started task profiles for STARTED; ZWESLSTC*, ZWESISTC*, and ZWESASTC* (where ZWE is configurable)

- Other changes
  - A data set profile IBMUSER.ZWEV3.*.** for the data sets that Zowe install creates. 

You should consider how user's will authenticate.
As part of the TLS session initialisation the server can request the
client's certificate and use information from the certificate to
determine the userid to be used.
You can authenticate using:

- Userid and password
- using z/OSMF
- Multi Factor authentication - such as having a widget or mobile phone 
application which generates a  code as a one off, time limited code as a password.

You can use AT-TLS.

## Certificates
Zowe uses a keystore for storing the private key used by the server, and a trust store for the Certificate Authority keys needed to validate any client certificate sent to the server.   This can, but is not recommended, to be the same as the keystore.

You should use keyrings rather than .pem files, as they are more secure.
They keystore will need

- the server key. You can specify which key should be used.
- the Certificate Authority keys needed to validate the server key.
- the server userid needs access to the keyring.   
If the private key belongs to the server's userid,
 then the server's userid needs read access to the keyring. 
 If they private key belongs to a different userid, the server's userid 
 needs update access to the keyring.  See [here](https://www.ibm.com/docs/en/zos/3.1.0?topic=library-usage-notes) for more information.

## Operations

You need to start the two stared tasks. 
The authorised server is active and does not do much. You can start it at 
IPL and leave it running.

You start the Zowe Java task when you want to use Zowe.
You use the stop z/OS command (P ...) to terminate it.   
When it shuts down, it terminates the services running in BPXAS 
address spaces.

## Data management 
Zowe does not hold any state information.  The configuration files in the Zowe instance home directory should be backed up regularly, as well as the proclib and parmlib members.

## Running in a sysplex
The Zowe product libraries can be shared across all LPARs in a Sysplex.  You may want to consider mounting it read only.
A Zowe instance can be started on any LPAR, provided the home directory is available and writable.

You can create more Zowe instances on one LPAR ( why would you?)
or for availability you can create a Zowe instance on more than one LPAR.

## High availability

If you have a Zowe instance running on more than one LPAR,
if one instance is shutdown, you can (re)connect to a different solution, and logon.
You can also configure a [Zowe HA environment](https://docs.zowe.org/stable/user-guide/zowe-ha-overview), where you can
reconnect to a alternate instance, without needing to logon.

## Migrating to a new level of Zowe

Install the new level of Zowe into a different directory to your current system.
The process will update the Zowe PDS datasets 
...SZWEAUTH,
...SZWEEXEC,
...SZWELOAD,
...SZWESAMP

so you should back these up, or change the config file to use a different data set prefix.
To overwrite these datasets you need to explicitly set an option.

Copy the configuration files, so if you need to go back to the current level of code, you just rename the files and data sets and restart Zowe.


# Installing Zowe
You can install Zowe using SMP/E or using a PAX file.

Follow the instructions.
- [From SMP/E](https://docs.zowe.org/stable/user-guide/zosmf-install/)
- [From a .pax file](https://docs.zowe.org/stable/user-guide/install-zowe-zos-convenience-build)
Where it says *pax -ppx -rf <zowe-V.v.p>.pax*
  - cd to the product library for example cd /usr/lpp/zowe
  - unpax using pax -ppx -rf path-to-pax/<zowe-V.v.p>.pax such as  *pax -ppx -rf /tmp/zowe3.0.pax* 
  - you can remove the pax file if you no longer need it.

## General comment

In the following sections, we refer to configuration 
keys by using the concatenation of key names and dots. 
For example, if you want to update the configuration key 
zowe.certificate.keystore.type with the value PKCS12, 
you should set the value for this entry in the zowe.yaml:

zowe:
  # Specify the certificate keystore type
  certificate:
    keystore:
      type: PKCS12

where each level is indented two more spaces than the preceeding 
level

If you search for "zowe.certificate.keystore.type", you will not find it in the file.


Within the configuration is reference to a data set prefix ZWEV3.
You may want to use a name like PP.ZWE3 which fits with 
your data set naming convention.


My set up 

/u/tmp/zowep contains my installed libraries

/u/tmp/zowec contains my configuration
# Configuring Zowe

- You should have Zowe and the prereqs installed, for example Zowe
installed in /u/tmp/zowep.
- Create the directory for the Zowe instance configuration file, 
for example /u/tmp/zowec

The instructions below configure the minimal function Zowe instance.   This makes it quicker to resolve set up issues, such as certificate and keyring problems.   
The instructions then add more function, until it is fully configured.

## Create the configuration file


### Copy the yaml file from product directory to the instance directory

See [detailed instructions](https://docs.zowe.org/stable/user-guide/install-zowe-zos-convenience-build#step-4-copy-the-zoweyaml-configuration-file-to-preferred-location)

for example 

```
cd /u/tmp/zowep
cp example-zowe.yaml /u/tmp/zowec/zowe.yaml
cd /u/tmp/zowec
```

## Basic editing of the zowe.yaml file

### For the MVS systems programmer 

Under Zowe: setup: dataset
| Description | Parameter | Default value |
| ----------- | --------- | -------------|
| Where Zowe MVS data sets will be installed | prefix: |IBMUSER.ZWEV3A |
| PROCLIB where Zowe STCs will be copied over | proclib: |USER.PROCLIB |
| Zowe PARMLIB | parmlib: | IBMUSER.ZWEV3A.CUST.PARMLIB |
|PARMLIB members for plugins |  parmlibMembers: zis | ZWESIP00 |
|JCL library where Zowe will store temporary JCLs during initialization |jcllib: |IBMUSER.ZWEV3A.CUST.JCLLIB |
|Utilities for use by Zowe and extensions|loadlib: |IBMUSER.ZWEV3A.SZWELOAD|
|APF authorized LOADLIB for Zowe|authLoadlib: |IBMUSER.ZWEV3A.SZWEAUTH |
|APF authorized LOADLIB for Zowe ZIS Plugins | authPluginLib: |IBMUSER.ZWEV3A.CUST.ZWESAPL|

Under node:

| Description | Parameter | Default value |
| ----------- | --------- | -------------|
|home: |Path to your node.js home directory |  home: /usr/lpp/IBM/cnj/IBM/node-v20.11.0-os390-s390x-202402131732 |

If you are using the JCL path you need

- the prefix of the ISPF data sets, such as **ISP**.SISPPENU.

### Security

If you want the configuration to generate security parameters 
uncomment the security section


Edit the yaml file and change prefix to your data set prefix

Change the node, for example 

node: 
  home: /usr/lpp/IBM/cnj/IBM/node-v20.11.0-os390-s390x-202402131732 

## Configuration

You can configure Zowe 

-  using JCL provided in the ...SZWESAMP PDS.
See [here](https://docs.zowe.org/stable/user-guide/configuring-zowe-via-jcl).
-  or you can configure Zowe using the Zowe zwe command.  See 
[here](https://docs.zowe.org/stable/user-guide/initialize-zos-system).

But there are additional comments below


### Ccreate the PDS
For full details see the 
[instructions](https://docs.zowe.org/stable/user-guide/zwe-init-subcommand-overview/#initializing-zowe-custom-data-sets-zwe-init-mvs)


The install command uses the yaml file to allocate the data sets.

/u/tmp/zowep/bin/zwe install -c zowe.yaml

This took about a minute to run



### APF authorise the libraries

The APF authorisation step tries to APF authorise an authorised plugin data set, which is not created. In the YAML file there is an entry authPluginLib: with the value IBMUSER.ZWEV3.CUST.ZWESAPL. Change the value, or create the data set.

You can issue the zowe command to update the APF libraries for the current IPL using

/u/tmp/zowep/bin/zwe init apfauth -c zowe.yaml

or you can update your PROGxx member with


    APF ADD 
        DSNAME(IBMUSER.ZWEV3.SZWEAUTH)  SMS 
    APF ADD 
        DSNAME(IBMUSER.ZWEV3.CUST.ZWESAPL) SMS 


and activate it using

T PROG=xx

With this technique the definitions are available across IPLs

## Setup VSAM

This is no longer required.



## Set up security

If you want to use the zwe init security -c ./zowe.yaml --security-dry-run command, you will need to customise the yaml file.

I set up the security through JCL and PDS members.



## Use of APPL profiles

You can restrict which userids can access which APPL profiles.    A common one use OMVSAPPL.  See Controlling access to applications.  I do not know if a different APPL can be used.  It looks like zowe uses OMVSAPPL


## Summary of resources defined

The JCL defines system wide resources

RDEFINE STARTED &ZOWESTC..* - 
RDEFINE STARTED &ZISSTC..* - 
RDEFINE STARTED &AUXSTC..* - 
RDEFINE FACILITY ZWES.IS UACC(NONE) 
RDEFINE FACILITY BPX.DAEMON UACC(NONE) 
RDEFINE FACILITY BPX.SERVER UACC(NONE) 
RDEFINE FACILITY BPX.JOBNAME UACC(NONE) 
RDEFINE UNIXPRIV SUPERUSER.FILESYS UACC(NONE) 
RDEFINE FACILITY IRR.RUSERMAP UACC(NONE) 
RDEFINE FACILITY IRR.IDIDMAP.QUERY UACC(NONE) 
RDEFINE FACILITY IRR.RAUDITX UACC(NONE) 
RDEFINE CDT ZOWE - 
RDEFINE ZOWE APIML.SERVICES UACC(NONE) 

Check you are happy for these to be defined.  See Security Permissions Reference Table for more information.

Submit the JCL

Change the job card and submit it.   Check the output.


## Certificates

zowe has different levels of checks for certificates sent from the client.  See Certificate verification.   Edit the yaml file.

The documentation discusses external key usage.  I do not know how this is configured with RACF and keyrings.

I have an existing keyring with

Server certificate 

The CA for the server certificate

CA for the users who use my server

There is configuration yaml - and run yaml.

Configuration yaml has



My run time yaml has  ( use oedit find cert  3 7 )

 certificate: 
     keystore: 
       type: JCERACFKS 
       file: safkeyring:////IZUSVR/CCPKeyring.IZUDFLT 
       alias: CONN2.IZUDFLT 
     truststore: 
       type: JCERACFKS 
       file: safkeyring:////IZUSVR/CCPKeyring.IZUDFLT 
                                                                                               
 # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
 # How we want to verify SSL certificates of services. Valid values are: 
 # - STRICT:    will validate if the certificate is trusted in our trust store and 
 #              if the certificate Command Name and Subject Alternative Name (SAN) 
 #              is validate. This is recommended for the best security. 
 # - NONSTRICT: will validate if the certificate is trusted in our trust store. 
 #              This mode does not validate certificate Common Name and Subject 
 #              Alternative Name (SAN). 
 # - DISABLED:  disable certificate validation. This is NOT recommended for 
 #              security. 
 verifyCertificates: STRICT 

init MVS

This step copies files into the parmlib and proclib specified files.
You may wish to copy them to a staging data set, for an authorised userid to copy to the system datasets.

zwe init mvs

init STC

Parmlib

ZOWE has its configuration in YAML.   This can be in the ZFS, or can be in a parmlib member.

The ZWESISTC started task needs a parmlib member.  It can point to the member IBMUSER.ZWEV3.SZWESAMP(ZWESIP00), or you can copy it to a PARMLIB concatenation data set.

I copied 3 members from IBMUSER.ZWEV3.SZWESAMP, ZWESASTC, ZWESISTC and
ZWESLSTC.   They are described here.

You need to change the STEPLIB, PARMLIB and CONFIG= statements.

xhttps://docs.zowe.org/stable/appendix/zwe_server_command_reference/zwe/init/zwe-init-mvs/

Configure the yaml file prior to starting

java: 
  # **COMMONLY_CUSTOMIZED** 
  # Path to your Java home directory 
  home: "/usr/lpp/java/J17.0_64" 
node: 
   home: /usr/lpp/IBM/cnj/IBM/node-v20.11.0-os390-s390x-202402131732 
                                                                     
runtimeDirectory: "/u/tmp/zowep/"                                                                                         
logDirectory: /u/tmp/zowec/logs 
                                                                                         
workspaceDirectory: /u/tmp/zowec/workspace 
                                                                                         
extensionDirectory: /u/tmp/zowec/extensions 
useConfigmgr: true 
job: 
  name: CCP1SV 
  prefix: CCP1 
                                                                
rbacProfileIdentifier: "1" 
                                                                
cookieIdentifier: "1" 
                                                                
externalDomains: 
  - 10.1.1.2 
                                                           
                                                                
                                                                
externalPort: 7554 

externalDomains: 
  # this should be the domain name to access Zowe APIML Gateway 
  - 10.1.1.2s
                                                                            

Workload manager

You need to configure Zowe to workload manager

xhttps://www.ibm.com/docs/en/was-liberty/zos?topic=zos-enabling-workload-management-liberty

For the started tasks, and the started tasks started from within ZOWE for example ZWE1

basic definition of the address spaces

-------------------------------------------------


System wide definitions
The install updates parmlib and proclib members.  You can specify Zowe specific which you then copy the members to the system parmlib and proclib at a later date.   The defaults are
proclib: IBMUSER.ZWEV3.CUST.PROCLIB
parmlib: IBMUSER.ZWEV3.CUST.PARMLIB
There is a parmlib member. 
parmlibMembers:
  zis: ZWESIP00
The install create datasets with 
prefix: IBMUSER.ZWEV3

It creates 
jcllib: IBMUSER.ZWEV3.CUST.JCLLIB
loadlib: IBMUSER.ZWEV3.SZWELOAD
authLoadlib: IBMUSER.ZWEV3.SZWEAUTH
authPluginLib: IBMUSER.ZWEV3.CUST.ZWESAPL

Started task
You need two started tasks
…

..

Where do I specify the userid the started tasks run under?


Certificates
You can use an existing keyring and trust store, or you can have the install process create a keyring, CA and server certificate.
Type of keyring…

You can use keyring or a keystore file
directory: /var/zowe/keystore


Where are the instance files stored?

 runtimeDirectory: "/u/tmp/zowep/"
                                                              	 
 logDirectory: /u/tmp/zowec/logs
                                                              	 
 workspaceDirectory: /u/tmp/zowec/workspace
                                                              	 
 extensionDirectory: /u/tmp/zowec/extensions
                                                               	






Zowe planning and installation instructions


You will need the following information before you can install Zowe

Products installed
Java 17
Node/js

How much disk space do you need?

The zowe product libraries use 
The PDS’s need
Each instance  needs.

System wide definitions
The install updates parmlib and proclib members.  You can specify Zowe specific which you then copy the members to the system parmlib and proclib at a later date.   The defaults are
proclib: IBMUSER.ZWEV3.CUST.PROCLIB
parmlib: IBMUSER.ZWEV3.CUST.PARMLIB
There is a parmlib member. 
parmlibMembers:
  zis: ZWESIP00
The install create datasets with 
prefix: IBMUSER.ZWEV3

It creates 
jcllib: IBMUSER.ZWEV3.CUST.JCLLIB
loadlib: IBMUSER.ZWEV3.SZWELOAD
authLoadlib: IBMUSER.ZWEV3.SZWEAUTH
authPluginLib: IBMUSER.ZWEV3.CUST.ZWESAPL

Started task
You need two started tasks
…

..

Where do I specify the userid the started tasks run under?


Certificates
You can use an existing keyring and trust store, or you can have the install process create a keyring, CA and server certificate.
Type of keyring…

You can use keyring or a keystore file
directory: /var/zowe/keystore


Where are the instance files stored?

 runtimeDirectory: "/u/tmp/zowep/"
                                                              	 
 logDirectory: /u/tmp/zowec/logs
                                                              	 
 workspaceDirectory: /u/tmp/zowec/workspace
                                                              	 
 extensionDirectory: /u/tmp/zowec/extensions
