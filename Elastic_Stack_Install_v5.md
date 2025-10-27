# ELK Setup with v5.
<i>ELK Setup in local environment

## OS Command
- cat /etc/redhat-release

## Elasticsearch (Elasticsearch v5)
- Elasticsearch is a distributed, RESTful search and analytics engine that allows you to store, search, and analyze large volumes of data in near-real-time. Built on Apache Lucene, it processes both structured and unstructured data, powering use cases like full-text search, business analytics, observability, and security intelligence.
- Elasticsearch performance can be heavily penalised if the node is allowed to swap memory to disk. Elasticsearch can be configured to automatically prevent memory swapping on its host machine by adding the bootstrap memory_lock true setting to elasticsearch.yml. If bootstrap checks are enabled,
bootstrap.memory_lock: true
  - You can check whether the setting has worked by running: GET _nodes?filter_path=**.mlockall
  - Turn off all swapping on Linux option 1: sudo swapoff -a
  - https://devhosaga.tistory.com/entry/Elasticsearch-OS-%ED%99%98%EA%B2%BD-%EC%84%A4%EC%A0%95 (sudo sysctl vm.swappiness=1)
- OS Release : https://www.elastic.co/support/matrix#matrix_os
- __Installation Commands__
  - sudo groupadd elasticsearch
  - sudo useradd -g elasticsearch elasticsearch
  - sudo sysctl -w vm.max_map_count=262144
  - cd /apps
  - sudo mkdir elasticsearch
  - sudo mkdir java
  - sudo mkdir scripts
  - sudo chmod 775 -R ./elasticsearch
  - sudo chmod 775 -R ./java
  - sudo mv ./scripts/ ./scripts_bk
  - sudo chmod 755 -R ./scripts
  - sudo chown -R root:biadmin ./scripts
  - sudo su -l elasticsearch
  - cd /apps
  - cd /apps/elasticsearch
  - scp -r devuser@localhost:/apps/storage/ELK_UPGRADE/setup/elasticsearch-5.6.4.tar.gz .
  - tar -zxvf ./elasticsearch-5.6.4.tar.gz
  - ln -s elasticsearch-5.6.4 latest
  - mkdir data
  - mkdir logs
  - cd /apps/elasticsearch/elasticsearch-8.17.0/config
  - mv ./elasticsearch.yml ./elasticsearch_bk.yml
  - scp -r devuser@localhost:/apps/storage/ELK_UPGRADE/setup/elasticsearch.yml .
  - vi .elasticsearch.yml
  - vi ./jvm.options
  ```bash
  # Xms represents the initial size of total heap space
  # Xmx represents the maximum size of total heap space
  -Xms15g
  -Xmx15g
  ```
  - ** Run 
  - export JAVA_HOME='/apps/java/latest'
  - /apps/elasticsearch/latest/bin/elasticsearch 
  - **
  - exit
  - cd /apps
  - sudo chmod 775 -R ./elasticsearch
  - sudo scp -r devuser@localhost:/apps/storage/ELK_UPGRADE/setup/elasticsearch /etc/init.d/
  - sudo cp ./elasticsearch /etc/init.d/
  - sudo /apps/scripts/systemctl.sh elasticsearch status
  - sudo service elasticsearch status
  - sudo service elasticsearch stop
  - sudo service elasticsearch start


## Kibana (Kibana v5)
- Kibana is a visual interface tool that allows you to explore, visualize, and build a dashboard over the log data massed in Elasticsearch Clusters.
- __Installation Commands (Simple Setup)__
  - sudo groupadd kibana
  - sudo useradd -g kibana kibana
  - sudo mkdir ./kibana
  - sudo chown -R kibana:kibana ./kibana/
  - sudo su -l kibana
  - cd /apps/kibana
  - scp -r devuser@localhost:/apps/storage/ELK_UPGRADE/setup/kibana-5.6.0-linux-x86_64.tar.gz .
  - tar -zxvf kibana-5.6.0-linux-x86_64.tar.gz
  - ln -s  kibana-5.6.0-linux-x86_64 latest
  - cd /apps/kibana/kibana-5.6.4-linux-x86_64/config
  - scp -r devuser@localhost:/apps/storage/ELK_UPGRADE/setup/kibana.yml .
  - /apps/kibana/latest/bin/kibana  (sudo /apps/kibana/latest/bin/kibana &)
  - exit
  - cd /apps
  - sudo chmod 775 -R ./kibana
  - sudo -u kibana /apps/scripts/startkibana
  - sudo /apps/scripts/killps.sh
  - sudo netstat -nlp | grep :5601 
  

## Logstash (Logstash v5)
- Logstash is an open-source data processing pipeline that collects data from various sources, transforms it on the fly, and sends it to a desired destination. As part of the Elastic Stack (formerly ELK stack), it functions as an ETL (Extract, Transform, Load) tool, using a pipeline of input, filter, and output plugins to ingest, structure, and ship logs and events for analysis and visualization in Elasticsearch and Kibana.  
- __Installation Commands__
  - sudo groupadd logstash
  - sudo useradd -g logstash logstash
  - cd /apps
  - sudo mkdir logstash
  - sudo chown -R logstash:logstash ./logstash/
  - sudo chmod 775 -R ./logstash/
  - sudo su -l logstash
  - cd logstash
  - scp -r devuser@localhost:/apps/storage/ELK_UPGRADE/setup/logstash-5.6.4.tar.gz .
  - tar -zxvf logstash-5.6.4.tar.gz
  - ln -s ./logstash-5.6.4 latest
  - cd /apps/logstash
  - mkdir data
  - mkdir logs
  - cd ./latest
  - mkdir tmp
  - cd config
  - mkdir ./conf.d
  - vi ./ingest_socket.conf
  ```bash
  input
  {
      tcp
          {
              type => "TCP_LOG"
              port => 5044
              codec => json
          }

      udp
          {
              type => "UDP_LOG"
              port => 5046
              codec => json
          }

  }


  filter
  {
    ruby {
          #code => "event.set('@timestamp', event.get('@timestamp').time.localtime('-04:00').strftime('%Y-%m-%d %H:%M:%S'))"
          code => "event.set('@timestamp', LogStash::Timestamp.new(Time.parse(event.get('@timestamp').time.localtime('-04:00').strftime('%Y-%m-%d %H:%M:%S'))))"
    }
  }

  output {
    if 'TCP_LOG' in [type] {
      elasticsearch {
          hosts => ["localhost1:9200","localhost2:9200","localhost3:9200"]
          #user => es_logstash
          #password => "test"
          #ssl => true
          #ssl_certificate_verification => false
          #index => "logstash-%{+YYYY.MM.dd}"
          #cacert => "/etc/logstash/root-ca.pem"
        }
      }
      stdout{
        codec => rubydebug
      }
    }
  }
  ```

  - vi /apps/logstash/latest/config/logstash.yml
  ```bash
    pipeline.ecs_compatibility: disabled
      
    # ------------ Data path ------------------
    #
    # Which directory should be used by logstash and its plugins
    # for any persistent needs. Defaults to LOGSTASH_HOME/data
    #
    path.data: /apps/logstash/data/
    #
    # ------------ Pipeline Configuration Settings --------------
    #
    # Where to fetch the pipeline configuration for the main pipeline
    #
    path.config: /apps/logstash/latest/config/conf.d/
    #
    # log.format.json.fix_duplicate_message_fields: false
    #
    path.logs: /apps/logstash/logs/
    #
    # ------------ Other Settings --------------
    ```
  - ** Run 
  - export JAVA_HOME='/apps/java/latest'
  - /apps/logstash/bin/logstash 
  - **
  - exit
  - sudo chmod 775 -R ./logstash/
  - sudo scp -r devuser@localhost:/apps/storage/ELK_UPGRADE/elk_stack_upgrade_script_latest/scripts/* .
  - sudo cp -r ./logstash /etc/init.d/
  - sudo service logstash status
  - sudo service logstash stop
  - sudo service logstash start


## Java (Redhat OpenJDK Download)
- https://developers.redhat.com/products/openjdk/download, https://www.openlogic.com/openjdk-downloads
- __Installation Commands__
  - cd /apps
  - sudo mkdir java
  - sudo chmod 775 ./java/
  - sudo chown -R root: root./java/
  - sudo su -l logstash
  - sudo tar -xvf ./openlogic-openjdk-8u442-b06-linux-x64.tar.gz 
  - sudo ln -s openlogic-openjdk-8u442-b06-linux-x64 latest


## Elastic Stack Migration Scripts with v8.17.0 (Python Script)
- Create index all to new cluster: `python ./upgrade-script/migrate-index-script.py --es http://localhost:9200 --ts https://localhost1:9200`
