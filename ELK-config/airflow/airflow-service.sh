#!/bin/sh
AIRFLOW_HOME=/home/devuser/monitoring/apache_airflow
PATH=$PATH:$AIRFLOW_HOME
SERVICE_NAME=airflow-service
SERVICE_SUB_NAME=airflow-scheduler-service
export AIRFLOW_HOME

# - Export JAVA_HOME
JAVA_HOME=~/openlogic-openjdk-11.0.23+9-linux-x64
export PATH=$JAVA_HOME/bin:$PATH
export JAVA_HOME

export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

VENV=".venv"
# Python 3.11.7 with Window
if [ -d "$AIRFLOW_HOME/$VENV/bin" ]; then
    source $AIRFLOW_HOME/$VENV/bin/activate
else
    source $AIRFLOW_HOME/$VENV/Scripts/activate
fi

# See how we were called.
case "$1" in
  start)
        # Start daemon.
        echo "Starting $SERVICE_NAME";
        nohup $AIRFLOW_HOME/$VENV/bin/airflow webserver -p 7001 &> /dev/null &
        nohup $AIRFLOW_HOME/$VENV/bin/airflow scheduler &> /dev/null &
        #$AIRFLOW_HOME/$VENV/bin/airflow webserver -p 7001
        #$AIRFLOW_HOME/$VENV/bin/airflow scheduler
        ;;
  stop)
        # Stop daemons.
        echo "Shutting down $SERVICE_NAME";
        pid=`ps ax | grep -i '/airflow webserver' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          kill -9 $pid
         else
          echo "$SERVICE_NAME was not Running"
        fi
        echo "Shutting down $SERVICE_SUB_NAME";
        pid=`ps ax | grep -i '/airflow scheduler' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          kill -9 $pid
         else
          echo "$SERVICE_SUB_NAME was not Running"
        fi
        pkill airflow
        ;;
  restart)
        $0 stop
        sleep 2
        $0 start
        ;;
  status)
        pid=`ps ax | grep -i '/airflow webserver' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          echo "$SERVICE_NAME is Running as PID: $pid"
        else
          echo "$SERVICE_NAME is not Running"
        fi
        pid=`ps ax | grep -i '/airflow scheduler' | grep -v grep | awk '{print $1}'`
        if [ -n "$pid" ]
          then
          echo "$SERVICE_SUB_NAME is Running as PID: $pid"
        else
          echo "$SERVICE_SUB_NAME is not Running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
esac

