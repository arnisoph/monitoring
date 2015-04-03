elasticsearch:
  lookup:
    index_templates:
      salt_defaults:
        #ensure: absent
        config:
          template: salt-*
          order: 10
          settings:
            number_of_shards: 1
          mappings:
            2014_7_a:
              _all:
                enabled: False
              properties:
                '@timestamp':
                  type: date
                success:
                  type: boolean
                retcode:
                  type: short
                minion:
                  type: string
                  index: not_analyzed
                fun:
                  type: string
                  index: not_analyzed
                jid:
                  type: string
                  index: not_analyzed
      salt-test_ping:
        #ensure: absent
        config:
          template: salt-test_ping-*
          order: 100
          mappings:
            2014_7_a:
              properties:
                return:
                  type: boolean
