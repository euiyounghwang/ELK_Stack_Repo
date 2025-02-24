# Beat
<i>Beat

Beat

- PacketBeat
    - Packetbeat is a lightweight network packet analyzer that sends data from your hosts and containers to Logstash or Elasticsearch. Network protocols like HTTP let you keep a pulse on application latency and errors, response times, SLA performance, user access patterns and trends, and more. Packetbeat enables you to access this data to understand how traffic is flowing through your network.

- MetricBeat
    - Metricbeat is lightweight shipper for metrics. Collect metrics from your systems and services From CPU to memory, Redis to NGINX, and much more, Metricbeat is a lightweight way to send system and service statistics. Deploy Metricbeat on all your Linux, Windows, and Mac hosts, connect it to Elasticsearch and voila: you get system-level CPU usage, memory, file system, disk IO, and network IO statistic


#### Packet Beat
- PacketBeat : https://www.elastic.co/blog/monitoring-the-search-queries, https://nirsa.tistory.com/262

![alt text](flow.png)
1) Install a Logstash instance to process your monitored packets.
2) Configure Logstash. For this example I chose to only monitor search queries. I created config file called sniff_search.conf with below content; it includes extracting query_body and the index that has been searched into their own fields. 
```bash
input {
  beats {
    port => 5044
  }
}

filter {
   ruby {
        code => "event.set('timestamp', event.get('@timestamp').time.localtime('-04:00').strftime('%Y-%m-%d %H:%M:%S'))"
   }

   geoip {
		  source => "client_ip"
	}

  if [request] {
    if ".kibana" not in [index] {
        if "search" in [request]{
          grok {
            match => { "request" => ".*\n\{(?<query_body>.*)"}
          }
          grok {
            match => { "path" => "\/(?<index>.*)\/_search"}
          }
          if [index] {
          }
          else {
            mutate {
              add_field  => { "index" => "All" }
            }
          }
          mutate {
            gsub => [
                "request", "\n", " ",
                "request", "\s", "",
                "query_body", "\s", "",
                "query_body", "\s", ""
            ]
            update  => { "query_body" => "{%{query_body}" }
          } 
      }
    }
  }
}

output {
  if [request] {
    if ".kibana" not in [index] {
      if "search" in [request] and "ignore_unmapped" not in [query_body]{
        elasticsearch {
          hosts => "localhost:9201"
          index => "%{[@metadata][beat]}-%{+YYYY.MM.dd}"
          user => devuser
          password => 1
          ssl => true
          ssl_certificate_verification => false
        }
        stdout{
          codec => rubydebug
        }
      } 
    }
  }
}
```
3) Start Logstash : Logstash Instance : `/home/biadmin/logstash-5.6.4/bin/logstash -f /home/biadmin/logstash-5.6.4/config/conf.d/` or Kibanan instance : `/home/biadmin/ELK_UPGRADE/logstash-7.13.0/bin/logstash -f /home/biadmin/ELK_UPGRADE/logstash-7.13.0/config/conf.d/`
4) Start sniffing : Install Packetbeat on each host of the production cluster you would like to monitor.
5) Configure packetbeat.yml on each node
- Import Dashboard for packetbeat in Kibana (V.8.12.2 > 6.0) : `./packetbeat setup --dashboards`
```bash

#============================== Network device ================================

# Select the network interface to sniff the data. On Linux, you can use the
# "any" keyword to sniff on all connected interfaces.
#packetbeat.interfaces.device: any

...
packetbeat.protocols.http:
  # Configure the ports where to listen for HTTP traffic. You can disable
  # the HTTP protocol by commenting out the list of ports.
  ports: [80, 8080, 8000, 5000, 8002, 9200]
  send_request: true
  include_body_for: ["application/json", "x-www-form-urlencoded"]

#----------------------------- Logstash output --------------------------------
output.logstash:
  # The Logstash hosts
  hosts: ["localhost:5044"]

  # Optional SSL. By default is off.
  # List of root certificates for HTTPS server verifications
  #ssl.certificate_authorities: ["/etc/pki/root/ca.pem"]

  # Certificate for SSL client authentication
  #ssl.certificate: "/etc/pki/client/cert.pem"

  # Client Certificate Key
  #ssl.key: "/etc/pki/client/cert.key"


#============================== Kibana =====================================
#
setup.kibana:
#
  host: "localhost:5601"

  # Optional protocol and basic auth credentials.
  #protocol: "https"
  username: "biadmin"
  password: "biadmin"
  #
  # Optional HTTP Path
  #path: ""
  # Use SSL settings for HTTPS. Default is true.
  ssl.enabled: true


#  #============================== Dashboards =====================================
# setup.dashboards.enabled: true

[biadmin@localhost packetbeat-8.12.2-linux-x86_64]$ ./packetbeat setup --dashboards
Loading dashboards (Kibana must be running and reachable)
Loaded dashboards
[biadmin@localhost packetbeat-8.12.2-linux-x86_64]$
```
6) Run packetbeat.yml on each node 
- Run command manually : `sudo /apps/packetbeat/packetbeat-5.6.4-linux-x86_64/packetbeat -e -c /apps/packetbeat/packetbeat-5.6.4-linux-x86_64/packetbeat.yml -strict.perms=false "publish"` or `sudo /apps/packetbeat/packetbeat-5.6.4-linux-x86_64/packetbeat -e -c /apps/packetbeat/packetbeat-5.6.4-linux-x86_64/packetbeat.yml -d -strict.perms=false "publish"` as background (Start Packetbeat. For sniffing the packets it must be started as root), 
strict.perms option on this URL (https://dzlab.github.io/2023/04/02/packetbeat-intro/)
- Run Service : `sudo service packetbeat_service start` (./packetbeat-service.sh)/`sudo service packetbeat_service stop`(./packetbeat-log.sh)
-  sudo /apps/packetbeat/packetbeat-5.6.4-linux-x86_64/packetbeat setup -e -E output.logstash.enabled=false -E output.elasticsearch.hosts=['localhost:9201'] -E output.elasticsearch.username=biadmin -E output.elasticsearch.password=biadmin -E setup.kibana.host=localhost:5601 -strict.perms=false
- This is an example of what a document will look like:
```bash
{
     "bytes_in" => 537,
    "client_ip" => "10.255.5.101",
  "client_port" => 52213,
  "client_proc" => "",
"client_server" => "",
           "ip" => "10.255.4.167",
         "port" => 9200,
         "path" => "/logstash-*/_search",
         "beat" => {
     "hostname" => "ip-10-255-4-167.eu-west-1.compute.internal",
         "name" => "ip-10-255-4-167.eu-west-1.compute.internal"
},
         "proc" => "",
       "server" => "",
       "method" => "POST",
         "type" => "http",
       "status" => "OK",
       "params" => "%7B+%22query%22%3A+%7B%0A%22match%22%3A+%7B%0A+++%22clientip%22%3A+%22105.235.130.196%22%0A%7D%0A%7D%7D%0A=",
         "http" => {
              "code" => 200,
    "content_length" => 7587,
            "phrase" => "OK"
},
    "bytes_out" => 7675,
      "request" => "POST /logstash-*/_search HTTP/1.1\r\nHost: 10.255.4.167:9200\r\nConnection: keep-alive\r\nContent-Length: 62\r\nAccept: application/json, text/javascript, */*; q=0.01\r\nOrigin: chrome-extension://lhjgkmllcaadmopgmanpapmpjgmfcfig\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36\r\nContent-Type: application/x-www-form-urlencoded; charset=UTF-8\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: en-US,en;q=0.8\r\n\r\n{ \"query\": {\n\"match\": {\n   \"clientip\": \"105.235.130.196\"\n}\n}}\n",
   "@timestamp" => "2016-08-05T14:35:36.740Z",
        "query" => "POST /logstash-*/_search",
        "count" => 1,
    "direction" => "in",
 "responsetime" => 28,
     "@version" => "1",
         "host" => "ip-10-255-4-167.eu-west-1.compute.internal",
         "tags" => [
             [0] "beats_input_raw_event"
         ],
   "query_body" => "{ \"query\": {\n\"match\": {\n   \"clientip\": \"105.235.130.196\"\n}\n}}\n",
        "index" => "logstash-*"
}
```
- From the data you see the IP and the port of the client connected to Elasticsearch "client_ip": "10.255.5.101" , "client_port": 56433. The IP of the node and port   "ip": "10.255.4.167", "port": 9200,, you can also see the query sent to Elasticsearch "query": "POST /logstash-*/_search",...
- You can visualize this data in Kibana. Connect to Kibana you installed in step 2 and configure an index pattern of Logstash-*