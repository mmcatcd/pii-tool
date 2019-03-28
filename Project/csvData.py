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

    def sensitivities(self, column, column_score, confidence_values, vals):
        vals.append(column_score)
        confidence_values.append("Sensitivity Score of field " + "'" + column + "' is: " + str(column_score))


    def run(self, rules_dict, scores, filename):
        df = pd.read_csv(filename)
        df.fillna("NaN!", inplace = True)
        nlp = spacy.load('en_core_web_sm')
        report_data = []
        confidence_values = []
        vals = []
        overall = []
        max_rule = 0.0
        min_rule = 1.0

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
                        column_score = float(score_dict.get(rule))

                        if column_score > max_rule:
                            max_rule = column_score

                        if column_score < min_rule:
                            min_rule = column_score

                        #print(matched_vals, column)
                        if matched_vals:
                            column_score = (column_score * len(matched_vals)) / len(matched_vals) # for individual field
                        
                        self.sensitivities(column, column_score, confidence_values, vals)

                        #print(column_score)
                        for val in matched_vals:
                            string = "Location from rule based search: %s, Value: %s" % (column + str(np.where(df[column]==val)[0] + 1), val) 
                            report_data.append(string)



        overall_mean = np.array(vals).mean()
        variances = self.calculate_variances(overall_mean, vals)
        overall.append("Mean Score: " + str(overall_mean))
        overall.append("Max Score: " + str(max_rule))
        overall.append("Min Score: " + str(min_rule))
   
        self.write_report(report_data, confidence_values, variances, overall)


    def calculate_variances(self, overall_mean, vals):
        variances = []
        temp_vals = vals
        for val in temp_vals:
            val = (val - overall_mean)**2
        for val in temp_vals:
            variances.append(val/len(vals))
        return variances


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

