#!/usr/bin/env python
'''
foo
'''

import elasticsearch
import json
from pprint import pprint

es = elasticsearch.Elasticsearch(['10.10.10.100:9200'])

body = {
        "query": {
            "filtered": {
                "query": {
                    "match": {
                        "_type": "ssh.host_keys"
                        }
                    },
                "filter" : {
                    "term": {
                        "id": "client1.mon.local.arnoldbechtoldt.com"
                        }
                    }
                }
            }
}

res = es.search(index='salt', body=body)

for hit in res['hits']['hits']:
    print(json.dumps(hit, sort_keys=True, indent=4, separators=(',', ': ')))
print("Got %d Hits" % res['hits']['total'])
