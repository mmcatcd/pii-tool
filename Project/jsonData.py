import pandas as pd
import re
import ijson
import spacy
import json

class jsonData:

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


    def flatten_json(self, y):  # function to flatten jsons
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


    def json_to_dataframe(self, filename):  # function to turn flsttened json into a pandas dataframe
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


    def run(self, rules_dict, filename):
        nlp = spacy.load('en_core_web_sm')
        report_data = []

        ## rule based approach
        for rule in rules_dict:
            a = open(filename, 'r')
            parser = ijson.parse(a)
            for prefix, event, value in parser:
                if re.search(rule, prefix, re.IGNORECASE):
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))
                        if r.match(value):
                            string = "Location: %s, Value: %s" % (prefix, value)
                            report_data.append(string)
        
        ## NLP based approach
        a = open(filename, 'r')
        parser = ijson.parse(a)
        for prefix, event, value in parser:
            if isinstance(value, str):
                doc = nlp(value)
                for ent in doc.ents:
                    if ent.label_ == 'PERSON':
                        string = "POSSIBLE PII @: %s, Value: %s" % (prefix, value)
                        report_data.append(string)
                        
        return report_data    


    def write_report(self, report_data):
        writefile = open('report.txt', 'w+')
        [writefile.write(line + "\n") for line in report_data]

