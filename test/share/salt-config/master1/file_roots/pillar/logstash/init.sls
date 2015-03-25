logstash:
  lookup:
    defaults:
    #  JAVA_HOME: /usr/lib/jvm/java-7-openjdk-amd64/jre/
      JAVACMD: /usr/bin/java
      LS_CONF_DIR: /etc/logstash/conf.d
      LS_GROUP: adm
      LS_HEAP_SIZE: 500m
      LS_HOME: /var/lib/logstash
      LS_JAVA_OPTS: '-Djava.io.tmpdir=${LS_HOME}'
      LS_LOG_FILE: /var/log/logstash/logstash.log
      LS_NICE: 19
      LS_OPEN_FILES: 16384
      LS_OPTS: ''
      LS_PIDFILE: /var/run/logstash.pid
      LS_USE_GC_LOGGING: 'true'
      LS_USER: logstash
    #plugins:
    #  - name: contrib
    #    installed_name: 'logstash-contrib-*'
    config:
      manage:
        - defaults_file
        - comp_test_file
        #- es_to_es
      es_to_es:
        contents: |
          input {
            elasticsearch {
              host => "10.10.10.100"
              index => "mydata-2018.09.*"
              query => "*"
              size => 500
              scroll => "5m"
              docinfo => true
            }
          }
          #output {
          #  elasticsearch {
          #    index => "copy-of-production.%{[@metadata][_index]}"
          #    index_type => "%{[@metadata][_type]}"
          #    document_id => "%{[@metadata][_id]}"
          #  }
          #}
          output {
            file {
              path => "/tmp/logstash-es_to_es-%{+YYYY-MM-dd}.log"
            }
          }
      comp_test_file:
        contents: |
          input {
            file {
              type => "syslog"
              path => [ "/var/log/messages", "/var/log/syslog", "/var/log/*.log" ]
            }
          }

          output {
            file {
              path => "/tmp/logstash-output-%{+YYYY-MM-dd}.log"
            }
          }


{# https://github.com/bechtoldt/saltstack-repos-formula #}
repos:
  lookup:
    repos:
      logstash:
        url: http://packages.elasticsearch.org/logstash/1.5/debian
        dist: stable
        comps:
          - main
        keyurl: http://packages.elasticsearch.org/GPG-KEY-elasticsearch
