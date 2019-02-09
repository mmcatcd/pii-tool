import json
import pprint
import argparse 
import os.path
import re

def get_keys(d_or_l, keys_list):  # function to iterate through a dictionary OR list and recursively find all keys
    if isinstance(d_or_l, dict):
        for k, v in iter(sorted(d_or_l.items())):
            if isinstance(v, list):
                get_keys(v, keys_list)
            elif isinstance(v, dict):
                get_keys(v, keys_list)
            keys_list.append(k)
    elif isinstance(d_or_l, list):
        for i in d_or_l:
            if isinstance(i, list):
                get_keys(i, keys_list)
            elif isinstance(i, dict):
                get_keys(i, keys_list)
    else:
        print("Skipping item of type: {}".format(type(d_or_l)))

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r') # return an open file handle
  
def main():
    parser = argparse.ArgumentParser(description = "PII detection tool")
    parser.add_argument("-i", dest = "filename", required = True, help = "input json file", metavar = "FILE",
                         type = lambda x: is_valid_file(parser, x))
    args = parser.parse_args()
    emp_dict = json.load(args.filename)
    args.filename.close()

    with open('rules.txt') as rules_file:
         rules = [line.rstrip() for line in rules_file] # get rid of pesky new line character

    count = 0
    keys_list = [] 
    get_keys(emp_dict, keys_list)
    keys_list = list(set(keys_list))  # remove duplicate keys from 'keys_list'
   # print(keys_list)
    for rule in rules:
        for key in keys_list:
            if re.search(rule, key, re.IGNORECASE):
                count += 1
   # print("{}".format((sensitive_items * 100) / count) + "% of this database is potentially non-GDPR compliant")
    #print(count)

if __name__ == '__main__':
    main()
