import re
import pandas as pd
import numpy as np
import spacy
import dask.dataframe as dd

class csvData:


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


    def run(self, rules_dict, filename, df):
        nlp = spacy.load('en_core_web_sm')
        report_data = []

        ## rule based approach
        for rule in rules_dict:
            for column in df.columns:
                if re.search(rule, column, re.IGNORECASE): 
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))  
                        if df[column].dtype == np.float64 or df[column].dtype == np.int64:
                            matched_vals = list(set(filter(r.match, df[column].apply(str))))

                        else:
                            matched_vals = list(set(filter(r.match, df[column])))

                        for val in matched_vals:
                            string = "Location from rule based search: %s, Value: %s" % (column + str(np.where(df[column]==val)[0] + 1), val) 
                            report_data.append(string)


        ## NLP approach
        for column in df.columns:
            for val in df[column]:
                if df[column].dtype != np.float64 and df[column].dtype != np.int64:
                    doc = nlp(val)
                    for ent in doc.ents:
                        if ent.label_ == 'PERSON':
                            string = "POSSIBLE PII @: %s, Value: %s" % (column + str(np.where(df[column]==val)[0] + 1), val) 
                            report_data.append(string)
                        #print(ent.text, ent.start_char, ent.end_char, ent.label_)

        return report_data              

    def dask_run(self, rules_dict, filename):
        df = pd.read_csv(filename)
        df.fillna("nan!", inplace = True)
        df = dd.from_pandas(df, npartitions=8)

        df.map_partitions(self.run(rules_dict, filename, df), columns=len(df)/8 ).compute(scheduler='processes')









    def write_report(self, report_data):
        writefile = open('report.txt', 'w+')
        for line in report_data:
            writefile.write(line + "\n")