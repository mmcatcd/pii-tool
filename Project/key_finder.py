import json
import pprint


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


if __name__ == '__main__':
    with open('employees.json', 'r') as f:  # create a dictionary object from json file to work on
        emp_dict = json.load(f)

    sensitive_keys = ['name', 'firstName', 'lastName', 'phoneNumber', 'emailAddress']
    sensitive_items = 0
    count = 0
    keys_list = []
    get_keys(emp_dict, keys_list)
    keys_list = list(set(keys_list))  # remove duplicate keys from 'keys_list'
    for key in keys_list:
        count += 1
        if key in sensitive_keys:
            sensitive_items += 1
    pprint.pprint(keys_list)  # nicer view of keys in the output than print()
    print("{}".format((sensitive_items * 100) / count) + "% of this database is potentially non-GDPR compliant")
