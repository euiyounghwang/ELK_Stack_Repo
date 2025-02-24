#!/bin/bash
set -e

JAVA_HOME='/home/biadmin/monitoring/openlogic-openjdk-8u412-b08-linux-x64'
PATH=$PATH:$JAVA_HOME/bin
export JAVA_HOME

#export JAVA_OPTS="$JAVA_OPTS -XX:+IgnoreUnrecognizedVMOptions"
#export JAVA_OPTS="$JAVA_OPTS -XX:+UseG1GC"

echo $JAVA_HOME
java -version

#/home/biadmin/ELK_UPGRADE/logstash-8.12.0/bin/logstash -f /home/biadmin/ELK_UPGRADE/logstash-8.12.0/ingest.conf
/home/biadmin/ELK_UPGRADE/logstash-7.13.0/bin/logstash -f /home/biadmin/ELK_UPGRADE/logstash-7.13.0/conf/conf.d/

