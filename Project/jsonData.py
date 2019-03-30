import pandas as pd
import re
import ijson
import json
import numpy as np

class jsonData:

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


    def sensitivities(self, field, field_score, confidence_values, running_scores):
        running_scores.append(field_score)
        confidence_values.append("Sensitivity Score of field " + "'" + field + "' is: " + str(field_score))
    
    
    def calculate_variances(self, overall_mean, running_scores):
        variances = []
        temp_vals = running_scores
        for val in temp_vals:
            val = (val - overall_mean)**2
        for val in temp_vals:
            variances.append(val/len(running_scores))
        return variances


    def run(self, rules_dict, scores, filename):
        report_data = []
        confidence_values = []
        running_scores = []
        variances = []
        overall = []
        min_rule = 1.0
        max_rule = 0

        ## rule based approach
        for rule in rules_dict:
            field = ""
            matched_vals = []
            
            a = open(filename, 'r')
            parser = ijson.parse(a)
            for prefix, event, value in parser:
                if re.search(rule, prefix, re.IGNORECASE):
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))
                        if r.match(value):
                            print(value)
                            matched_vals.append(value)
                            string = "Location: %s, Value: %s" % (prefix, value)
                            report_data.append(string)
                            field = prefix

            ## individual field scores
            if field != "":
                score_dict = self.search_dicts(rule, scores)
                field_score = float(score_dict.get(rule))
                if field_score > max_rule:
                    max_rule = field_score
                
                if field_score < min_rule:
                    min_rule = field_score

                field_score = float(score_dict.get(rule)) * len(matched_vals) / len(matched_vals)
                self.sensitivities(field, field_score, confidence_values, running_scores)

        ## overall score
        overall_mean = np.array(running_scores).mean()
        variances = self.calculate_variances(overall_mean, running_scores)
        overall.append("Mean Score: " + str(overall_mean))
        overall.append("Max Score: " + str(max_rule))
        overall.append("Min Score: " + str(min_rule))
            
        self.write_report(report_data, confidence_values, variances, overall)    


    def write_report(self, report_data, confidence_values, variances, overall):
        writefile = open('report.txt', 'w+')

        for x, y in zip(confidence_values, variances):
            writefile.write(x + "\n")
            writefile.write("Varience from mean: " + str(y) + "\n")
            writefile.write("\n")
        writefile.write("\n")

        [writefile.write(line + "\n") for line in overall]    
        writefile.write("\n")

        [writefile.write(line + "\n") for line in report_data]
