
curl_host="http://localhost:8004/config/get_gloabl_config"

disk_usage_threshold=$(curl -s $curl_host | jq '.config.disk_usage_percentage_threshold')
echo "curl with jq to $curl_host -> disk usage theshold $disk_usage_threshold"


export PYTHONIOENCODING=utf8
disk_usage_threshold_python=$(curl -s $curl_host | \
    python2 -c "import sys, json; print json.load(sys.stdin)['config']['disk_usage_percentage_threshold']")
echo "curl with python2 to $curl_host -> disk usage theshold $disk_usage_threshold_python"

#echo -e "\n"

# return httpo_status_code
response_code=$( curl -s -o /dev/null -w "%{http_code}" $curl_host)
if [[ $response_code -eq 200 ]]; then
    echo "Request successful"
    echo $response_code
else
    echo "Request failed with response code $response_code"
fi

# json
response_code=$( curl -s $curl_host)
echo $response_code



# request

# ---
# Get threshold from ES configuration API service
curl_host="http://localhost:8004/config/get_gloabl_config"

THRESHOLD=$(curl -s $curl_host | jq '.config.disk_usage_percentage_threshold')
if [[ -n "$THRESHOLD" ]]
then
   echo "# Request succesful"
   echo "# ES Configuation API :  $THRESHOLD"
   #echo $THRESHOLD
else
   echo "Request failed"
   echo $curl_host
   # If ES configuration API does not work, manually set the THRESHOLD value to 85%.
   THRESHOLD=85
fi
#--


CURRENT=$(df /apps | grep / | awk '{ print $5}' | sed 's/%//g')
#THRESHOLD=85
echo $CURRENT
if [ "$CURRENT" -gt "$THRESHOLD" ] ; then
   echo here
    mailx -s 'Disk Space Alert' mareiuig@gmail.com << EOF
Your ENV1 localhost ($HOSTNAME) apps partition remaining free space is critically low. Used: $CURRENT%
EOF
fi


