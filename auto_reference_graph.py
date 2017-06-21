import re
import copy
import numpy as np
import csv
import functools
import pandas as pd
import subprocess
from openpyxl import load_workbook
import os
import glob

class AutoReferenceGraph:
    def __init__(self):
        self.color = {'node': "#855D5D", 'label_font': "#FFFFFF", 'label': "#9B2D1F", 'content_font': "#000000",
                      'content': "#EFE7E7", 'label_emphasized': "#9B2D1F", 'content_emphasized': "#EFE7E7",
                      'label_review': "#A28E6A"}
        self.edge_style = {'Leads_to': '[ weight=4, penwidth=3, color="#855D5D"]',
                           'Cites': '[ weight=2, penwidth=2, color="#855D5D"]'}
        try:
            self.template = self.load_template("./rs/nodeTemplate.txt")
        except:
            print('Node Template needs to be loaded')

    def load_template(self, template_path):
        self.template = open(template_path, 'r').read()
        return self.template

    def collect_info(self, pub, extra_info=None):
        """
        For each publication, only collect a subset info from Pulication
        :param pub: a Publication instance containing info
        :param extra_info: a string list of extra info to be collected beyond default ones
        :return: a dictionary of collected info
        """
        output = {}
        default_info = ['ID', 'author', 'year', 'title', 'citedby']
        if isinstance(extra_info, list):
            info = default_info + extra_info
        else:
            info = default_info

        for i in info:
            if i in pub.bib.keys():
                output[i] = pub.bib[i]
            elif i in dir(pub):
                output[i] = getattr(pub, i)
            else:
                output[i] = None
        return output

    def get_id(self, pub):
        """
        Get ID from pub is pub is filled, otherwise, make one which is different from the filled one.
        :param pub: a Publication instance containing info
        :return: ID string
        """
        if pub._filled is True:
            return pub.bib['ID']
        else:
            regex = re.compile('[^a-zA-Z0-9 ]')
            id_temp = regex.sub('', pub.bib['title'])
            return ''.join(id_temp.title().split(' '))

    def content_wrapper(self, text, length_perline=24):
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

    def add_a_node(self, template, items, values, display_keys=None, color=None):
        """ add a node to graph"""
        if display_keys is None:
            display_keys = items

        if color is None:
            color = self.color

        tmp = copy.deepcopy(template)
        # look for label and title first, to place them on top
        # encoding by citation
        if "Citation" in items:
            tmp = tmp.replace("$$$$",
                              '<TR><TD COLSPAN="2" BGCOLOR="colorLabel"><FONT  POINT-SIZE="20" COLOR="colorLabelFont">'
                              + self.content_wrapper(
                                  str(values[list(items).index("Label")])) + '</FONT></TD></TR>\n ' + "$$$$")
        else:
            tmp = tmp.replace("$$$$",
                              '<TR><TD COLSPAN="2" BGCOLOR="colorLabel"><FONT  POINT-SIZE="20" COLOR="colorLabelFont">'
                              + self.content_wrapper(
                                  str(values[list(items).index("Label")])) + '</FONT></TD></TR>\n ' + "$$$$")
        tmp = tmp.replace("$$$$", '<TR><TD COLSPAN="2" BGCOLOR="colorContent"><FONT COLOR="colorContentFont">'
                          + self.content_wrapper(
            str(values[list(items).index("Title")])) + '</FONT></TD></TR>\n ' + "$$$$")

        for item, value in zip(items, values):
            if item.strip() == "ID":
                tmp = tmp.replace("nodeID", value)
            elif item.strip() in ["Label", "Title", "Year", "Note"]:
                pass
            elif item in display_keys:
                if value != None and value not in ['None']:
                    tmp = tmp.replace("$$$$",
                                      '<TR><TD COLSPAN="1" width="20">' + item + '</TD><TD COLSPAN="1" width="180">'
                                      + self.content_wrapper(str(value)) + '</TD></TR>\n ' + "$$$$")
        # note shooud be put at the end
        if str(values[list(items).index("Note")]) != None and str(values[list(items).index("Note")]) != 'None':
            tmp = tmp.replace("$$$$", '<TR><TD COLSPAN="2">'
                              + self.content_wrapper(str(values[list(items).index("Note")])) + '</TD></TR>\n ' + "$$$$")

        tmp = tmp.replace("$$$$", '')
        tmp = tmp.replace("colorNode", self.color['node'])
        tmp = tmp.replace("colorLabelFont", self.color['label_font'])
        if "Citation" in items:
            dark = np.array([float(int(self.color['label'][1:3], 16)),
                             float(int(self.color['label'][3:5], 16)),
                             float(int(self.color['label'][5:7], 16))])
            shallow = np.array([float(int(self.color['content'][1:3], 16)),
                                float(int(self.color['content'][3:5], 16)),
                                float(int(self.color['content'][5:7], 16))])
            color_temp = dark + (64. - float(values[list(items).index("Citation")])) / 64. * np.linalg.norm(
                shallow - dark)
            color_temp = np.minimum(color_temp, shallow)
            color_temp = np.maximum(color_temp, dark)
            color_temp = [str(hex(int(v)))[-2:] for v in list(color_temp)]
            color_temp = '#' + ''.join(color_temp)
            # color_temp = self.color['label']
            tmp = tmp.replace("colorLabel", color_temp)
            # tmp = tmp.replace("colorLabel", self.color['label'])
        else:
            tmp = tmp.replace("colorNode", self.color['node'])

        # tmp = tmp.replace("colorLabel", self.color['label'])
        tmp = tmp.replace("colorContentFont", self.color['content_font'])
        tmp = tmp.replace("colorContent", self.color['content'])
        return tmp

    def load_relationship(self, relation_path):
        relations = list(csv.reader(open(relation_path, 'r')))
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
        return df_relation

    def load_reference_info(self, xlsx_path):
        """load a xlsx file for reference info"""
        wb = load_workbook(filename=xlsx_path)
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

    def combine_info(self, df, df_relation):
        df = df.append(df_relation)
        df = df.drop_duplicates(subset='ID')
        return df

    def create_gv_file(self, GV_PATH, df, relations):
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
                tmp = tmp[0] + ' -> ' + tmp[1] + self.edge_style[tmp[2]]
                f.write('    ' + tmp)

            # add nodes
            for idx in df.index:
                if 'if_record' in df.columns:
                    if df.loc[idx]['if_record']:
                        f.write(self.add_a_node(self.template, df.columns, df.loc[idx]))
                    else:
                        pass

            f.write('}\n')

    def create_graph(self, gv_path, output_path, output_type):
        if output_type == 'png':
            subprocess.call(['dot', '-Tpng', gv_path, '-o', output_path])
        elif output_type == 'pdf':
            subprocess.call(['dot', '-Tpdf', gv_path, '-o', output_path])
        else:
            raise ValueError('type error')

    def add_id(self, df):
        """
        add id column to a dataframe
        :param df: 
        :return: 
        """
        temp = []
        for idx in range(len(df)):
            temp.append(self.make_id(df.iloc[idx]['Authors'], df.iloc[idx]['Year'], df.iloc[idx]['Title']))
        df['ID'] = temp
        df.index = df['ID']
        return df

    def make_id(self, author, year, title):
        regex = re.compile('[^a-zA-Z0-9 ]')
        temp1 = regex.sub('', author)
        temp1 = temp1.split(' ')[0]
        temp2 = str(year)
        temp3 = regex.sub('', title)
        temp3 = ''.join(temp3.title().split(' ')[0:3])
        return ''.join([temp1, temp2, temp3])

    def load_scupus_citation_bank(self, citation_back_path, loading_type='all'):
        """
        
        :param citation_back_path: 
        :param loading_type: 'all', 'cited_by', 'citing'
        :return: 
        """
        df_all = pd.DataFrame()
        relation_all = []
        extension = 'csv'
        os.chdir(citation_back_path)
        files = [i for i in glob.glob('*.{}'.format(extension))]
        # print(result)
        for file in files:
            print('loading ' + file)
            df = pd.read_csv(os.path.join(citation_back_path, file), sep=',')
            df = self.add_id(df)
            if file[-5] == '_':
                if loading_type in ['all', 'cited_by']:
                    relation_all = relation_all + [[file[:-5], id, 'Cites'] for id in df['ID']]
            else:
                if loading_type in ['all', 'citing']:
                    relation_all = relation_all + [[id, file[:-4], 'Cites'] for id in df['ID']]
            df_all = df_all.append(df)
        # df_all = self.add_id(df_all)
        df_all = df_all.drop_duplicates(subset="ID")
        return [df_all, relation_all]

    def get_citation_count(self, reference_list):

        ids = set(reference_list)
        count = {}
        for id in ids:
            count[id] = reference_list.count(id)
        return count


