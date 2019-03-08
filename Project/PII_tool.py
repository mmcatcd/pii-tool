import argparse
import os
from jsonData import jsonData


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r') # return an open file handle


def rules():    # function that takes rules from file and turns them into a dictionary of format rule:RegEx
    f = open('rules.txt', 'r')
    rules_dict = {}
    for line in f:
        k, v = line.strip().split(':')
        rules_dict[k.strip()] = v.strip()
    f.close()
    return rules_dict


def main():
    parser = argparse.ArgumentParser(description = "PII detection tool")
    parser.add_argument("-i", dest = "filename", required = True, help = "input json file", metavar = "FILE",
                         type = lambda x: is_valid_file(parser, x))
    args = parser.parse_args()
    filename = args.filename.name
    rules_dict = rules()   #rules from rules file

    if filename.endswith('.json'):
        jsonObj = jsonData()
        jsonObj.run(rules_dict, filename)
        args.filename.close()
    
    elif filename.endswith('.sql'):
        print("Do something...")

    elif filename.endswith('.csv'):
        print("Do something...")


if __name__ == '__main__':
    main()