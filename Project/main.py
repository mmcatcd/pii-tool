import mysql.connector
import pandas as pd

class main:

    def __init__(self):

# connect to database
    def connect_to_db(self, host, user, password, database, table):
        mydb = mysql.connector.connect(
            host= host,  #"localhost" #127.0.0.1
            user=user,   #"root"
            password=password,  #""
            database=database   #"rob_dump"
        )
        mycursor = mydb.cursor()

        # access column information
        mycursor.execute("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'" + table + "'") # e.g. pi
        col_schema_result = mycursor.fetchall() # fetchall() method fetches all rows from the last execute statement

        sql_to_dataframe(self, col_schema_result, mycursor, table)


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
                    run_pii(sql_df) # a df for pii tool to check



