import csv
import re

values = None

def parse_val(val, key):
    '''Parse value and convert it to appropriate type.
       Check for boolean, empty string, nan, pandas Interval, and numbers.
    '''
    if val == '' or val == '*' or val.lower() == 'nan': return float('nan')
    elif val[0] == '(' or val[0] == '[' or val[0] == ']':
        return parse_interval(val, key)
    elif val.lower() == 'false': return False
    elif val.lower() == 'true': return True
    elif type(val.lower().strip()) == str : return val.lower()
    else:
        try:
            new_val = float(val)
            return new_val
        except ValueError:
            raise ValueError("Value doesn't have appropriate format: " + str(val))

def parse_interval(val, key):
    #get characteristics of interval (closed on the left-side, right-side, both or neither)
    leftClosed = val[0] == '['
    if not leftClosed and not (val[0] == '(' or val[0] == ']'):
        raise ValueError("Value given doesn't have the proper format for a pandas.Interval: " + str(val))
    rightClosed = val[len(val)-1] == ']'
    if not rightClosed and not (val[len(val)-1] == ')' or val[len(val)-1] == '['):
        raise ValueError("Value given doesn't have the proper format for a pandas.Interval: " + str(val))
    if leftClosed and rightClosed: closed = 'both'
    elif leftClosed and not rightClosed: closed = 'left'
    elif not leftClosed and rightClosed: closed = 'right'
    else: closed = 'neither'
    mylist = []
    i = 1
    left_str = ''
    while i < len(val):
        if val[i] == ';' or i == len(val)-1:
            try:
                left_val = left_str  
                mylist.append(left_val)
                left_str = ''
                i+=1
            except ValueError:
                raise ValueError("Value given doesn't have the proper format for being in the rule set: " + str(val))
        else : 
            left_str+=val[i]
            i+=1 
    if key == "metavariable" or key == "metavariable-pattern" or key == "metavariable-pattern-not" or key == "metavariable-pattern-either":
        #for each metavariable
        #problem if VAL and VALUE in the same rule... need a full match but if one is shorter -->  start with the longer ones and replace them direclty
        global values
        keyval = {}
        for string in mylist:  #sort metavariables' name by length 
            metavariable = ""
            i = 0
            while string[i] != ":":
                metavariable += string[i]
                i+=1
            regex = "("
            regex += string[i+1:]
            regex += ")"
            keyval[metavariable] = regex
        keyval = dict(sorted(keyval.items(), key=lambda x: len(x[0]), reverse=True)) #tri en fonction de la taille de la metavariable, reverse
        
        for meta in keyval.keys():
            newdict = {}
            regex = keyval[meta]
            for i in values.keys():
                value = values[i]
                if type(value) == list:
                    escaped = re.escape(re.escape(meta))
                    newlist = []
                    for j in range(len(value)):
                        item = re.escape(value[j])
                        if re.search(escaped, item):
                            itembis = "r:"
                            itembis += re.sub(escaped, regex, item)
                            newlist.append(itembis)
                        else : 
                            newlist.append(value[j])
                    newdict[i] = newlist
                            
                elif not isinstance(value,float) : #not a list but a single item
                        escaped = re.escape(re.escape(meta))
                        newval = re.escape(value)
                        if re.search(escaped, newval):
                            newval = re.sub(escaped, regex, newval)
                            newdict[i] = newval
                        else : 
                            newdict[i] = value
            values = newdict
        return float('nan')  #comme ca on prends plus metavariable en compte :)
    return mylist 

def parse(tree_str):
    counter = 0
    tree_lst = []
    tmp_str = ""
    index = 0
    while index < (len(tree_str)) : 
        if(tree_str[index] == ";" and counter == 0):
            tree_lst.append(tmp_str)
            tmp_str = ""
        elif tree_str[index] == "(":
            counter+=1
            if counter > 0:
                tmp_str+=tree_str[index]
        elif tree_str[index] == ")" : 
            counter-=1
            if counter == -1:
                if tmp_str != "":
                    tree_lst.append(tmp_str)
                return tree_lst,index
            else:
                tmp_str+= tree_str[index]
        elif tree_str[index:index+3] == "AND" or tree_str[index:index+3] == "NOT" :
            tree_lst.append(tree_str[index:index+3])
            mystr, myindex = parse(tree_str[index+4:])
            tree_lst.append(mystr)
            index = index + myindex +5
        elif tree_str[index:index+2] == "OR":
            tree_lst.append(tree_str[index:index+2])
            mystr, myindex = parse(tree_str[index+3:])
            tree_lst.append(mystr)
            index = index + myindex +4
        else:
            tmp_str+= tree_str[index]
        index +=1
    if tree_lst == []:
        return [tree_str],len(tree_str)
    return tree_lst , index


''' 
Parse csv and returns list of dictionnaries representing the rules
:params csv_name : string name of the csv file
:return rules: tree with the rules
'''
def parse_csv(csv_name):
    rules = []
    with open(csv_name, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for r in reader:
            global values
            values = r
            for key, val in values.items():
                if not key == "Rec" and not key == "Recommendation":
                    if isinstance(val,str):
                        try:
                            values[key] = float(val)
                        except ValueError:
                            values[key] = val
            rules.append(values)
    return rules


