import re
import pandas as pd
import numpy as np
import spacy

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


    def search_dicts(self, key, list_of_dicts):
        for item in list_of_dicts:
            if key in item.keys():
                return item

    def sensitivities(self, column, column_score, column_score_max, column_score_min, confidence_values, vals):
        vals.append(column_score)
        confidence_values.append("Sensitivity Score of field " + "'" + column + "' is: " + str(column_score))
        confidence_values.append("Max Sensitivity Score of field " + "'" + column + "' is: " + str(column_score_max))
        confidence_values.append("Min Sensitivity score of field " + "'" + column + "' is: " + str(column_score_min))
        if column_score >= column_score_max:
            confidence_values.append("LEVEL: CRITICAL" + "\n")

        elif column_score < column_score_max and column_score > column_score_min:
            confidence_values.append("LEVEL: MEDIUM" + "\n")

        elif column_score <= column_score_min:
            confidence_values.append("LEVEL: LOW" + "\n")



    def run(self, rules_dict, scores, filename):
        df = pd.read_csv(filename)
        df.fillna("NaN!", inplace = True)
        nlp = spacy.load('en_core_web_sm')
        report_data = []
        confidence_values = []
        vals = []

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

                        score_dict = self.search_dicts(rule, scores)
                        column_score = float(score_dict.get(rule)) * len(matched_vals)
                        column_score_max = float(score_dict.get(rule)) * len(df.index)
                        column_score_min = float(score_dict.get(rule))
                        self.sensitivities(column, column_score, column_score_max, column_score_min, confidence_values, vals)
                        
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
                            # print(ent.text, ent.start_char, ent.end_char, ent.label_)

        overall_average = str(np.array(vals).mean() * len(df.index))
        confidence_values.append("Overall Mean Sensitivity Score: " + overall_average)
        overall_max = str(np.sum(np.array(vals)) * len(df.index))
        confidence_values.append("Overall Max Sensitivity Score: " + overall_max )
        overall_min = str(np.sum(np.array(vals)))
        confidence_values.append("Overall Min Sensitivity Score: " + overall_min + "\n")

   
        self.write_report(report_data, confidence_values)



    def write_report(self, report_data, confidence_values):
        writefile = open('report.txt', 'w+')
        [writefile.write(line + "\n") for line in confidence_values]
        [writefile.write(line + "\n") for line in report_data]

