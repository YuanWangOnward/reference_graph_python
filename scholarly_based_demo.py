import scholarly
import auto_reference_graph
import importlib
import os
import pickle
import time
import random

importlib.reload(auto_reference_graph)
arg = auto_reference_graph.AutoReferenceGraph()


CITATION_PATH = os.path.join('.', 'citations')
PAPER_TXT_PATH = os.path.join('.', 'paper_list.txt')


# load paper list from txt file
text_file = open(PAPER_TXT_PATH, "r")
SEED_PAPER_TITLE_LIST = text_file.read().split('\n')
SEED_PAPER_DATA_LIST = []

# search for paper
for i in range(len(SEED_PAPER_TITLE_LIST)):
    search_query = scholarly.search_pubs_query(SEED_PAPER_TITLE_LIST[i])
    try:
        pub = next(search_query).fill()
        print('now processing: ' + pub.bib['title'])
        print('citation: ' + str(pub.citedby))
        SEED_PAPER_DATA_LIST.append(pub)
        #citations = []
        #for citation in pub.get_citedby():
        #    citations.append(citation)
        #    time.sleep(random.randint(5, 10))
        citations = [{'title': citation.bib['title'], 'citedby':citation.citedby} for citation in pub.get_citedby()]
        pickle.dump(SEED_PAPER_DATA_LIST, open(os.path.join(CITATION_PATH, arg.get_id(pub)), "wb"))
        pickle.dump(citations, open(os.path.join(CITATION_PATH, arg.get_id(pub)), "wb"))
        time.sleep(random.randint(50, 70))
    except:
        print('now processing: ' + pub.bib['title'])
        print('something goes wrong')




#loaded = pickle.load( open(os.path.join(CITATION_PATH, arg.get_id(pub)), "rb" ) )
#print(loaded[0])

'''
arg.collect_info(citations[0].fill())
print(citations[0])
print(citations[1])
'''



#search_query = scholarly.search_pubs_query('Perception of physical stability and center of mass of 3D objects')
#pub = next(search_query).fill()
#print(pub)
#print([citation.bib['title'] for citation in pub.get_citedby()])

