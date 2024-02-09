# Monitoring
Monitoring Solutions

Prometheus Installation <br>
https://prometheus.io/docs/prometheus/latest/installation/

###### Create a network for prometheus and grafana containers to network

docker network create -d bridge prometheus-grafana

docker volume create prometheus-data

docker run \ <br>
    -p 9090:9090 \ <br>
    --name=prometheus \ <br>
    --network=prometheus-grafana \ <br>
    -v /home/ubuntu/prometheusdev:/etc/prometheus \ <br>
    -v prometheus-data:/prometheus \ <br>
    prom/prometheus

docker volume create grafana-storage

docker volume inspect grafana-storage
    
docker run -d -p 3000:3000 --name=grafana --network=prometheus-grafana grafana/grafana-enterprise

docker run -d -p 3000:3000 --name=grafana \ <br>
  --volume "$PWD/grafana:/var/lib/grafana" \ <br>
  grafana/grafana-enterprise

###### For Multiple Targets or Environments Scraping from a single prometheus config file

scrape_configs: <br>
  - job_name: "zookeeper" <br>
    static_configs: <br>
      - targets: <br>
          - "zookeeper-0.dev:8079" <br>
        labels: <br>
          env: "dev" <br>
      - targets: <br>
          - "zookeeper-0.beta:8079" <br>
        labels: <br>
          env: "beta" <br>
    relabel_configs: <br>
      - source_labels: [__address__] <br>
        target_label: instance <br>
        regex: '([^:]+)(:[0-9]+)?' <br>
        replacement: '${1}' <br>

  - job_name: "kafka-broker" <br>
    static_configs: <br>
      - targets: <br>
          - "kafka-0.dev:8080" <br>
        labels: <br>
          env: "dev" <br>
      - targets: <br>
          - "kafka-0.beta:8080" <br>
        labels: <br>
          env: "beta" <br>
    relabel_configs: <br>
      - source_labels: [__address__] <br>
        target_label: instance <br>
        regex: '([^:]+)(:[0-9]+)?' <br>
        replacement: '${1}' <br>

  ###### For Single Target or Environments Scraping from a single prometheus config file      
  
 scrape_configs: <br>
  - job_name: "zookeeper" <br>
    static_configs: <br>
      - targets: <br>
          - "zookeeper-0.beta:8079" <br>
        labels: <br>
          env: "beta" <br>
    relabel_configs: <br>
      - source_labels: [__address__] <br>
        target_label: instance <br>
        regex: '([^:]+)(:[0-9]+)?' <br>
        replacement: '${1}' <br>

  - job_name: "kafka-broker" <br>
    static_configs: <br>
      - targets: <br>
          - "kafka-0.beta:8080" <br>
        labels: <br>
          env: "beta" <br>
    relabel_configs: <br>
      - source_labels: [__address__] <br>
        target_label: instance <br>
        regex: '([^:]+)(:[0-9]+)?' <br>
        replacement: '${1}' <br>

  Refs: https://github.com/confluentinc/jmx-monitoring-stacks/tree/main/jmxexporter-prometheus-grafana/cp-ansible
  
