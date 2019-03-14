cparms = -Wno-write-strings 
clibs = -I. -I../inc -I'/usr/include'  -I'/opt/mqm/inc'
lparms = -L /opt/mqm/lib64 -Wl,-rpath=/opt/mqm/lib64 -Wl,-rpath=/usr/lib64 -lmqm 
% : %.c
gcc -m64  $(cparms) $(clibs)   $< -o $@  $(lparms)
