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

See [here](https://docs.zowe.org/stable/appendix/zowe-yaml-configuration/#domain-and-port-to-access-zowe) for the contents of the zowe.yaml file.

The parameters below are one which are commonly customised, or you need to know about 
to be able to customise an instance.

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

Specify the location of the node.js support.

| Description | Parameter | Default value |
| ----------- | --------- | -------------|
|Path to your node.js home directory |home:|/usr/lpp/IBM/cnj/IBM/node-v20.11.0-os390-s390x-202402131732 |

Specify the location of Java 

| Description | Parameter | Default value |
| ----------- | --------- | -------------|
|Path to your node.js home directory |home: |/usr/lpp/java/J17.0_64/|

If you are using the JCL path you will need

- the prefix of the ISPF data sets, such as **ISP**.SISPPENU.


Location of the files in the file system.

The /global/ file system is commonly used as read/write across all LPARS in a sysplex.
Other file systems may only be local to the LPAR, and so cannot be used on a different LPAR.

Zowe allows server extensions to expand Zowe core functionalities. The extensions are required to be installed in a central location so Zowe runtime can find and recognize them.  These are stored in the extensionDirectory location.

These are under the zowe. element

| Description | Parameter | Default value |
| ----------- | --------- | -------------|
| where zowe is installed|runtimeDirectory:| "" |
| instance logs are stored|logDirectory: |/global/zowe/logs|
| instance configuration |workspaceDirectory: /global/zowe/workspace |
|Where extension are stored|extensionDirectory: |/global/zowe/extensions|

You will need to specify runtimeDirectory because there is no default value.

### Security

If you want the configuration to generate security parameters 
uncomment the security section.

You can create your own definitons without use the Zowe provided facilities.

These parameters are configured under zowe.security

| Description | Parameter | Default value |
| ----------- | --------- | -------------|
| Which security product |poduct: |RACF |
|Group name for Zowe admin user |groups:admin:| ZWEADMIN |
|Group name for Zowe STC userid |groups:stc:| ZWEADMIN |
|Group name for Zowe SysProgr group |groups:sysProg| ZWEADMIN |
|Runtime userid of main service|users:zowe|ZWESVUSR |
|Runtime userid of ZIS service|users:zowe|ZWESIUSR  |
|Started task names main task|stcs:zowe|ZWESLSTC |
|Started task names zis server |stcs:zis|ZWESISTC |
|Started task names zis Auxilary Server|stcs:zowe|ZWESASTC |


## Configuration

You can configure Zowe 

-  using JCL provided in the ...SZWESAMP PDS.
See [here](https://docs.zowe.org/stable/user-guide/configuring-zowe-via-jcl).
-  or you can configure Zowe using the Zowe zwe command.  See 
[here](https://docs.zowe.org/stable/user-guide/initialize-zos-system).

But there are additional comments below


### Create the PDS
For full details see the 
[instructions](https://docs.zowe.org/stable/user-guide/zwe-init-subcommand-overview/#initializing-zowe-custom-data-sets-zwe-init-mvs)


The install command uses the yaml file to allocate the data sets.

/u/tmp/zowep/bin/zwe install -c zowe.yaml

This took about a minute to run.


### APF authorise the libraries

The Zowe facilities issue commands to the console to dynamically APF authorised 
data sets for the duration of the current IPL.   Your userid may not be authorised to 
issued console command, and any attempt may be automatically cancelled.

For the APF library definitions to be available on all LPARs and to persist across IPLS you will need to update a PROGxx member in the PARMLIB concatentation.


    APF ADD 
        DSNAME(IBMUSER.ZWEV3.SZWEAUTH)  SMS 
    APF ADD 
        DSNAME(IBMUSER.ZWEV3.CUST.ZWESAPL) SMS 


and activate it using

T PROG=xx

Using the command line interface 

    /u/tmp/zowep/bin/zwe init apfauth -c zowe.yaml

or submitting member ZWEIAPF from the "JCL" approach, may fail if you are not authorised.

## Set up parmlib

The ZWESISTC cross memory server address space reads it parameters from an input file.

You can specify in the JCL a DDNAME of PARMLIB.  When the address space starts is 
reads member ZWESIP&MEM from this data set.

If the DDNAME of PARMLIB is not present, it locates the member in the system PARMLIB
defition.

You are unlikely to change this parmlib member.



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

- Server certificate 
- The CA for the server certificate
- CA for the users who use my server

There is configuration yaml - and run yaml.

  - 10.1.1.2 
                                                           
                                                                      

## Workload manager

You need to configure Zowe to workload manager

