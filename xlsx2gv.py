# read a csv file and create a gv file for reference graph
from openpyxl import load_workbook
import pandas as pd
import copy
import subprocess
import csv
import functools
import numpy as np


def add_a_node(template, items, values):
    # <TR><TD COLSPAN="2" BGCOLOR="colorLabel"><FONT COLOR="colorLabelFont">referenceLabel</FONT></TD></TR>
    # <TR><TD COLSPAN="2" BGCOLOR="colorContent" ><FONT COLOR="colorContentFont">referenceTitle</FONT></TD></TR>
    # <TR><TD COLSPAN="1" width="20">item</TD><TD COLSPAN="1" width="180">value</TD></TR>
    global DISPLAY_KEYS
    global color
    tmp = copy.deepcopy(template)
    # look for label and title first, to place them on top
    # encoding by citation
    if "Citation" in items:
        tmp = tmp.replace("$$$$",
                          '<TR><TD COLSPAN="2" BGCOLOR="colorLabel"><FONT  POINT-SIZE="20" COLOR="colorLabelFont">'
                          + content_wrapper(str(values[list(items).index("Label")])) + '</FONT></TD></TR>\n ' + "$$$$")
        # font_size = str(min((values[list(items).index("Citation")]) / 20 + 14, 128))
        # tmp = tmp.replace("$$$$",
        #                  '<TR><TD COLSPAN="2" BGCOLOR="colorLabel"><FONT  POINT-SIZE="' +
        #                  font_size + '" COLOR="colorLabelFont">'
        #                  + content_wrapper(str(values[list(items).index("Label")])) + '</FONT></TD></TR>\n ' + "$$$$")
    else:
        tmp = tmp.replace("$$$$",
                          '<TR><TD COLSPAN="2" BGCOLOR="colorLabel"><FONT  POINT-SIZE="20" COLOR="colorLabelFont">'
                          + content_wrapper(str(values[list(items).index("Label")])) + '</FONT></TD></TR>\n ' + "$$$$")
    tmp = tmp.replace("$$$$", '<TR><TD COLSPAN="2" BGCOLOR="colorContent"><FONT COLOR="colorContentFont">'
                      + content_wrapper(str(values[list(items).index("Title")])) + '</FONT></TD></TR>\n ' + "$$$$")

    for item, value in zip(items, values):
        if item.strip() == "ID":
            tmp = tmp.replace("nodeID", value)
        elif item.strip() in ["Label", "Title", "Year", "Note"]:
            pass
        elif item in DISPLAY_KEYS:
            if value != None and value not in ['None']:
                tmp = tmp.replace("$$$$", '<TR><TD COLSPAN="1" width="20">' + item + '</TD><TD COLSPAN="1" width="180">'
                                  + content_wrapper(str(value)) + '</TD></TR>\n ' + "$$$$")
    # note shooud be put at the end
    if str(values[list(items).index("Note")]) != None and str(values[list(items).index("Note")]) != 'None':
        tmp = tmp.replace("$$$$", '<TR><TD COLSPAN="2">'
                          + content_wrapper(str(values[list(items).index("Note")])) + '</TD></TR>\n ' + "$$$$")

    tmp = tmp.replace("$$$$", '')
    tmp = tmp.replace("colorNode", color['node'])
    tmp = tmp.replace("colorLabelFont", color['label_font'])
    if "Citation" in items:
        dark = np.array([float(int(color['label'][1:3], 16)),
                         float(int(color['label'][3:5], 16)),
                         float(int(color['label'][5:7], 16))])
        shallow = np.array([float(int(color['content'][1:3], 16)),
                            float(int(color['content'][3:5], 16)),
                            float(int(color['content'][5:7], 16))])
        color_temp = dark + (64. - float(values[list(items).index("Citation")])) / 64. * np.linalg.norm(shallow - dark)
        color_temp = np.minimum(color_temp, shallow)
        color_temp = np.maximum(color_temp, dark)
        color_temp = [str(hex(int(v)))[-2:] for v in list(color_temp)]
        color_temp = '#' + ''.join(color_temp)
        # color_temp = color['label']
        tmp = tmp.replace("colorLabel", color_temp)
        # tmp = tmp.replace("colorLabel", color['label'])
    else:
        tmp = tmp.replace("colorNode", color['node'])

    # tmp = tmp.replace("colorLabel", color['label'])
    tmp = tmp.replace("colorContentFont", color['content_font'])
    tmp = tmp.replace("colorContent", color['content'])
    return tmp


def content_wrapper(text, length_perline=24):
    text = text.strip()

    # change new line mark
    text = text.replace('\n', '<BR/>')
    text = text.split('<BR/>')
    text = ' <BR/> '.join(text)

    # wrap text to certain length
    words = text.split(' ')
    words_expended = []
    character_count = 0
    for idx, word in enumerate(words):
        character_count += len(word)
        if character_count >= length_perline:
            words_expended.append(word)
            words_expended.append('<BR/>')
            character_count = 0
        else:
            words_expended.append(word)
            if '<BR/>' in word:
                character_count = 0
    text = ' '.join(words_expended)

    # remove repeated new line mark
    text = text.replace('<BR/> <BR/>', '<BR/>')
    text = text.replace('<BR/><BR/>', '<BR/>')

    return text


# global setting
TEMPLATE_PATH = "./rs/nodeTemplate.txt"
GV_PATH = "/Users/yuanwang/Google_Drive/projects/Gits/reference_graph_python/graph.gv"

# story segmentation
# RELATION_PATH = "/Users/yuanwang/Google_Drive/job/2017ATT/research/relationship.csv"
# XLSX_PATH = "/Users/yuanwang/Google_Drive/job/2017ATT/research/reference_graph.xlsx"

# sentence representation
RELATION_PATH = "/Users/yuanwang/Google_Drive/job/2017ATT/research/relationship_sentence.csv"
XLSX_PATH = "/Users/yuanwang/Google_Drive/job/2017ATT/research/reference_graph_sentence.xlsx"

DISPLAY_KEYS = ['ID', 'Title', 'Citation', 'Assumption', 'Word_representation', 'Topic_model',
                'Document_representation', 'Segmentation_approach',
                'Distance_measurement', 'Key_technique', 'Note', ]

color = {'node': "#855D5D", 'label_font': "#FFFFFF", 'label': "#9B2D1F", 'content_font': "#000000",
         'content': "#EFE7E7", 'label_emphasized': "#9B2D1F", 'content_emphasized': "#EFE7E7",
         'label_review': "#A28E6A"}

edge_style = {'Leads_to': '[ weight=4, penwidth=3, color="#855D5D"]',
              'Cites': '[ weight=2, penwidth=2, color="#855D5D"]'}

# load template
template = open(TEMPLATE_PATH, 'r').read()

# load relationship
relations = list(csv.reader(open(RELATION_PATH, 'r')))
IDs = list(set(functools.reduce(lambda x, y: x + y, [[row[0], row[1]] for row in relations])))
df_relation = pd.DataFrame(IDs, columns=['ID'])
year = pd.Series([str("".join(list(filter(str.isdigit, s))[:4])) for s in df_relation["ID"]])
label = pd.Series([s[: s.find(year[i]) + 4] for i, s in enumerate(df_relation['ID'])])
df_relation['Year'] = year
df_relation['Label'] = label
df_relation['if_record'] = False
for col in df_relation.columns:
    df_relation[col] = [value.strip() if isinstance(value, str) else value for value in df_relation[col]]
df_relation.index = df_relation['ID']

# load in .xlsx file
wb = load_workbook(filename=XLSX_PATH)
ws = wb.active
df = pd.DataFrame(ws.values)
df.columns = list(df.loc[0])
df = df.drop(df.index[0])
df.index = range(len(df.index))
# check if year and label are in the xlsx table, if not, abstract the info from ID
if 'year' not in [item.lower() for item in df.columns]:
    year = pd.Series([str("".join(list(filter(str.isdigit, s))[:4])) for s in df["ID"]])
    df['Year'] = year
if 'label' not in [item.lower() for item in df.columns]:
    year = pd.Series([str("".join(list(filter(str.isdigit, s))[:4])) for s in df["ID"]])
    label = pd.Series([s[: s.find(year[i]) + 4] for i, s in enumerate(df['ID'])])
    df['Label'] = label
for col in df.columns:
    df[col] = [value.strip() if isinstance(value, str) else value for value in df[col]]
df['if_record'] = True
df.index = df['ID']
df.index = [id.strip() for id in df['ID']]

# combine information
df = df.append(df_relation)
df = df.drop_duplicates(subset='ID')

# <TR><TD COLSPAN="1" width="20">item</TD><TD COLSPAN="1" width="180">value</TD></TR>
# build graph (make .gv file)
with open(GV_PATH, 'w') as f:
    f.write('digraph G {\n')
    f.write('    edge [comment="Wildcard node added automatic in EG."];\n')
    f.write('    node [comment="Wildcard node added automatic in EG.",\n')
    f.write('        fontname="sans-serif"];\n')
    # f.write('        size ="8, 20";\n')
    f.write('        ratio = "compress"\n')
    f.write('        rankdir = LR;\n')
    f.write('        splines=ortho;\n')
    f.write('        ranksep=0.5;\n')
    # f.write('        nodesep=0.2;\n')
    f.write('        sep=0.3;\n')
    # add time line
    f.write('    {')
    f.write('        node[shape = plaintext fontsize = 28];')
    for year in sorted(set(df['Year'])):
        if year != sorted(set(df['Year']))[-1]:
            f.write('        ' + str(year) + ' ->')
        else:
            f.write('        ' + str(year))
    f.write('    }\n')

    # add time line rank
    for year in sorted(set(df['Year'])):
        f.write('    {rank = same;')
        f.write('    ' + str(year) + ';')
        for id in df.loc[df['Year'] == year]['ID']:
            f.write('    ' + id + ';')
        f.write('    }\n')

    # add relationship
    for row in relations:
        tmp = row
        tmp = tmp[0] + ' -> ' + tmp[1] + edge_style[tmp[2]]
        f.write('    ' + tmp)

    # add nodes
    for idx in df.index:
        if df.loc[idx]['if_record']:
            f.write(add_a_node(template, df.columns, df.loc[idx]))
        else:
            pass

    f.write('}\n')

# update output
subprocess.call(['dot', '-Tpdf', '/Users/yuanwang/Google_Drive/projects/Gits/reference_graph_python/graph.gv',
                 '-o', '/Users/yuanwang/Google_Drive/projects/Gits/reference_graph_python/graph.pdf'])
