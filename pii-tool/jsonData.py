import pandas as pd
import re
import ijson
import json
import numpy as np
import csv

class jsonData:
    percent_critical = 0
    percent_high = 0
    percent_medium = 0
    percent_low = 0
    total = 0
    def __init__(self):
        pass

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


    def search_dicts(self, key, list_of_dicts):
        for item in list_of_dicts:
            if key in item.keys():
                return item


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



    def get_level(self, level, low, medium, high, critical, score, matched_vals):
        if score == critical:
            level = 'CRITICAL'
            self.percent_critical += (matched_vals)

        if score >= high and score < critical:
            level = 'HIGH'
            self.percent_high += (matched_vals)

        if score >= medium and score < high:
            level = 'MEDIUM'
            self.percent_medium += (matched_vals)
                        
        if score <= low:
            level = 'LOW'
            self.percent_low += (matched_vals)

        return level
        

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


    def run(self, rules_dict, scores, filename):
        report_data = []
        per_column = []
        report_data = [['Rule matched', 'Field', 'Value', 'Mean', 'Max', 'Min', '%Critical', '%High', '%Medium', '%Low', 'Rule matched', 'Field', 'Score', 'Level', 'Variance']]
        overall = []
        running_scores = []

        min_rule = 1.0
        max_rule = 0
        critical = 1.0
        high = 0.8
        medium = 0.4
        low = 0.3
        level = 'UNDETERMINED'

        ## rule based approach
        for rule in rules_dict:
            field = ""
            matched_vals = 0
            
            a = open(filename, 'r')
            parser = ijson.parse(a)
            for prefix, event, value in parser:
                self.total += 1
                if re.search(rule, prefix, re.IGNORECASE):
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))
                        if r.match(value):
                            matched_vals += 1
                            #string = "Location: %s, Value: %s" % (prefix, value)
                            report_data.append([rule, prefix, value, "", "", "", "", "", "", ""])
                            field = prefix
                            matched_rule = rule

            ## individual field scores
            if field != "":
                score_dict = self.search_dicts(rule, scores)
                field_score = float(score_dict.get(rule))
                if field_score > max_rule:
                    max_rule = field_score
                
                if field_score < min_rule:
                    min_rule = field_score

                field_score = float(score_dict.get(rule)) * matched_vals / matched_vals
                level = self.get_level(level, low, medium, high, critical, field_score, matched_vals)
                per_column.append([matched_rule, field, field_score, level])
                running_scores.append(field_score)
        
        ## overall score
        self.percent_critical = round(self.percent_critical/self.total, 3) * 100
        self.percent_high = round(self.percent_high/self.total, 3) * 100
        self.percent_medium = round(self.percent_high/self.total, 3) * 100
        self.percent_low = round(self.percent_low/self.total, 3) * 100
        percentages = [self.percent_critical, self.percent_high, self.percent_medium, self.percent_low]
        
        overall_mean = round(np.array(running_scores).mean(), 3)
        per_column = self.add_variances(overall_mean, running_scores, per_column) # rule, field, score, level, variance
        overall.extend([str(overall_mean), str(max_rule), str(min_rule)]) # mean, max, min
        overall.extend(percentages) # mean, max, min, percentages
        overall.extend(per_column[0]) # mean, max, min rule, field, score, level, variance
        temp = list(filter(None, report_data[1]))
        temp.extend(overall)
        report_data[1] = temp
        i = 2

        # ## NLP based approach attempt
        # a = open(filename, 'r')
        # parser = ijson.parse(a)
        # for prefix, event, value in parser:
        #     if isinstance(value, str):
        #         doc = nlp(value)
        #         for ent in doc.ents:
        #             if ent.label_ == 'PERSON':
        #                 string = "POSSIBLE PII @: %s, Value: %s" % (prefix, value)
    
        for col_data in per_column:
            temp = list(filter(None, report_data[i]))
            blanks = ['', '', '', '', '', '', '']
            temp.extend(blanks)
            temp.extend(col_data)
            report_data[i] = temp
            i += 1

        self.write_report(report_data)    


    def write_report(self, report_data):
        writefile = open('report.csv', 'w+')
        writer = csv.writer(writefile)
        writer.writerows(report_data)