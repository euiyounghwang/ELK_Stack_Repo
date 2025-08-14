#PID=$(ps -ef | grep kibana | grep -v grep)
#test=$?
#if [ $test -eq 0 ]
#then
#  PID=$(ps -ef | grep kibana | grep -v grep | tr -s ' ' | cut -d " " -f2)
#  echo Killing $PID
#  kill -9 $PID
#fi

service_name='/apps/kibana/latest/bin/'

PID=$(ps -ef | grep $service_name | grep -v grep)
test=$?
if [ $test -eq 0 ]
then
  PID=$(ps -ef | grep $service_name | grep -v grep | tr -s ' ' | cut -d " " -f2)
  echo Killing $PID
  kill -9 $PID
else
  echo Kibana is not Running..
fi

