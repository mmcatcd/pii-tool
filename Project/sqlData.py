import mysql.connector
import pandas as pd
import re
import numpy as np

class sqlData:

    def search_dicts(self, key, list_of_dicts):
        for item in list_of_dicts:
            if key in item.keys():
                return item

    def sensitivities(self, column, column_score, confidence_values, vals):
        vals.append(column_score)
        confidence_values.append("Sensitivity Score of field " + "'" + column + "' is: " + str(column_score))

    #connect to database
    #def sqldb_to_df(self, host, user, password, database, table, rules_dict):
    def sqldb_to_df(self, db, scores, rules_dict):
        host = db[0]
        user = db[1]
        # password = db[2]
        password = ""
        database = db[2]
        table = db[3]
        mydb = mysql.connector.connect(
            host=host,  #"localhost" #127.0.0.1
            user=user,   #"root"
            password=password,  #""
            database=database   #"rob_dump"
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

        sql_df = pd.DataFrame(data)  # panda data frame set up
            # print(sql_df)

        self.run(rules_dict,scores, sql_df)


    def run(self, rules_dict, scores, sql_df): ##
        report_data = []
        confidence_values = []
        vals = []
        overall = []
        max_rule = 0.0
        min_rule = 1.0
        for rule in rules_dict:
            for column in sql_df:
                if re.search(rule, column, re.IGNORECASE):
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))
                        #print(sql_df[column])
                        matched_vals = list(set(filter(r.match, sql_df[column])))

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

                        self.sensitivities(column, column_score, confidence_values, vals)

                        for val in matched_vals:
                            string = "Location from rule based search: %s,  Value: %s" % (
                                column + str(np.where(sql_df[column] == val)[0] + 1), val)
                            # print(string)
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








