import re
import pandas as pd
import numpy as np
import spacy
import csv
from pprint import pprint

class csvData:
    df = None
    percent_critical = 0
    percent_high = 0
    percent_medium = 0
    percent_low = 0
    total = 0

    def __init__(self, filename):
        self.df = pd.read_csv(filename)
        self.total = len(self.df) * len(self.df.columns)
        
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


    def search_dicts(self, key, list_of_dicts):
        for item in list_of_dicts:
            if key in item.keys():
                return item

    def get_level(self, level, low, medium, high, critical, score, matched_vals):
        if score == critical:
            level = 'CRITICAL'
            self.percent_critical += len(matched_vals)

        if score >= high and score < critical:
            level = 'HIGH'
            self.percent_high += len(matched_vals)

        if score >= medium and score < high:
            level = 'MEDIUM'
            self.percent_medium += len(matched_vals)
                        
        if score <= low:
            level = 'LOW'
            self.percent_low += len(matched_vals)

        return level
        

    def run(self, rules_dict, scores):
        self.df = self.df.applymap(str)         # preprocessing of dataframe
        self.df.fillna("NaN!", inplace = True)  # preprocessing of dataframe
        overall = []
        per_column = []
        report_data = [['Rule matched', 'Field', 'Value', 'Mean', 'Max', 'Min', '%Critical', '%High', '%Medium', '%Low', 'Rule matched', 'Field', 'Score', 'Level', 'Variance']]
        critical = 1.0
        high = 0.8
        medium = 0.4
        low = 0.3
        level = 'UNDETERMINED'
        vals = [] # scores for each column
        
        max_rule = 0.0
        min_rule = 1.0

        ## rule based approach
        for rule in rules_dict:
            for column in self.df.columns:
                if re.search(rule, column, re.IGNORECASE): 
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))  
                        matched_vals = list(set(filter(r.match, self.df[column])))

                        score_dict = self.search_dicts(rule, scores)
                        column_score = float(score_dict.get(rule))

                        if column_score > max_rule:
                            max_rule = column_score

                        if column_score < min_rule:
                            min_rule = column_score

                        if matched_vals:
                            column_score = (column_score * len(matched_vals)) / len(matched_vals) # for individual field
                        
                        level = self.get_level(level, low, medium, high, critical, column_score, matched_vals)
                        per_column.append([rule, column, column_score, level])
                        vals.append(column_score)

                        for val in matched_vals: 
                            report_data.append([rule, column, val, "", "", "", "", "", "", "", "", "", "", "", ""]) # rule, field, value, ....                          
                            #found_values.append([rule, column + str(np.where(self.df[column]==val)[0] + 1), val])

        if vals:
            overall_mean = round(np.array(vals).mean(), 3)
            self.percent_critical = round(self.percent_critical/self.total, 3) * 100
            self.percent_high = round(self.percent_high/self.total, 3) * 100
            self.percent_medium = round(self.percent_high/self.total, 3) * 100
            self.percent_low = round(self.percent_low/self.total, 3) * 100
            percentages = [self.percent_critical, self.percent_high, self.percent_medium, self.percent_low]

            per_column = self.add_variances(overall_mean, vals, per_column) # rule, field, score, level, variance
            overall.extend([str(overall_mean), str(max_rule), str(min_rule)]) # mean, max, min
            overall.extend(percentages) # mean, max, min, percentages
            overall.extend(per_column[0]) # mean, max, min rule, percentages, field, score, level, variance
            temp = list(filter(None, report_data[1]))
            temp.extend(overall)
            report_data[1] = temp
            i = 2

            for col_data in per_column:
                temp = list(filter(None, report_data[i]))
                blanks = ['', '', '', '', '', '', '']
                temp.extend(blanks)
                temp.extend(col_data)
                report_data[i] = temp
                i += 1
        self.write_report(report_data)

        # ## NLP approach - attempt
        # for column in df.columns:
        #     for val in df[column]:
        #         if df[column].dtype != np.float64 and df[column].dtype != np.int64:
        #             doc = nlp(val)
        #             for ent in doc.ents:
        #                 if ent.label_ == 'PERSON':
        #                     string = "POSSIBLE PII @: %s, Value: %s" % (column + str(np.where(df[column]==val)[0] + 1), val) 
        #                     report_data.append(string)
        #                 #print(ent.text, ent.start_char, ent.end_char, ent.label_)

    def add_variances(self, overall_mean, vals, per_column):
        variances = []
        temp_vals = vals
        i = 0
        for val in temp_vals:
            val = (val - overall_mean)**2
        for val in temp_vals:
            variances.append(round(val/len(vals), 3))
        for l in per_column:
            l.append(variances[i])
            i += 1
        return per_column


    def write_report(self, report_data):
        writefile = open('report.csv', 'w+')
        writer = csv.writer(writefile)
        writer.writerows(report_data)