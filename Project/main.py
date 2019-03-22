import mysql.connector
import pandas as pd
import re

class main:

    def __init__(self):

# connect to database
    def connect_to_db(self, host, user, password, database, table):
        mydb = mysql.connector.connect(
            host=host,  #"localhost" #127.0.0.1
            user=user,   #"root"
            password=password,  #""
            database=database   #"rob_dump"
        )
        mycursor = mydb.cursor()

        # access column information
        mycursor.execute("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'" + table + "'") # e.g. pi
        col_schema_result = mycursor.fetchall() # fetchall() method fetches all rows from the last execute statement

        return col_schema_result, mycursor, table # sql_to_dataframe(self, col_schema_result, mycursor, table)


    def sql_to_dataframe(self, col_schema_result, mycursor, table):
        col_count = 0
        for col_schema_line in col_schema_result:
            col_count +=1
            for rule in rules_dict: ###
                if rule in col_schema_line:
                    print(rule, "located at column ", col_count)
                    mycursor.execute("SELECT " + rule + " FROM " + table)
                    data = mycursor.fetchall()
                    sql_df = pd.DataFrame(data) # panda data frame set up
                    print(sql_df)

        return sql_df # run(self, rules_dict, sql_df) # a df for pii tool to check


    def run(self, rules_dict, sql_df):
        report_data = []
        for rule in rules_dict:
            index = 0
            for col, row in sql_df:
                if re.search(rule, col, re.IGNORECASE):
                    if rules_dict.get(rule) != '':
                        r = re.compile(rules_dict.get(rule))
                        if r.match(row):
                            string = "Location: %s, Value: %s" % (index, row)
                            report_data.append(string)

        return report_data

    def write_report(self, report_data):
        writefile = open('report.txt', 'w+')
        [writefile.write(line + "\n") for line in report_data]








