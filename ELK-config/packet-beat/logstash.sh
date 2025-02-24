
#!/bin/sh

JAVA_HOME=~/openlogic-openjdk-8u402-b06-linux-x64

LOGSTASH_EXPORT_PATH=/home/biadmin/logstash-5.6.4/
PATH=$PATH:$LOGSTASH_EXPORT_PATH/bin
PATH=$PATH:$JAVA_HOME/bin
SERVICE_NAME=logstash-service

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        nohup $LOGSTASH_EXPORT_PATH/bin/logstash -f  $LOGSTASH_EXPORT_PATH/conf.d/ &> /dev/null &
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/logstash' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          kill -9 $pid
         else
          echo "$SERVICE_NAME was not Running"
        fi
        ;;
  restart)
        $0 stop
        sleep 2
        $0 start
        ;;
  status)
        pid=`ps ax | grep -i '/logstash' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          echo "$SERVICE_NAME is Running as PID: $pid"
        else
          echo "$SERVICE_NAME is not Running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac
