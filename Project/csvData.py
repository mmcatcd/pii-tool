import csv
import re
import pandas as pd
import numpy as np
import pickle

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

    def run(self, rules_dict, filename):
        report_data = []
        df = pd.read_csv(filename)
        df.fillna("0", inplace = True)
        for rule in rules_dict:
            for column in list(df):
                if re.search(rule, column, re.IGNORECASE): 
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))  
                        if df[column].dtype == np.float64 or df[column].dtype == np.int64:
                            matched_vals = list(filter(r.match, df[column].apply(str)))

                        else:
                            matched_vals = list(filter(r.match, df[column]))

                        for val in matched_vals:
                            string = "Location: %s, Value: %s" % (column + str(np.where(df[column]==val)[0] + 1), val)
                            report_data.append(string)

        return report_data              


    def write_report(self, report_data):
        writefile = open('report.txt', 'w+')
        for line in report_data:
            writefile.write(line + "\n")