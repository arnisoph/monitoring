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
                        "_type": "pkg.install"
                        }
                    },
                "filter" : {
                    "term": {
                        "id": "master1.mon.local.arnoldbechtoldt.com"
                        }
                    }
                }
            }
}

body = {
    "query": {
        "match_all": {}
        }
    }


res = es.search(index='salt-test_ping', body=body)

for hit in res['hits']['hits']:
    print(json.dumps(hit, sort_keys=True, indent=4, separators=(',', ': ')))
print("Got %d Hits" % res['hits']['total'])
