import argparse
import os
from jsonData import jsonData
from csvData import csvData
from sqlData import sqlData
from timeit import default_timer as timer

sensitivity_scores = []

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r') # return an open file handle


def rules():   # function that takes rules from file
    try:
        f = open('rules.txt', 'r')
        rules_dict = {}
        for line in f:
            k, v, s = line.strip().split('->', 2)
            rules_dict[k.strip()] = v.strip()
            sensitivity_scores.append({k.strip():s.strip()})
        f.close()
        return rules_dict
    except ValueError:
        print("ERROR: Make sure rules are in the form 'rule -> regex -> sensitivity' and try again")
        quit()
    

def main():
    parser = argparse.ArgumentParser(description = "PII detection tool")
    parser.add_argument("-i", dest = "filename", required = False, help = "input a data file", metavar = "FILE",
                         type = lambda x: is_valid_file(parser, x))
    parser.add_argument("-d", dest="db", nargs=4, required=False, type=str)
    args = parser.parse_args()
    filename = ""
    if args.filename :
        filename = args.filename.name

    
    rules_dict = rules()   #rules from rules file
    if filename.endswith('.json'):
        jsonObj = jsonData()
        jsonObj.run(rules_dict, sensitivity_scores, filename)
 
    if args.db:
        sqlObj = sqlData()
        sqlObj.sqldb_to_df(args.db, sensitivity_scores, rules_dict)


    if filename.endswith('.csv'):
        csvObj = csvData(filename)
        csvObj.run(rules_dict, sensitivity_scores)
      
    #args.filename.close()

if __name__ == '__main__':
    main()