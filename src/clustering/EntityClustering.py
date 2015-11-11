import codecs
import sys
import getopt
import json
import random
import uuid

PRIOR = 0.1
data_folder = '../../data/'

## PROBABILITY TABLES
MATCH_ITEMS = ['personAge', 'hairColor', 'eyeColor', 'name']
MATCHPROBS = json.loads(open(data_folder+'MATCHPROBS.json').read())
TOTALS = json.loads(open(data_folder+'TOTALS.json').read())
RELATIVE_FREQS = {}
for match_item in MATCH_ITEMS:
    try:
        RELATIVE_FREQS[match_item] = json.loads(open(data_folder+match_item+'_frequencies.json').read())
    except:
        print '!!!!ERROR LOADING RELATIVE_FREQS for ' + match_item

## Not USED YET
MAX_VALUES = {
    'personAge': 2,
    'hairColor': 2,
    'eyeColor': 2,
    'name': 2
}

def get_best_record_and_score(cluster, records):
    best_record = {}
    best_score = 0
    for record in records:
        score = PRIOR
        for key in cluster.get_keys():
            if key in record:
                # We do this because some of the values are strings and some are arrays
                record_values = []
                entity_values = cluster.entity["entity_"+key]
                
                if isinstance(record[key], basestring):
                    record_values.append(record[key])
                else:
                    record_values = record[key]
                 
                freq_count_total = 0
                match = False
                for record_value in record_values:
                    record_value = record_value.lower()
                    for entity_value in entity_values:
                        entity_value = entity_value.lower()
                        freq_count = 1
                        if record_value in RELATIVE_FREQS[key]:
                            freq_count = RELATIVE_FREQS[key][record_value]
                        freq_count_total += freq_count
                        
                        if record_value == entity_value:
                            match = True
                
                if freq_count_total > 0:
                    PVr = (1.0*freq_count_total) / (1.0*TOTALS[key])
                    if match:
                        numerator = MATCHPROBS[key]
                    else:
                        numerator = (1 - MATCHPROBS[key]) * PVr
                    
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
        
        self.items.append(item)
        
    def get_keys(self):
        keys = self.entity.keys()
#         keys.remove('uri')
        return keys
    
    def __init__(self):
        self.items = []
        self.entity = {}
#         self.entity['entity_uris'] = []
        self.entity['entity_id'] = str(uuid.uuid4())
    
    def getFlattenedItems(self):
        output_objects = []
        for item in self.items:
            output_object = item
            output_object.update(self.entity)
            output_objects.append(output_object)
        return output_objects
            
#     def __str__(self, *args, **kwargs):
#         output_object = {}
#         output_object['entity'] = self.entity
#         for item in output_object['entity']:
#             output_object['entity'][item] = list(set(output_object['entity'][item]))
#         output_object['items'] = self.items
#         return json.dumps(output_object)

def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:",["ifile=",])
    except getopt.GetoptError:
        print 'test.py -i <inputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
#     print 'Input file is ', inputfile
    
    records = []
    
    with codecs.open(inputfile, "r", "utf-8") as myfile:
        for line in myfile:
            the_json = line.encode("utf-8")
            json_object = json.loads(the_json)
            records.append(json_object)
        
    # Take an item from the canopy and make it a cluster
    clusters = []
    random.shuffle(records)
    
    while len(records) > 0:
        processing_item = records.pop()
        
        new_cluster = Cluster()
#         print "Processing " + str(processing_item)
        new_cluster.addItem(processing_item)
        score = 1
        while score > 0.5:
            (record, score) = get_best_record_and_score(new_cluster, records)
            if score > 0.5:
                new_cluster.addItem(record)
#                 print score
#                 print " -- Added " + str(record)
                records.remove(record)

        clusters.append(new_cluster)
        
    json_result = []
    for cluster in clusters:
        json_result.extend(cluster.getFlattenedItems())
    for result in json_result:
        print json.dumps(result, separators=(',', ': '))

if __name__ == "__main__":
    main(sys.argv[1:])