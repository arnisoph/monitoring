#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Salt2Common

A daemon that translates Salt specific index mappings into a common
(*place monitoring tool name here*) (FIXME) mappings.
"""
# TODO add logger
# TODO add config parser
# TODO add doc (at least mapping docs)
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from datetime import datetime, timedelta, tzinfo
import json
import sys

es = Elasticsearch(['10.10.10.100:9200'])


class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def dst(self, dt):
        return timedelta(0)


utc = UTC()

indices = [{'salt_index': 'salt-status_loadavg',
            'common_index': 'sysloadavg', },
           {'salt_index': 'salt-test_ping',
            'common_index': 'saltping', },
           {'salt_index': 'salt-diskarbe_usage',
            'common_index': 'diskusage', }, ]


def main(argv):
    for index in indices:
        common_index_prefix = 'monitoring-'
        common_index_suffix = '-{0}'.format(datetime.utcnow().strftime('%Y-%m-%d'))
        common_index = '{0}{1}'.format(common_index_prefix, index.get('common_index'))
        common_index_full = '{0}{1}{2}'.format(common_index_prefix, index.get('common_index'), common_index_suffix)
        common_index_definition = {}
        salt_index = index['salt_index']

        if not es.indices.exists(common_index):
            es.indices.create(index=common_index_full, body=common_index_definition)
            es.indices.put_alias(index=common_index_full, name=common_index)

        body = {'query': {'match_all': {}}, 'size': 1, 'sort': {'@timestamp': 'desc'}}
        res = es.search(index=common_index, body=body)

        newest_doc_time = datetime(year=1970, month=1, day=1, microsecond=1, tzinfo=utc).isoformat()
        print 'found {0} in {1}'.format(res['hits']['total'], common_index)

        if res['hits']['total'] > 0:
            newest_doc_time = res['hits']['hits'][0]['_source']['@timestamp']
        print 'newest doc in {0} has ts {1}'.format(common_index, newest_doc_time)

        time_gte = newest_doc_time
        time_lte = 'now'

        from_offset = 0
        docs_size = 10
        docs_index_old = []
        replace_key_seqs = {'-': '_'}
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
                                'must_not': [{'term': {'@timestamp': time_gte}}]
                            }
                        }
                    }
                },
                'from': from_offset,
                "size": docs_size,
                "sort": {"@timestamp": "asc"}
            }
            res = es.search(index=salt_index, body=body)

            docs_index_old += res['hits']['hits']
            from_offset += docs_size

            print 'import: total {0} - step {1}'.format(res['hits']['total'], from_offset)
            if res['hits']['total'] - from_offset <= 0:
                break

        bulk_actions = []
        for hit in docs_index_old:
            values = hit['_source']['data']

            if hasattr(hit['_source']['data'], '__getitem__'):
                values = {}
                for key, val in hit['_source']['data'].iteritems():
                    for old_seq, new_seq in replace_key_seqs.iteritems():
                        new_key = key.replace(old_seq, new_seq)
                    values[new_key] = val

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
            res = bulk(client=es, actions=bulk_actions, index=common_index)


if __name__ == '__main__':
    main(sys.argv)
