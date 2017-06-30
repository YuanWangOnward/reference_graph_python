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
import functools

# global setting
PROJECT_PATH = "/home/ywang/PycharmProjects/reference_graph_python"
RESEARCH_PATH = "/home/ywang/Desktop/research"
GV_PATH = PROJECT_PATH + "/graph.gv"
SEED_RELATION_PATH = RESEARCH_PATH + "/relationship_sentence.csv"
SEED_XLSX_PATH = RESEARCH_PATH + "/reference_graph_sentence.xlsx"
CITATION_BANK_PATH = RESEARCH_PATH + "/citation_bank"
GRAPH_OUTPUT_PATH = PROJECT_PATH + "/graph"
SCUPUS_RELATION_PATH =PROJECT_PATH + "/scupus_relation.csv"

importlib.reload(auto_reference_graph)
arg = auto_reference_graph.AutoReferenceGraph()
arg.display_keys = ['Citation', 'Title']
arg.temple = arg.load_template(PROJECT_PATH + "/rs/nodeTemplate.txt")


# load Scupus citation bank
df, relation = arg.load_scupus_citation_bank(CITATION_BANK_PATH, 'all')

# find the cohesive paper set
cohesive_reference_set = arg.find_cohesive_data_set(relation, n_threshold=5)
cohesive_reference_set = cohesive_reference_set.index

# find reference info and relationship within the cohesive reference set
relation_cohesive = arg.filter_relation_by_cohesive_set(relation, cohesive_reference_set)
df_cohesive = arg.filter_reference_info_by_cohesive_set(df, cohesive_reference_set)

# load info of seed collection
df_seed, relation_seed = arg.load_seed_collection(SEED_RELATION_PATH, SEED_XLSX_PATH)

# merge info
relation = relation_cohesive + relation_seed
relation = arg.remove_duplicated_relation(relation)
df = df_seed.append(df_cohesive)
df = df.drop_duplicates(subset='ID')
df = arg.remove_isolated_reference(df, relation)

# create .gv file
arg.create_gv_file(GV_PATH, df, relation)


# draw the reference graph
outpout_type = 'pdf'
arg.create_graph(GV_PATH, '.'.join([GRAPH_OUTPUT_PATH, outpout_type]), outpout_type)






