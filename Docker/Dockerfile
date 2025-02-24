
# Build Elasticsearch 7 image
FROM docker.elastic.co/elasticsearch/elasticsearch:5.6.4 as omni_es

ARG DEBIAN_FRONTEND=noninteractive

# RUN elasticsearch-plugin install analysis-stempel
# RUN elasticsearch-plugin install analysis-ukrainian
# RUN elasticsearch-plugin install analysis-smartcn
# RUN elasticsearch-plugin install analysis-phonetic
# RUN elasticsearch-plugin install analysis-icu

EXPOSE 9201


FROM docker.elastic.co/kibana/kibana:5.6.4 as omni_kibana
# RUN bin/kibana-plugin remove x-pack
# COPY config/kibana.yml /usr/share/kibana/config/kibana.yml
EXPOSE 5601