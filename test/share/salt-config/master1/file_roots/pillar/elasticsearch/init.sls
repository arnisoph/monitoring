elasticsearch:
  lookup:
    repo:
      keyurl: salt://elasticsearch/files/GPG-KEY-elasticsearch
    defaults:
      JAVA_HOME: /opt/java/jdk/current/src
      ES_HEAP_SIZE: 512m
    settings:
      cluster:
        name: cluster1
      node:
        name: {{ salt['grains.get']('fqdn') }}
        master: true
        data: true
      index:
        number_of_replicas: 0
      network:
        host: 0.0.0.0
      gateway:
        expected_nodes: 1
      discovery:
        zen:
          ping:
            multicast:
              enabled: false
    plugins:
      - name: lmenezes/elasticsearch-kopf
        installed_name: kopf
#        url: 'https://github.com/lmenezes/elasticsearch-kopf'
      - name: karmi/elasticsearch-paramedic
        installed_name: paramedic
#        url: 'https://github.com/karmi/elasticsearch-paramedic'

java:
  jdk:
    current_ver: 8u20
    versions:
      8u20:
        source: http://fipmb1012.mgmt.systems/share/java/jdk-8u20-linux-x64.tar.gz
        source_hash: md5=ec7f89dc3697b402e2c851d0488f6299
        version: jdk1.8.0_20

sysctl:
  params:
    - name: vm.swappiness
      value: 0
    - name: vm.max_map_count
      value: 262144
