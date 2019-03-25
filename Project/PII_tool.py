import argparse
import os
from jsonData import jsonData
from csvData import csvData

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
        print("ERROR: Make sure rules are in the form 'rule -> regex -> sensitivity score' and try again")
        quit()
    

def main():
    parser = argparse.ArgumentParser(description = "PII detection tool")
    parser.add_argument("-i", dest = "filename", required = False, help = "input a data file", metavar = "FILE",
                         type = lambda x: is_valid_file(parser, x))
    args = parser.parse_args()
    try:
        filename = args.filename.name
    except AttributeError:
        pass
    
    rules_dict = rules()   #rules from rules file
    if filename.endswith('.json'):
        jsonObj = jsonData()
        jsonObj.run(rules_dict, sensitivity_scores, filename)
        
        
    if filename.endswith('.sql'):
        print("")
        #sqlObj = sqlData()
        #report_data = sqlObj.run(rules_dict, sql_df)
        #sqlObj.write_report(report_data)

    if filename.endswith('.csv'):
        csvObj = csvData()
        csvObj.run(rules_dict, sensitivity_scores, filename)

    args.filename.close()

if __name__ == '__main__':
    main()