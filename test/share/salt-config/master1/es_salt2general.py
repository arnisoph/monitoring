#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
foo
'''

import elasticsearch
from elasticsearch.helpers import bulk
import json
from pprint import pprint
from datetime import datetime, timedelta, tzinfo

es = elasticsearch.Elasticsearch(['10.10.10.100:9200'])


class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return timedelta(0)


utc = UTC()

indices = [{'salt_index': 'salt-status_loadavg',
            'common_index': 'monitoring-sysloadavg', },
           {'salt_index': 'salt-test_ping',
            'common_index': 'monitoring-saltping', },
           {'salt_index': 'salt-diskarbe_usage',
            'common_index': 'monitoring-diskusage', }, ]

for index in indices:
    common_index_prefix = 'monitoring-'
    common_index_suffix = '-{0}'.format(datetime.utcnow().strftime('%Y-%m-%d'))
    index_salt = index['salt_index']
    index_common = index.get('common_index')
    index_full = '{0}{1}'.format(index_common, common_index_suffix)
    index_definition = {}

    index_exists = es.indices.exists(index_common)
    if not index_exists:
        es.indices.create(index=index_full, body=index_definition)
        es.indices.put_alias(index=index_full, name=index_common)

    body = {'query': {'match_all': {}}, 'size': 1, 'sort': {'@timestamp': 'desc'}}
    res = es.search(index=index_common, body=body)
    #print(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))

    newest_doc_time = datetime(year=1970, month=1, day=1, microsecond=1, tzinfo=utc).isoformat()
    print 'found {0} in {1}'.format(res['hits']['total'], index_common)
    if res['hits']['total'] > 0:
        newest_doc_time = res['hits']['hits'][0]['_source']['@timestamp']

    print 'newest doc in {0} has ts {1}'.format(index_common, newest_doc_time)
    time_gte = newest_doc_time
    time_lte = 'now'

    from_offset = 0
    docs_size = 10
    docs_index_old = []
    replace_key_seqs = {'-': '_', }
    while True:
        body = {
            "query": {
                "filtered": {
                    "query": {"query_string": {"query": "*",
                                               "analyze_wildcard": True}},
                    "filter": {
                        "bool": {
                            "must": [{"range": {"@timestamp": {"gte": time_gte,
                                                               "lte": time_lte}}}],
                            'must_not': [{'term': {'@timestamp': time_gte, }}]
                        }
                    }
                }
            },
            'from': from_offset,
            "size": docs_size,
            "sort": {"@timestamp": "asc"}
        }
        res = es.search(index=index_salt, body=body)
        #print(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))
        docs_index_old += res['hits']['hits']
        from_offset += docs_size
        print 'total {0} - step {1}'.format(res['hits']['total'], from_offset)
        if res['hits']['total'] - from_offset <= 0:
            break

    bulk_actions = []
    for hit in docs_index_old:
        #print "fo"
        #print(json.dumps(hit, sort_keys=True, indent=4, separators=(',', ': ')))

        values = hit['_source']['data']

        if hasattr(hit['_source']['data'], '__getitem__'):
            values = {}
            for key, val in hit['_source']['data'].iteritems():
                for old_seq, new_seq in replace_key_seqs.iteritems():
                    new_key = key.replace(old_seq, new_seq)
                values[new_key] = val
        #else:
        #    values.append({'name': 'general', 'values': val})

        doc = {
            '@timestamp': hit['_source']['@timestamp'],
            'code': hit['_source']['retcode'],
            'entity': hit['_source']['minion'],
            'fun': hit['_source']['fun'],
            'origin': hit['_source']['jid'],
            'metrics': values,
        }
        bulk_actions.append({'_type': 'common', '_source': doc})

    if len(res) > 0:
        res = bulk(client=es, actions=bulk_actions, index=index_common)
