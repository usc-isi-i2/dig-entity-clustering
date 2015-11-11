from elasticsearch.client import Elasticsearch
import csv
import json

MATCH_ITEMS = ['personAge', 'hairColor', 'eyeColor', 'name']

if __name__ == '__main__':
    clusters = {}
    
    ## Code to pull in known clusters from ES
#     elasticsearch_loc = 'https://darpamemex:darpamemex@esc.memexproxy.com/dig-ht-trial11/adultservice/'
#     es = Elasticsearch([elasticsearch_loc], show_ssl_warnings=False)
#     
#     ads = 0
#     ads_found = 0
#     csv_file = '/Users/bamana/Downloads/nov2015_qpr_truth__ids_images.csv'
#     with open(csv_file) as myfile:
#         csvreader = csv.reader(myfile, delimiter=',')
#         for row in csvreader:
#             cluster_id = row[0]
#             ad_id = row[5]
#             if ad_id == 'ad id':
#                 continue
#             ads += 1
#             res = es.search(body={"query": {"match": {"offers.identifier" : str(ad_id)}}})
#             total_hits = res['hits']['total']
#             if total_hits > 0:
#                 ads_found += 1
#                 if cluster_id not in clusters:
#                     clusters[cluster_id] = []
#                 clusters[cluster_id].append(res['hits']['hits'][0])
#     
#     print json.dumps(clusters, sort_keys=True, indent=4, separators=(',', ': '))

    clusters = json.loads(open('../../sample/truth_clusters.json').read())
    potentials = {}
    matches = {}
    
    for match_item in MATCH_ITEMS:
        potentials[match_item] = 0
        matches[match_item] = 0
    
    for cluster_id in clusters:
        cluster = clusters[cluster_id]
        if len(cluster) > 0:
            for record_left in cluster:
                for record_right in cluster[1:]:
                    for match_item in MATCH_ITEMS:
                        if match_item in record_left['_source'] and match_item in record_right['_source']:
                            match = False
                            potentials[match_item] += 1
                            record_left_values = []
                            record_right_values = []
                
                            if isinstance(record_left['_source'][match_item], basestring):
                                record_left_values.append(record_left['_source'][match_item])
                            else:
                                record_left_values = record_left['_source'][match_item]
                                
                            if isinstance(record_right['_source'][match_item], basestring):
                                record_right_values.append(record_right['_source'][match_item])
                            else:
                                record_right_values = record_right['_source'][match_item]

                            for record_left_value in record_left_values:
                                for record_right_value in record_right_values:
                                    if record_left_value == record_right_value:
                                        match = True
                                        break
                            if match:
                                matches[match_item] += 1
    print potentials
    print matches
    
    match_probs = {}
    for match_item in MATCH_ITEMS:
        prob = (1.0*matches[match_item]) / (1.0*potentials[match_item])
        match_probs[match_item] = prob
        
    print json.dumps(match_probs, sort_keys=False, indent=4, separators=(',', ': '))
    