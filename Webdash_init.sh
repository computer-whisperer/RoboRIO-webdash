#!/bin/sh
# Copyright (c) 2014 National Instruments.
# All rights reserved.

# runFRCNetComm is a function that restarts FRCNetComm if it crashes
runFRCNetComm() {
  while true
  do
    /bin/su - -- lvuser -l -c /usr/local/frc/bin/FRC_NetCommDaemon &
    echo $! > $PID_FRCNETCOMM
         wait $!
  done
}

case "$1" in
  start)
    if [ -e $PID_RUNFRCNETCOMM -a -e /proc/`cat $PID_RUNFRCNETCOMM 2> /dev/null` ]; then
      echo "$0 already started"
      exit 1
    fi

    touch $PID_RUNFRCNETCOMM
    chmod +r $PID_RUNFRCNETCOMM

    touch $PID_FRCNETCOMM
    # we need user lvuser to write its PID
    chown lvuser $PID_FRCNETCOMM
    chmod +r $PID_FRCNETCOMM

    runFRCNetComm &
    # save  runFRCNetComm process PID to /var/run
    echo $! > $PID_RUNFRCNETCOMM
    ;;
  stop)
    # kill saved PID for runFRCNetComm process
    if [[ -f "$PID_RUNFRCNETCOMM" ]]; then
      kill `cat $PID_RUNFRCNETCOMM`
      rm $PID_RUNFRCNETCOMM
    fi

    # kill saved PID for FRCNetComm process
    if [[ -f "$PID_FRCNETCOMM" ]]; then
      kill `cat $PID_FRCNETCOMM`
      rm $PID_FRCNETCOMM
    fi
    ;;
