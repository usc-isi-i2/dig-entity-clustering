import codecs
import sys
import getopt
import json

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
    
    with codecs.open(inputfile, "r", "utf-8") as myfile:
        for line in myfile:
            the_json = line.encode("utf-8")
            json_object = json.loads(the_json)
            print json_object

if __name__ == "__main__":
    main(sys.argv[1:])