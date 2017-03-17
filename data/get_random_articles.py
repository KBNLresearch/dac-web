import random
import urllib
import xml.etree.ElementTree as etree


NUM_ARTICLES = 69427015
SAMPLE_SIZE = 15
SOLR_QUERY = 'http://solr.kbresearch.nl/solr/DDD_artikel_research/select?q=type:artikel&rows=1&start='


sample = random.sample(range(1, NUM_ARTICLES), SAMPLE_SIZE)

# print sample

f = open('articles_test_add.txt', 'w')

index = 0
for s in sample:
    sf = urllib.urlopen(SOLR_QUERY + str(s))
    solr_string = sf.read()
    sf.close()

    root = etree.fromstring(solr_string)
    identifier = root.findtext(".//str[@name='identifier']")
    f.write(identifier + '\n')
    index += 1
    print(index, identifier)

f.close()

