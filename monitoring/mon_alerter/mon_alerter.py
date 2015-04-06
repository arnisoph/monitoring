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


class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return timedelta(0)


utc = UTC()

utcnow = datetime.now(utc)
td = timedelta(minutes=6)
time_gte = (utcnow - td).isoformat()
time_lte = 'now'

body = {
    "query": {
        "filtered": {
            "query": {"query_string": {"query": "*",
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
    "size": 30,
    "sort": {"@timestamp": "asc"}
}

res = es.search(index='monitoring-sysloadavg-*', body=body)

for hit in res['hits']['hits']:
    print(json.dumps(hit, sort_keys=True, indent=4, separators=(',', ': ')))
for hit in res.get('aggregations', {}).iteritems():
    print "w00t"
    print(json.dumps(hit, sort_keys=True, indent=4, separators=(',', ': ')))
print("Got %d Hits" % res['hits']['total'])
