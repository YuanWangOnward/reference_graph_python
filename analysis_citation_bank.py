# create graph with Scupus citation info

import auto_reference_graph
import importlib
import csv
import functools
import pandas as pd
import subprocess
from openpyxl import load_workbook
import os
import glob
import pickle

importlib.reload(auto_reference_graph)
arg = auto_reference_graph.AutoReferenceGraph()


# global setting
GV_PATH = "/Users/yuanwang/Google_Drive/projects/Gits/reference_graph_python/graph.gv"
RELATION_PATH = "/Users/yuanwang/Google_Drive/job/2017ATT/research/relationship_sentence.csv"
XLSX_PATH = "/Users/yuanwang/Google_Drive/job/2017ATT/research/reference_graph_sentence.xlsx"
CITATION_BANK_PATH = "/Users/yuanwang/Google_Drive/job/2017ATT/research/citation_bank"
GRAPH_OUTPUT_PATH = "/Users/yuanwang/Google_Drive/projects/Gits/reference_graph_python/graph.pdf"
SCUPUS_RELATION_PATH = "/Users/yuanwang/Google_Drive/projects/Gits/reference_graph_python/scupus_relation.csv"

# df, relation = arg.load_scupus_citation_bank(CITATION_BANK_PATH)
df, relation = arg.load_scupus_citation_bank(CITATION_BANK_PATH, 'cited_by')

new_papers = [item[1] for item in relation]
citation_count = arg.get_citation_count([item[1] for item in relation])
top_citations = {id:citation_count[id] for id in set(citation_count.keys()) if citation_count[id] >= 5}
len(top_citations)
df.loc[top_citations]['Title']

i=0
top_citations_temp = list(top_citations.keys())
for i in range(len(top_citations_temp)):
    print(df.loc[top_citations_temp[i]]['Title'])

df.duplicated()
df.drop_duplicates()

arg.create_gv_file(GV_PATH, df, relation)

# arg.create_graph(GV_PATH, GRAPH_OUTPUT_PATH, 'png')




with open(SCUPUS_RELATION_PATH, 'w') as csvfile:
    spamwriter = csv.writer(csvfile)
    for row in relation:
        spamwriter.writerow(row)


#df = arg.add_id(df)


"""
citation_back_path = CITATION_BANK_PATH

df_all = pd.DataFrame()
relation = pd.DataFrame()
extension = 'csv'
os.chdir(citation_back_path)
files = [i for i in glob.glob('*.{}'.format(extension))]
# print(result)
for file in files:
# file = 'Kim2014ConvolutionalNeuralNetworks.csv'
    print('loading ' + file)
    df = pd.read_csv(os.path.join(citation_back_path, file), sep=',')
    print(len(df.columns))

# print(df)
df_all = df_all.append(df)
# print(df_all)

"""
print(json.dumps(resp.json(),sort_keys=True,indent=4, separators=(',', ': ')))