if [ $# -ne 2 ]
then
  echo usage $0 service command
  exit 5
fi
service=$1
command=$2

if [ $service != "elasticsearch" -a $service != "logstash" ]
then
  echo invalid service $service
  exit 5
fi

# systemctl $command $service
sudo service $service $command

