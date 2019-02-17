import json
from pprint import pprint
import argparse 
import os.path
import re


def get_keys(d_or_l, keys_list):  # function to iterate through a (nested) dictionary OR list and recursively find all keys
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


def find(key, d_or_l):  # function to find values for a specific key in a (nested) dictionary, returns generator
    if hasattr(d_or_l,'items'):
        for k, v in d_or_l.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in find(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in find(key, d):
                        yield result


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
    jdata = json.load(args.filename)
    args.filename.close()

    keys_list = []
    get_keys(jdata, keys_list)
    keys_list = list(set(keys_list))
    rules_dict = rules()
   # key_found = 0

    for rule in rules_dict:
        for key in keys_list:
            if re.search(rule, key, re.IGNORECASE):
             #   print(key + ": " + rule)    # shows the key that was found by the specified rule
             #   key_found += 1
                if rules_dict.get(rule) != '':
                    r = rules_dict.get(rule)
                    mylist = list(find(key, jdata))
                    for value in mylist:
                        if re.match(r, value):
                            print("Match found!: " + value)



if __name__ == '__main__':
    main()
