
import codecs
import json

if __name__ == '__main__':
    json_file = ''
    with codecs.open('../../sample/es_result.json', "r", "utf-8") as myfile:
        for line in myfile:
            json_file += line
    
    result = {}   
    es_result = json.loads(json_file)
    for bucket in es_result['aggregations']['identical-text']['buckets']:
        result[bucket['key']] = bucket['doc_count']
    
    print json.dumps(result, sort_keys=False, indent=4, separators=(',', ': '))