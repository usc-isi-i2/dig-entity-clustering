import json
import random
import uuid
import codecs

PRIOR = 0.4
MATCH_ITEMS = ['personAge', 'hairColor', 'eyeColor', 'name']
MATCHPROBS = {}
TOTALS = {}
RELATIVE_FREQS = {}

class EntityClusterer(object):
    def __init__(self):
        global PRIOR

        ## PROBABILITY TABLES
        global MATCH_ITEMS
        global MATCHPROBS
        MATCHPROBS = json.loads(open('MATCHPROBS.json').read())
        global TOTALS
        TOTALS = json.loads(open('TOTALS.json').read())
        global RELATIVE_FREQS
#         for match_item in MATCH_ITEMS:
#             try:
#                 RELATIVE_FREQS[match_item] = json.loads(open(data_folder+match_item+'_frequencies.json').read())
#             except:
#                 print '!!!!ERROR LOADING RELATIVE_FREQS for ' + match_item
        RELATIVE_FREQS['personAge'] = json.loads(open('personAge_frequencies.json').read())
        RELATIVE_FREQS['hairColor'] = json.loads(open('hairColor_frequencies.json').read())
        RELATIVE_FREQS['eyeColor'] = json.loads(open('eyeColor_frequencies.json').read())
        RELATIVE_FREQS['name'] = json.loads(open('name_frequencies.json').read())

        ## Not USED YET
        MAX_VALUES = {
            'personAge': 2,
            'hairColor': 2,
            'eyeColor': 2,
            'name': 2
        }
        
    def do_clustering(self, doc, canopy_id ):
        if not canopy_id:
            canopy_id = str(uuid.uuid4())
#         canopy_id = str(uuid.uuid4())
        records = []
        
        for record in doc['cluster']:
            records.append(record)
        
#     with codecs.open(inputfile, "r", "utf-8") as myfile:
#         for line in myfile:
#             the_json = line.encode("utf-8")
#             json_object = json.loads(the_json)
#             records.append(json_object)    
        
        # Take an item from the canopy and make it a cluster
        clusters = []
        random.shuffle(records)
    
        while len(records) > 0:
            processing_item = records.pop()
            
            new_cluster = Cluster(canopy_id)
            new_cluster.addItem(processing_item)
            score = 1
            while score > 0.5:
                (record, score) = get_best_record_and_score(new_cluster, records)
                if score > 0.5:
                    new_cluster.addItem(record)
                    records.remove(record)
    
            clusters.append(new_cluster)
        
        print '--> %d entities' % len(clusters)
        
        json_result = []
        for cluster in clusters:
            json_result.extend(cluster.getFlattenedItems())
        return json_result

def get_best_record_and_score(cluster, records):
    best_record = {}
    best_score = 0
    for record in records:
        score = PRIOR
        for key in cluster.get_keys():
            record_key = key.replace("entity_", "")
            if record_key in record:
                # We do this because some of the values are strings and some are arrays
                record_values = []
                entity_values = cluster.entity[key]
                
                if isinstance(record[record_key], basestring):
                    record_values.append(record[record_key])
                else:
                    record_values = record[record_key]
                
                freq_count_total = 0
                match = False
                for record_value in record_values:
                    record_value = record_value.lower()
                    for entity_value in entity_values:
                        entity_value = entity_value.lower()
                        freq_count = 1
                        if record_value in RELATIVE_FREQS[record_key]:
                            freq_count = RELATIVE_FREQS[record_key][record_value]
                            
                        # HACK TO DO +/- 1 for age
                        if record_key == 'personAge':
                            age = int(record_value)
                            age_plus_one = str(age+1)
                            if age_plus_one in RELATIVE_FREQS[record_key]:
                                freq_count += RELATIVE_FREQS[record_key][age_plus_one]
                                if age_plus_one == entity_value:
                                    match = True
                            age_minus_one = str(age-1)
                            if age_minus_one in RELATIVE_FREQS[record_key]:
                                freq_count += RELATIVE_FREQS[record_key][age_minus_one]
                                if age_minus_one == entity_value:
                                    match = True
                        
                        freq_count_total += freq_count
                        
                        if record_value == entity_value:
                            match = True
                
                if freq_count_total > 0:
                    PVr = (1.0*freq_count_total) / (1.0*TOTALS[record_key])
                    if match:
                        numerator = MATCHPROBS[record_key]
                    else:
                        numerator = (1 - MATCHPROBS[record_key]) * PVr
                    
                    unit_score = numerator / PVr
                    score = score * unit_score
                
#                 best_unit_score = -1
#                 for record_value in record_values:
#                     record_value = record_value.lower()
#                     for entity_value in entity_values:
#                         entity_value = entity_value.lower()
#                         freq_count = 1
#                         if record_value in RELATIVE_FREQS[key]:
#                             freq_count = RELATIVE_FREQS[key][record_value]
#                         PVr = (1.0*freq_count) / (1.0*TOTALS[key])
#                         if record_value == entity_value:
#                             numerator = MATCHPROBS[key]
#                         else:
#                             numerator = (1 - MATCHPROBS[key]) * PVr
#                         denom = PVr
#                         unit_score = numerator / denom
#                          
#                         if unit_score > best_unit_score:
#                             best_unit_score = unit_score
#                 if best_unit_score > -1:
#                     score = score * best_unit_score
                
        if score > best_score:
            best_record = record
            best_score = score
    
    return (best_record, best_score)

class Cluster(object):
    def addItem(self, item):
#         self.entity['uri'].append(item['uri'])
        if len(self.items) == 0:
            for match_item in MATCH_ITEMS:
                if match_item in item:
                    entity_match_item = "entity_" + match_item
                    self.entity[entity_match_item] = []
                    if isinstance(item[match_item], basestring):
                        self.entity[entity_match_item].append(item[match_item])
                    else:
                        self.entity[entity_match_item].extend(item[match_item])
                    self.entity[entity_match_item] = list(set(self.entity[entity_match_item]))
        else:
            for match_item in MATCH_ITEMS:
                if match_item in item:
                    entity_match_item = "entity_" + match_item
                    if entity_match_item not in self.entity:
                        self.entity[entity_match_item] = []
                    
                    if isinstance(item[match_item], basestring):
                        self.entity[entity_match_item].append(item[match_item])
                    else:
                        self.entity[entity_match_item].extend(item[match_item])
                    self.entity[entity_match_item] = list(set(self.entity[entity_match_item]))
        
        self.items.append(item)
        
    def get_keys(self):
        keys = self.entity.keys()
#         keys.remove('uri')
        return keys
    
    def __init__(self, canopy_id):
        self.items = []
        self.CANOPY_ID = canopy_id
        self.entity = {}
#         self.entity['entity_uris'] = []
        self.entity['entity_id'] = str(uuid.uuid4())
    
    def getFlattenedItems(self):
        output_objects = []
        for item in self.items:
            output_object = item
            output_object['canopy_id'] = self.CANOPY_ID
            output_object.update(self.entity)
            for item in self.entity:
                if item != 'entity_id':
                    output_object[item] = list(set(self.entity[item]))
            output_objects.append(output_object)
        return output_objects
            
#     def __str__(self, *args, **kwargs):
#         output_object = {}
#         output_object['entity'] = self.entity
#         for item in output_object['entity']:
#             output_object['entity'][item] = list(set(output_object['entity'][item]))
#         output_object['items'] = self.items
#         return json.dumps(output_object)

if __name__ == "__main__":
    
    from elasticsearch.client import Elasticsearch
    import traceback
    import urllib3
    import os
    urllib3.disable_warnings()
    
    ec = EntityClusterer()
    
    #JSON LINES TO JSON LINES
    with codecs.open('../../canopy_entity.jl', "w", "utf-8") as myfile:
        directory = '../../data/canopy_frist_try/'
        for subdir, dirs, files in os.walk(directory):
            for the_file in files:
                if the_file.startswith('.'):
                    continue
                print "processing " + the_file
                cluster = {}
                cluster['cluster'] = []
                with codecs.open(directory+the_file, "r", "utf-8") as json_file:
                    for line in json_file:
                        record = json.loads(line)
                        cluster['cluster'].append(record)
                      
                if len(cluster['cluster']) < 2:
                    print "skipping because record size is " + str(len(cluster['cluster']))
                    continue
                  
                print 'processing ' + the_file + ' with size ' + str(len(cluster['cluster']))
                records = ec.do_clustering(cluster, the_file)
                for record in records:
                    myfile.write(json.dumps(record))
                    myfile.write('\n')
                    
    ## ELASTIC SEARCH TO JSON LINES
#     elasticsearch_loc = 'https://darpamemex:darpamemex@esc.memexproxy.com/dig-clusters-qpr-01/'
#     es = Elasticsearch([elasticsearch_loc], show_ssl_warnings=False)
#    
#     import operator
#     clusters = {}
#        
#     with codecs.open('../../canopy_entity.jl', "w", "utf-8") as myfile:
#         res = es.search( body={"size" : 12834, "query": {"match_all": {}}, "_source":["cluster.a"]  })
#         hits_array = res['hits']['hits']
#         for hit in hits_array:
#             _id = hit['_id']
#             cluster_size = len(hit['_source']['cluster'])
#             clusters[_id] = cluster_size
#         sorted_clusters = sorted(clusters.items(), key=operator.itemgetter(1), reverse=True)
#            
#         for index in range(0,5):
#             print sorted_clusters[index]
#             _id = sorted_clusters[index][0]
#             res = es.search( body={"query": {"match": {"_id": _id}},"_source": { "excludes": ["cluster.image.isSimilarTo"]}})
#             hits_array = res['hits']['hits']
#             for hit in hits_array:
#                 cluster = hit['_source']
#                 print 'processing canopy with size ' + str(len(hit['_source']['cluster']))
#                 records = ec.do_clustering(cluster, None)
#                 for record in records:
#                     myfile.write(json.dumps(record))
#                     myfile.write('\n')

    
    
    