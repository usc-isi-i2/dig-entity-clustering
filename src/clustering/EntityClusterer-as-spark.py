#!/usr/bin/env python

# from pyspark import SparkContext
# 
# from optparse import OptionParser
# from fileUtil import FileUtil
from clustering import EntityClusterer
import json

if __name__ == "__main__":
    
    ec = EntityClusterer()
    json_object = json.loads(codecs.open('/Users/bamana/Documents/InferLink/workspace/dig-entity-clustering/sample/adultservice_canopy.json', "r", "utf-8").read().encode("utf-8"))
    ec.do_clustering(json_object)

#     sc = SparkContext(appName="DIG-ENTITY-CLUSTERER")
# 
#     usage = "usage: %prog [options] inputDataset inputDatasetFormat inputPath " \
#             "outputFilename outoutFileFormat"
#     parser = OptionParser()
#     parser.add_option("-r", "--separator", dest="separator", type="string",
#                       help="field separator", default="\t")
# 
#     (c_options, args) = parser.parse_args()
#     print "Got options:", c_options
#     inputFilename = args[0]
#     inputFileFormat = args[1]
#     outputPath = args[2]
#     outputFileFormat = args[3]
# 
#     fileUtil = FileUtil(sc)
#     input_rdd = fileUtil.load_json_file(inputFilename, inputFileFormat, c_options)
#     
#     ec = EntityClusterer()
# 
#     ec_rdd = input_rdd.filter(lambda x:)
#     #as_rdd = input_rdd.mapValues(lambda x: partition.filter_docs(AdultService, x)).filter(lambda x: x[1] is not None).coalesce(42)
#     #as_rdd = input_rdd.filter(lambda x: "offers" in x[1] and "image" in x[1]).mapValues(lambda x : ec.do_clustering(x)).coalesce(21)
#     
#     fileUtil.save_json_file(as_rdd, outputPath, outputFileFormat, c_options)