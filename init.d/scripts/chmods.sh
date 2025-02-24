if [ $# -ne 1 ]
then
  echo usage $0 service
  echo "server = e|l|k|i"
  exit 5
fi
service=$1

if [ "$service" = "e" ]
then
  chown -R elasticsearch:elasticsearch /apps/elasticsearch
  chown -R elasticsearch:elasticsearch /apps/java
  chown -R elasticsearch:elasticsearch /apps/UtilityScripts
  chmod -R ug=rwX,o=rX /apps
fi


if [ "$service" = "l" ]
then
  chown -R logstash:logstash /apps/logstash
  chown -R logstash:logstash /apps/java
  chmod -R ug=rwX,o=rX /apps
fi

if  [ "$service" = "k" ]
then
  group=middleware
  chown -R kafka:${group} /apps/kafka
  chown -R kafka:${group} /apps/java
  chown -R kafka:${group} /apps/UtilityScripts
  chown -R kafka:${group} /apps/opt
  chown -R biadmin:${group} /apps/var
  chown -R biadmin:${group} /apps/utils
  chown -R spark:${group} /apps/spark
  chown -R kafka:${group} /apps/data
  chmod -R ug=rwX,o=rX /apps
fi

if  [ "$service" = "i" ]
then
  chown -R kibana:kibana /apps/kibana
  chmod -R ug=rwX,o=rX /apps
fi

chmod -R g-w,o-rwx /apps/scripts
