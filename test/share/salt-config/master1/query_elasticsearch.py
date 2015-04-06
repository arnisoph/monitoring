#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
foo
"""

from elasticsearch import Elasticsearch
import json
from pprint import pprint
from datetime import datetime, timedelta, tzinfo

es = Elasticsearch(['10.10.10.100:9200'])

#body = {
#        "query": {
#            "filtered": {
#                "query": {
#                    "match": {
#                        "fun": "test.ping"
#                        }
#                    },
#                "filter" : {
#                    "term": {
#                        "minion": "master1.mon.local.arnoldbechtoldt.com"
#                        }
#                    }
#                }
#            }
#}

body = {"query": {"match_all": {}}}

utcnow = datetime.utcnow()
td = timedelta(minutes=10)
time_gte = (utcnow - td).isoformat()
time_lte = "now"

body = {
    "query": {
        "filtered": {
            "query": {"query_string": {"query": "minion:\"master1.mon.local.arnoldbechtoldt.com\"",
                                       "analyze_wildcard": True}},
            "filter": {"bool": {"must": [{"range": {"@timestamp": {"gte": time_gte,
                                                                   "lte": time_lte}}}]}}
        }
    },
    "aggs": {
        "time_range": {
            "date_histogram": {
                "field": "@timestamp",
                "format": "dd.MM.YYYY HH:mm:ss Z z",
                #"ranges": [
                #    { "to": "now-10s/s" },
                #    { "from": "now" },
                #]
                "interval": "120s"
            }
        }
    },
    "size": 10,
    "sort": {"@timestamp": "asc"}
}
#,
#"size": 0 } #,
#    "aggs": {
#        "2": {
#            "date_histogram": {
#                "field": "@timestamp",
#                "interval": "1h",
#                "pre_zone": "+02:00",
#                "pre_zone_adjust_large_interval": True,
#                "min_doc_count": 1,
#                "extended_bounds": {"min": 1428210358438,
#                                    "max": "now"}
#            },
#            "aggs": {
#                "4": {"terms": {"field": "minion",
#                                "size": 5,
#                                "order": {"1": "desc"}},
#                      "aggs": {"1": {"avg": {"field": "data.1-min"}}}}
#            }
#        }
#    }
#}

#body = None
#json_data = open('/vagrant/src/monitoring/config/checks/loadavg.json', 'r+')
#jdata = json.loads(json_data.read().decode("utf-8"))
#
#replace_map = {
#    '{{ 10m_ago }}': '10m ago'
#}

#def replace_vars(obj):
#    new_obj = obj
#    for key, val in new_obj.iteritems():
#        if hasattr(obj[key], '__getitem__'):
#            replace_vars(obj[key])
#
#        for old, new in replace_map.iteritems():
#            if old in val:
#                obj[key] = obj[key].replace(new, old)
#                del obj[key]
#    return obj

#print replace_vars(jdata)

#exit(0)

body = {"query": {"match_all": {}}}
res = es.search(index='monitoring-diskusage', body=body)

#print(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))
#print "===================="

for hit in res['hits']['hits']:
    print(json.dumps(hit, sort_keys=True, indent=4, separators=(',', ': ')))
for hit in res.get('aggregations', {}).iteritems():
    print "w00t"
    print(json.dumps(hit, sort_keys=True, indent=4, separators=(',', ': ')))
print("Got %d Hits" % res['hits']['total'])
