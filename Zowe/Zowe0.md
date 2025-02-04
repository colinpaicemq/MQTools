# Introduction to Zowe

## What is Zowe used for?

 The Zowe server runs on z/OS and allows people to work with z/OS without using the traditional ISPF interface.  They can use
 
 -  a Zowe command interface from within and OMVS session,
 -  a browser,
 -  vscode IDE,
 -  a REST API,

 ## What is Zowe?

 Zowe is implemented as a collection of started tasks running Java programs, including, for example, a web-server.

 If you connect to z/OS through Zowe, it provides the same facilities as if you had logged on through a 3270.

 Information about users is not stored in Zowe.   If you have multiple LPARs running Zowe, you can access z/OS through any of the Zowe instances. !Is this true?!

 Zowe has a High Availablity option which does !??!

 Zowe has some PDS containing sample JCL and load modules, and a directory in Unix Services.    This can be shared read/only between LPARS in a sysplex.
 
 Each Zowe instance has a directory in Unix Services which contains configuration information, and logs and traces.

 A Zowe instance can be started on a different LPAR if the instance's directory is available on the different LPAR.  This may mean a shared directory, or remounting the directories file system.

 Once you connect to a Zowe instance, your traffic goes to that instance until you logoff.

 If you logon again a network load balancer may route you to a different Zowe instance on the LPAR.

 Connection to Zowe is done over TLS connections, either TLS 1.2 or TLS 1.3.

 The server will send a certificate, and the traffic will be encrypted.   You can configure Zowe to request the client send up it's certificate, and Zowe can authenticate the client's certificate.

 You can use use the z/OS security manager to map a client's certicate to a userid.   You can use different criteria, such as Certificate's Distinguished Name and issuer, to map an input certificate to a userid. 

 You can use existing keystore keyrings, and truststore keyrings, or have your certificates in .pem files in a  file system (use of .pem files is not recommended).  During configuration you can choose to have the installation create a Certicate Authority key, a keyring, and a key for the server.

 Authentication to Zowe, and thus to z/OS can be done with 
 
 -  userid and password and the SAF
 -  ?   Using z/OSMF.
 -  Zss - whatever this is
 -  Multi Factor Authentication (MFA)

 There are multiple started tasks for Zowe.  These communicate with each other over TLS connections, so the certificate key used by the address space, can be used as both a server key, and as a client key to another started task.

 Zowe configuration is done using [.YAML]() files.
 
 The Zowe product code can be shared across LPARs in a Sysplex.
 If you want to be able to start a Zowe instance on any LPAR in the sysplex the instance files need to be on a file system which is read/write on all systems.





