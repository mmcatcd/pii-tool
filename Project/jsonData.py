import json
import pandas as pd
import re
import argparse
import os

class jsonData:

    def rules(self):    # function that takes rules from file and turns them into a dictionary of format rule:RegEx
        f = open('rules.txt', 'r')
        rules_dict = {}
        for line in f:
            k, v = line.strip().split(':')
            rules_dict[k.strip()] = v.strip()
        f.close()
        return rules_dict


    def print_full(self, x):    # function that prints full dataframe for display/debugging purposes
        pd.set_option('display.max_rows', len(x))
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 2000)
        pd.set_option('display.float_format', '{:20,.2f}'.format)
        pd.set_option('display.max_colwidth', -1)
        print(x)
        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')
        pd.reset_option('display.width')
        pd.reset_option('display.float_format')
        pd.reset_option('display.max_colwidth')


    def flatten_json(self, y):  # function to recursively turn nested jsons into 
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '_')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '_')
                    i += 1
            else:
                out[name[:-1]] = x

        flatten(y)
        return out


    def json_to_dataframe(self, filename):
        jsonObj = json.load(filename)
        flat = self.flatten_json(jsonObj)

        results = pd.DataFrame()
        columns_list = list(flat.keys())
        for item in columns_list:
            row_idx = re.findall(r'\_(\d+)\_', item )[0]
            column = item.replace('_'+row_idx+'_', '_')
            row_idx = int(row_idx)
            value = flat[item]
            results.loc[row_idx, column] = value

        return results


    def run(self, rules_dict, df):
        for rule in rules_dict:
            for column in list(df):
                if re.search(rule, column, re.IGNORECASE): 
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))
                        matched_vals = list(filter(r.match, df[column]))
                        print(matched_vals) 

