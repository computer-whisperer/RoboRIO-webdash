#!/bin/bash
#
# Webdashscp         Start up myservice
#
# chkconfig: 2345 55 25
# description: This's the description
#
# processname: myservice
 
# Source function library
. /etc/init.d/functions
 
#the service name, a python script
SNAME=webdash
 
#the full path and name of the daemon program
#Warning: The name of executable file must be identical with service name
PROG=/usr/local/bin/$SNAME
 
 
# start function
start() {
    #check the daemon status first
    if [ -f /var/lock/subsys/$SNAME ]
    then
        echo "$SNAME is already started!"
        exit 0;
    else
        echo $"Starting $SNAME ..."
        $PROG &
        [ $? -eq 0 ] && touch /var/lock/subsys/$SNAME
        echo $"$SNAME started."
        exit 0;
    fi
}
 
#stop function
stop() {
    echo "Stopping $SNAME ..."
    pid=`ps -ef | grep $PROG | grep -v -m 1 "grep" |  awk '{ print $1 }'`
    [ "$pid"X != "X" ] && kill $pid
    rm -rf /var/lock/subsys/$SNAME
}
 
case "$1" in
start)
  start
  ;;
stop)
  stop
  ;;
reload|restart)
  stop
  start
  ;;
status)
  pid=`ps -ef | grep $PROG | grep -v -m 1 "grep" | awk '{ print $1 }'`
  if [ "$pid"X = "X" ]; then
      echo "$SNAME is stopped."
  else
      echo "$SNAME (pid $pid) is running..."
  fi
  ;;
*)
  echo $"\nUsage: $0 {start|stop|restart|status}"
  exit 1
esac