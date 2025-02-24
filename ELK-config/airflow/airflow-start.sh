#!/bin/sh
AIRFLOW_HOME=/home/devuser/monitoring/apache_airflow
PATH=$PATH:$AIRFLOW_HOME
SERVICE_NAME=airflow-service
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

# --
# Apache Airflow (or simply Airflow) is a platform to programmatically author, schedule, and monitor workflows.
# The advantage of using Airflow over other workflow management tools is that Airflow allows you to schedule and monitor workflows
# --

# airflow dags list
nohup $AIRFLOW_HOME/$VENV/bin/airflow webserver -p 7001 &> /dev/null &
nohup $AIRFLOW_HOME/$VENV/bin/airflow scheduler &> /dev/null &
