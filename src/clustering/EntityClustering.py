import codecs
import sys
import getopt
import json
import random

PRIOR = 0.2
data_folder = '../../data/'

## PROBABILITY TABLES
MATCHPROBS = json.loads(open(data_folder+'MATCHPROBS.json').read())

personAge_frequencies = json.loads(open(data_folder+'personAge_frequencies.json').read())
hairColor_frequencies = json.loads(open(data_folder+'hairColor_frequencies.json').read())
eyeColor_frequencies = json.loads(open(data_folder+'eyeColor_frequencies.json').read())
name_frequencies = json.loads(open(data_folder+'name_frequencies.json').read())

RELATIVE_FREQS = {
    'personAge': personAge_frequencies,
    'hairColor': hairColor_frequencies,
    'eyeColor': eyeColor_frequencies,
    'name': name_frequencies
}

TOTALS = {
    'personAge': 11699659,
    'hairColor': 1993511,
    'eyeColor': 1334966,
    'name': 1425455
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
                entity_values = cluster.entity[key]
                
                if isinstance(record[key], basestring):
                    record_values.append(record[key])
                else:
                    record_values = record[key]
                
                best_unit_score = -1
                for record_value in record_values:
                    record_value = record_value.lower()
                    for entity_value in entity_values:
                        entity_value = entity_value.lower()
                        freq_count = 1
                        if record_value in RELATIVE_FREQS[key]:
                            freq_count = RELATIVE_FREQS[key][record_value]
                        PVr = (1.0*freq_count) / (1.0*TOTALS[key])
                        if record_value == entity_value:
                            numerator = MATCHPROBS[key]
                        else:
                            numerator = (1 - MATCHPROBS[key]) * PVr
                        denom = PVr
                        unit_score = numerator / denom
                        
                        if unit_score > best_unit_score:
                            best_unit_score = unit_score
                if best_unit_score > -1:
                    score = score * best_unit_score
                
        if score > best_score:
            best_record = record
            best_score = score
    
    return (best_record, best_score)

class Cluster(object):
    def addItem(self, item):
        self.entity['uri'].append(item['uri'])
        if len(self.items) == 0:
            if 'personAge' in item:
                self.entity['personAge'] = []
                if isinstance(item['personAge'], basestring):
                    self.entity['personAge'].append(item['personAge'])
                else:
                    self.entity['personAge'].extend(item['personAge'])
            if 'hairColor' in item:
                self.entity['hairColor'] = []
                if isinstance(item['hairColor'], basestring):
                    self.entity['hairColor'].append(item['hairColor'])
                else:
                    self.entity['hairColor'].extend(item['hairColor'])
            if 'eyeColor' in item:
                self.entity['eyeColor'] = []
                if isinstance(item['eyeColor'], basestring):
                    self.entity['eyeColor'].append(item['eyeColor'])
                else:
                    self.entity['eyeColor'].extend(item['eyeColor'])
            if 'name' in item:
                self.entity['name'] = []
                if isinstance(item['name'], basestring):
                    self.entity['name'].append(item['name'])
                else:
                    self.entity['name'].extend(item['name'])
        else:
            if 'personAge' in item:
                if 'personAge' not in self.entity:
                    self.entity['personAge'] = []
                
                if isinstance(item['personAge'], basestring):
                    self.entity['personAge'].append(item['personAge'])
                else:
                    self.entity['personAge'].extend(item['personAge'])
            if 'hairColor' in item:
                if 'hairColor' not in self.entity:
                    self.entity['hairColor'] = []
                
                if isinstance(item['hairColor'], basestring):
                    self.entity['hairColor'].append(item['hairColor'])
                else:
                    self.entity['hairColor'].extend(item['hairColor'])
            if 'eyeColor' in item:
                if 'eyeColor' not in self.entity:
                    self.entity['eyeColor'] = []
                
                if isinstance(item['eyeColor'], basestring):
                    self.entity['eyeColor'].append(item['eyeColor'])
                else:
                    self.entity['eyeColor'].extend(item['eyeColor'])
            if 'name' in item:
                if 'name' not in self.entity:
                    self.entity['name'] = []
                    
                if isinstance(item['name'], basestring):
                    self.entity['name'].append(item['name'])
                else:
                    self.entity['name'].extend(item['name'])
        
        self.items.append(item)
        
    def get_keys(self):
        keys = self.entity.keys()
        keys.remove('uri')
        return keys
    
    def __init__(self):
        self.items = []
        self.entity = {}
        self.entity['uri'] = []
        
    def __str__(self, *args, **kwargs):
        output_object = {}
        output_object['entity'] = self.entity
        for item in output_object['entity']:
            output_object['entity'][item] = list(set(output_object['entity'][item]))
        output_object['items'] = self.items
        return json.dumps(output_object)

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
    print 'Input file is ', inputfile
    
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
        print "Processing " + str(processing_item)
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
        
        print len(records)
        print len(clusters)

if __name__ == "__main__":
    main(sys.argv[1:])