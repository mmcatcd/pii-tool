import argparse
import os
from jsonData import jsonData
from csvData import csvData


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r') # return an open file handle


def rules():   # function that takes rules from file and turns them into a dictionary of format rule:RegEx
    try:
        f = open('rules.txt', 'r')
        rules_dict = {}
        for line in f:
            k, v = line.strip().split('->')
            rules_dict[k.strip()] = v.strip()
        f.close()
        return rules_dict
    except ValueError:
        print("ERROR: Make sure rules are in the form 'rule -> regex' and try again")
        quit()
    

def main():
    parser = argparse.ArgumentParser(description = "PII detection tool")
    parser.add_argument("-i", dest = "filename", required = True, help = "input json file", metavar = "FILE",
                         type = lambda x: is_valid_file(parser, x))
    args = parser.parse_args()
    filename = args.filename.name
    rules_dict = rules()   #rules from rules file

    if filename.endswith('.json'):
        jsonObj = jsonData()
        report_data = jsonObj.run(rules_dict, filename)
        jsonObj.write_report(report_data)
        
    
    if filename.endswith('.sql'):
        print("Do something...")

    if filename.endswith('.csv'):
        csvObj = csvData()
        report_data = csvObj.run(rules_dict, filename)
        csvObj.write_report(report_data)

    args.filename.close()

if __name__ == '__main__':
    main()