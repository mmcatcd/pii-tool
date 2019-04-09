import mysql.connector
import pandas as pd
import re
import numpy as np
import csv

class sqlData:
    df = None
    percent_critical = 0
    percent_high = 0
    percent_medium = 0
    percent_low = 0
    total = 0

    def __init__(self):
        self.sql_df = pd.DataFrame()
        self.total = len(self.sql_df) * len(self.sql_df.columns)


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


    #connect to database
    def sqldb_to_df(self, db, scores, rules_dict):
        host = db[0]
        user = db[1]
        # password = db[2]
        password = ""
        database = db[2]
        table = db[3]
        mydb = mysql.connector.connect(
            host=host, 
            user=user, 
            password=password,  
            database=database  
        )
        mycursor = mydb.cursor()
        #  access column information
        mycursor.execute("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'" + table + "'") # e.g. pi
        col_schema_result = mycursor.fetchall() # fetchall() method fetches all rows from the last execute statement

        col_count = 0
        match_count = 0
        for col_schema_line in col_schema_result:
            #print(col_schema_line)
            col_count += 1
            for rule in rules_dict:  ###
                if rule in col_schema_line:
                    #print(rule, "located at column ", col_count)
                    mycursor.execute("SELECT " + rule + " FROM " + table)
                    if match_count == 0:
                        data = {rule: pd.Series(mycursor.fetchall())}
                    else:
                        data[rule] = pd.Series(mycursor.fetchall())

                    match_count += 1

        for key in data.keys():
            for i in range(len(data[key])):
                if len(data[key][i]) == 1:
                    data[key][i] = data[key][i][0]
                    string = str(data[key][i])
                    data[key][i] = string

        self.sql_df = pd.DataFrame(data)  # panda data frame set up
        self.total = len(self.sql_df) * len(self.sql_df.columns)
        self.run(rules_dict, scores)


    def run(self, rules_dict, scores): ##
        self.sql_df = self.sql_df.applymap(str)         # preprocessing of dataframe
        self.sql_df.fillna("NaN!", inplace = True)  # preprocessing of dataframe
        overall = []
        per_column = []
        report_data = [['Rule matched', 'Field', 'Value', 'Mean', 'Max', 'Min', '%Critical', '%High', '%Medium', '%Low',
                        'Rule matched', 'Field', 'Score', 'Level', 'Variance']]
        critical = 1.0
        high = 0.8
        medium = 0.4
        low = 0.3
        level = 'UNDETERMINED'
        vals = []  # scores for each column
        max_rule = 0.0
        min_rule = 1.0
        for rule in rules_dict:
            for column in self.sql_df:
                if re.search(rule, column, re.IGNORECASE):
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))
                        #print(sql_df[column])
                        matched_vals = list(set(filter(r.match, self.sql_df[column])))

                        score_dict = self.search_dicts(rule, scores)
                        column_score = float(score_dict.get(rule))

                        if column_score > max_rule:
                            max_rule = column_score

                        if column_score < min_rule:
                            min_rule = column_score

                        # print(matched_vals, column)
                        if matched_vals:
                            column_score = (column_score * len(matched_vals)) / len(
                                matched_vals)  # for individual field

                        level = self.get_level(level, low, medium, high, critical, column_score, matched_vals)
                        # levels.append(level)
                        per_column.append([rule, column, column_score, level])
                        vals.append(column_score)

                        for val in matched_vals:
                            report_data.append([rule, column, val, "", "", "", "", "", "", "", "", "", "", "", ""]) # rule, field, value, ....


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

