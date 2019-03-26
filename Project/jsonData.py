import pandas as pd
import re
import ijson
import spacy
import json
import numpy as np

class jsonData:

    def print_full(self, x):    # function that prints full dataframe for display/debugging purposes
        pd.set_option('display.max_rows', len(x))
        pd.set_option('display.max_fields', None)
        pd.set_option('display.width', 2000)
        pd.set_option('display.float_format', '{:20,.2f}'.format)
        pd.set_option('display.max_colwidth', -1)
        print(x)
        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_fields')
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
        fields_list = list(flat.keys())
        for item in fields_list:
            row_idx = re.findall(r'\_(\d+)\_', item )[0]
            field = item.replace('_'+row_idx+'_', '_')
            row_idx = int(row_idx)
            value = flat[item]
            results.loc[row_idx, field] = value

        return results

    def sensitivities(self, field, field_score, field_score_max, field_score_min, confidence_values, running_scores):
        running_scores.append(field_score)
        confidence_values.append("Sensitivity Score of field " + "'" + field + "' is: " + str(field_score))
        confidence_values.append("Max Sensitivity Score of field " + "'" + field + "' is: " + str(field_score_max))
        confidence_values.append("Min Sensitivity score of field " + "'" + field + "' is: " + str(field_score_min))
        if field_score >= field_score_max:
            confidence_values.append("LEVEL: CRITICAL" + "\n")

        if field_score < field_score_max and field_score > field_score_min:
            confidence_values.append("LEVEL: MEDIUM" + "\n")

        if field_score <= field_score_min:
            confidence_values.append("LEVEL: LOW" + "\n")


    def run(self, rules_dict, scores, filename):
        nlp = spacy.load('en_core_web_sm')
        report_data = []
        confidence_values = []
        entries = 0
        running_scores = []

        ## rule based approach
        for rule in rules_dict:
            field_total = 0
            field = ""
            matched_vals = []
            
            a = open(filename, 'r')
            parser = ijson.parse(a)
            for prefix, event, value in parser:
                entries += 1
                if re.search(rule, prefix, re.IGNORECASE):
                    field_total += 1
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))
                        if r.match(value):
                            matched_vals.append(value)
                            string = "Location: %s, Value: %s" % (prefix, value)
                            report_data.append(string)
                            field = prefix

            ## individual field scores
            if field != "":
                score_dict = self.search_dicts(rule, scores)
                field_score = float(score_dict.get(rule)) * len(matched_vals)
                field_score_max = float(score_dict.get(rule)) * field_total
                field_score_min = float(score_dict.get(rule))
                self.sensitivities(field, field_score, field_score_max, field_score_min, confidence_values, running_scores)

        ## overall score
        overall_average = str(np.array(running_scores).mean() * entries)
        confidence_values.append("Overall Mean Sensitivity Score: " + overall_average)
        overall_max = str(np.sum(np.array(running_scores)) * entries)
        confidence_values.append("Overall Max Sensitivity Score: " + overall_max )
        overall_min = str(np.sum(np.array(running_scores)))
        confidence_values.append("Overall Min Sensitivity Score: " + overall_min + "\n")


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
                        
        self.write_report(report_data, confidence_values)    


    def write_report(self, report_data, confidence_values):
        writefile = open('report.txt', 'w+')
        [writefile.write(line + "\n") for line in confidence_values]
        [writefile.write(line + "\n") for line in report_data]
