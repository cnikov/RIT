import yaml
# import required module
import src.gui as Gui
import os
import re
import pandas as pd
import sys
import shutil
import sys
import csv 
# REMOVE SIZE LIMIT ON CSV FILE
csv.field_size_limit(sys.maxsize)


path_to_folder = "myfolder"
if os.path.exists(path_to_folder) and os.path.isdir(path_to_folder):
    shutil.rmtree(path_to_folder)

zip_directory = sys.argv[1]
from zipfile import ZipFile 
  
# loading the temp.zip and creating a zip object 
with ZipFile(zip_directory, 'r') as zObject: 
  
    # Extracting all the members of the zip  
    # into a specific location. 
    zObject.extractall(
        path = "myfolder"
    ) 
tmppath = "myfolder/"
for filename in os.listdir(tmppath):
    directory = os.path.join(tmppath, filename) 

# directory = "../myfolder/semgrep-rules_full"
# assign directory

 

meta = []

"""
This function takes a tree as a string and transform it in a list to simplify the transformation 
:param tree_str: string, the tree that need to be parsed
:return list,int: list that represent the tree and the size of this tree
"""
def parse(tree_str):
    # Counter to track nested parentheses
    counter = 0
    # List to store the parsed tree structure
    tree_lst = []
    # Temporary string to store intermediate values
    tmp_str = ""
    # Index to track the current position in the tree_str
    index = 0
    # Loop through each character in the tree_str
    while index < (len(tree_str)) : 
        # Check for end of subtree and append to tree_lst
        if(tree_str[index] == ";" and counter == 0):
            tree_lst.append(tmp_str)
            tmp_str = ""
        # Check for opening parentheses and increment counter
        elif tree_str[index] == "(":
            counter+=1
            if counter > 0:
                tmp_str+=tree_str[index]
        # Check for closing parentheses and decrement counter
        elif tree_str[index] == ")" : 
            counter-=1
            if counter == -1:
                if tmp_str != "":
                    tree_lst.append(tmp_str)
                return tree_lst,index
            else:
                tmp_str+= tree_str[index]
                
        # Check for AND, OR and NOT operators and parse accordingly
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
        # Append any other characters to the temporary string
        else:
            tmp_str+= tree_str[index]
        index +=1
    # If the tree_lst is empty, return the entire tree_str as a single subtree
    if tree_lst == []:
        return [tree_str],len(tree_str)
    return tree_lst , index

"""
This function take a string and transform it in regular expression
:param val1: string
:return regex1: regex
"""
def toregex(val1):
    # Use re.escape to escape all special characters in val1
    regex1 = re.escape(val1)
    # Replace the special sequence '\\.\\.\\.' with '.*'
    if re.search(r"\\\.\\\.\\\.", regex1):
        regex1 = re.sub(r"\\\.\\\.\\\.", r".*", regex1)
    # Replace the special sequence '\\$[A-Z]+' with '.*'
    if re.search(r"\\\$", regex1):
        regex1 = re.sub(r"\\\$[A-Z]+", r".*", regex1)
    return regex1

"""
This function find the number of occurence that a val appears in a string 
params: string,val,counter: string string to check ,string value that wze want to check in the string,int the counter says which occurence
return: int return the index of the occurence
"""
def find_occ(string, val, counter):
    # If length of value is larger than string, return 0
    if len(val) >= len(string):
        return 0
    # List to store indices of value in string
    l = []
    # Loop through string and check if value matches at any position
    for i in range(len(string) - len(val)):
        if string[i:i + len(val)] == val:
            l.append(i)
    # If any indices are found, return the index at the specified counter
    if l:
        return l[counter - 1]
    # If no indices are found, return 0
    return 0


def inside_replace(inside,pattern):
    d = []
    occurences = inside.count('...')
    for items in range(len(pattern)) : 
        if occurences >1 : 
            d2 = {"pattern-either":[]}
            for occ in range(occurences):
                count = find_occ(inside,"...",occ)
                for key in pattern[items]:
                    if key == "pattern-either":
                        for nest in pattern[items][key]:
                            for key2 in nest:
                                # print(nest)
                                if type(nest[key2]) == list:
                                    for e in nest[key2]: 
                                        for k in e:
                                            if inside[count-1]=='(' and inside[count+3] == ')':
                                                d2["pattern-either"].append({key2:inside[:count]+'...,'+e[k]+',' +inside[count:]})
                                            elif type(e[k]) == list: 
                                                d2["pattern-either"].append({key2:inside[:count]+'...\n'+buildTree(e[k]) +'\n'+inside[count:]})
                                            else: 
                                                d2["pattern-either"].append({key2:inside[:count]+'...\n'+e[k] +'\n'+inside[count:]})
                                else: 
                                    if inside[count-1] == '(' and inside[count+3] == ')':
                                        d2["pattern-either"].append({key2:inside[:count]+'...,'+nest[key2] +','+inside[count:]})
                                    else: 
                                        d2["pattern-either"].append({key2:inside[:count]+'...\n'+nest[key2] +'\n'+inside[count:]})
                    elif type(pattern[items][key]) == str:
                        if inside[count-1] == '(' and inside[count+3] == ')':
                            d2["pattern-either"].append({key:inside[:count]+'...,'+pattern[items][key]+','+inside[count:]})
                        else: 
                           d2["pattern-either"].append({key:inside[:count]+'...\n'+pattern[items][key]+'\n'+inside[count:]}) 
            d.append(d2)

        elif occurences == 1 :
            count = find_occ(inside,"...",0)
            for key in pattern[items]:
                if key == "pattern-either":
                    d3 = {key:[]}
                    for nest in pattern[items][key]:
                        for key2 in nest : 
                            # print(nest)
                            if type(nest[key2]) == list : 
                                for e in nest[key2]: 
                                    for k in e:
                                        if type(e[k] )== str:
                                            if inside[count-1] == '(' and inside[count+3] == ')':
                                                d3[key].append({key2:inside[:count]+'...,'+e[k]+',' +inside[count:]})
                                            else:
                                                d3[key].append({key2:inside[:count]+'...\n'+e[k]+'\n' +inside[count:]})
                            else:
                                if inside[count-1] == '(' and inside[count+3] == ')':
                                    d3[key].append({key2:inside[:count]+'...,'+nest[key2] +','+inside[count:] })
                                else:
                                    d3[key].append({key2:inside[:count]+'...\n'+nest[key2] +'\n'+inside[count:] })
                                
                    d.append(d3)
                elif type(pattern[items][key]) ==str: 
                    if inside[count-1] == '(' and inside[count+3] == ')':
                        d.append({key:inside[:count]+'...,'+pattern[items][key]+',' +inside[count:]})     
                    else:
                        d.append({key:inside[:count]+'...\n'+pattern[items][key]+'\n' +inside[count:]})     
    return d

"""
This function is made to build the part of the tree that correspond to a pattern inside
:params inside,patterns: string, dict
:return string: return inside with the patterns correctly added
"""
def buildInsideTree(inside, patterns):
    # Initialize the inside tree as an empty list
    insideTree = []
    # Loop through each pattern
    index = 0
    inside2 = ""
    for i in inside:
        inside2 = inside[i]
    for pattern in patterns:
        # Loop through each key in the pattern
        for key in pattern:
            # Check if the key is the focus metavariable
            if key == "focus-metavariable":
                return [inside[i]]
            # Check if the key is pattern not inside
            if key == "pattern-not-inside":
                insideTree = [inside]
                newl = buildInsideTree(pattern, patterns[index+1:])
                if len(newl) == 1 and type(newl[0]) == str:
                    insideTree.append({"pattern-not": newl[0]})
                else:
                    for e in newl:
                        insideTree.append(e)
            # Check if the key is pattern inside
            elif key == "pattern-inside":
                insideTree = [inside]
                newl = buildInsideTree(pattern, patterns[index+1:])
                if len(newl) == 1 and type(newl[0]) == str:
                    insideTree.append({"pattern": newl[0]})
                else:
                    for e in newl:
                        insideTree.append(e)
        index += 1
        if index == len(patterns) and insideTree == []:
            new_inside = inside_replace(inside2, patterns)
            return new_inside
    if patterns == []:
        insideTree = [inside2]
    return insideTree


"""
This method transform the tree into a list to change the metavariable easily
:params tree,value: tree is the tree that we want to transform and value is there to handle the breaker for the recursion
:return tree: list[] return the tree transformed into a list
"""
def buildDico(tree, value): 
    # Create a list for storing dictionaries
    dico = []
    # Set the pointer to 0
    pointer = 0
    # Create a temporary string for holding characters
    tmp = ""
    # Set the breaker variable
    breaker = value
    # Start the loop
    while pointer < len(tree):
        # Add the current character to the temporary string
        if not(tmp == "" and tree[pointer] == ";") : 
            tmp += tree[pointer]    
        # If the character is "(" increment the breaker variable
        if(tree[pointer] == "("):
            breaker += 1
        # If the character is ")" decrement the breaker variable
        # If the breaker variable is 0, return the dico list
        elif (tree[pointer] == ")"):
            breaker -= 1
            if breaker == 0:
                if(tmp != ')'):
                    dico.append(tmp[:-1])
                return dico
        # If the character is ";" and the temporary string is not ';',
        # add the temporary string to the dico list and reset the temporary string
        if tree[pointer] == ";" and tmp !=';':
            dico.append(tmp)
            tmp=""
        # If the temporary string is "AND", add "AND" to the dico list and call the function recursively
        elif tmp == "AND":
            dico.append("AND")
            dico.append(buildDico(tree[pointer+2:],1))
            pointer+=2
            breaker_tmp = 1
            breaker+=1
            tmp = ""
            while breaker_tmp != 0 and pointer < len(tree):
                now = tree[pointer]
                if now =="(":
                    breaker_tmp += 1
                    breaker+=1
            
                elif tree[pointer] == ")":
                    breaker_tmp -=1
                    breaker -=1
                    if breaker ==0:
                        return dico
                pointer+=1
            pointer -=1
        # If the temporary string is "OR", add "OR" to the dico list and call the function recursively
        elif tmp =="OR":
            dico.append("OR")
            dico.append(buildDico(tree[pointer+2:],1))
            pointer+=2
            breaker_tmp = 1
            breaker+=1
            tmp = ""
            while breaker_tmp != 0 and pointer < len(tree):
                now = tree[pointer]
                if now =="(":
                    breaker_tmp += 1
                    breaker+=1
            
                elif now== ")":
                    breaker_tmp -=1
                    breaker -=1
                    if breaker ==0:
                        return dico
                pointer+=1
            pointer-=1
        # Increment the pointer
        pointer+=1
    # Return the dico list
    return dico

"""
Retransform the dictionary with the tree to a tree in string
:params tmp_dico : [] list with the dico struct
:return : str, the retransformed tree
"""
def dicTostr(tmp_dico):
    # Initialize mystr to empty string
    mystr = ""
    # Initialize i to 0
    i = 0
    # Iterate over each element in tmp_dico
    for elem in tmp_dico:
        # Check if elem is a list
        if type(elem) == list:
            # Convert the list to a string using dicTostr
            tmp_str = dicTostr(elem)
            # Check if the last character of tmp_str is a semicolon
            if tmp_str[-1] == ";":
                # Append the string surrounded by parentheses and a semicolon to mystr
                mystr += '(' + tmp_str[:-1]+');'
            else:
                # Check if we're at the last element or the next element is AND, OR, or NOT
                if i< len(tmp_dico) and (tmp_dico[i] != "AND" and tmp_dico[i] != 'OR' and tmp_dico[i] != 'NOT'):
                    # Append the string surrounded by parentheses and a semicolon to mystr
                    mystr += '(' + tmp_str+';'
                # Check if the last character of tmp_str is a parenthesis
                elif tmp_str[-1] != ")":
                    # Append the string surrounded by parentheses and a semicolon to mystr
                    mystr += '(' + tmp_str+');'
                else:
                    # Append the string surrounded by parentheses to mystr
                    mystr += '(' + tmp_str+')'
        else:
            # Check if we're at the last element or the next element is AND, OR, or NOT
            if i< len(tmp_dico) and (tmp_dico[i] != "AND" and tmp_dico[i] != 'OR' and tmp_dico[i] != 'NOT') and elem!="" and elem[-1]!=';':
                # Append the string to mystr and a semicolon
                mystr += str(elem) +';'
            else:
                # Append the string to mystr
                mystr += str(elem)
        # Increment i
        i+=1 
    # Return the final string
    return mystr


"""
This function is for the metavariable and it add the metavariables patterns into the dict
:params metavariable,pattern,dict: string,[],[]
:return new_dict : []
"""
def dict_to_patterns(metavariable,pattern,dict):
    new_dict = []
    either_cond = False
    for elem in dict:
        if type(elem) == list:
            new_dict.append(dict_to_patterns(metavariable,pattern,elem))
        else:
            if metavariable in elem:
                tmp = []
                for sub_pat in pattern: 
                    if 'pattern-either' in sub_pat.keys():
                            either_cond = True
                            for either in sub_pat['pattern-either']:

                                for val in either.values():
                                    if 'patter-not' in either.keys():
                                        not_cond = True
                                        tmp.append('NOT')
                                        tmp.append([elem.replace(metavariable,val)])
                                        tmp.append(elem.replace(metavariable,'...'))
                                    else : 
                                        tmp.append(elem.replace(metavariable,val))
                    else:                
                        for val in sub_pat.values() :                       
                            if 'pattern-not' in sub_pat.keys() or 'pattern-not-regex' in sub_pat.keys() : 
                                new_dict.append('NOT')
                                new_dict.append([elem.replace(metavariable,val)])
                                new_dict.append(elem.replace(metavariable,'...'))
                            else : 
                                tmp.append(elem.replace(metavariable,val))
                if either_cond == True:
                    new_dict.append('OR')
                if len(tmp) ==1  :
                    new_dict.append(tmp[0])
                elif len(tmp) >1: 
                    new_dict.append(tmp)
            else:
                new_dict.append(elem)
    return new_dict

"""
handle the case of metavariable regex
"""
def dict_to_reg(metavariable, pattern, dict):
    # Create a new list
    new_dict = []
    # Iterate through the dictionary
    for elem in dict:
        # Check if the element is a list
        if type(elem) == list:
            # If so, recursively call the function
            new_dict.append(dict_to_reg(metavariable, pattern, elem))
        else:
            # Check if the metavariable is in the element
            if metavariable in elem:
                # Replace the metavariable with the pattern
                new_dict.append(elem.replace(metavariable, pattern))
            else:
                # If not, keep the element as is
                new_dict.append(elem)
    # Return the new list
    return new_dict


"""
This function build a tree by replacing the metavariable
:params tree: string 
:return new_str: string (updated tree)
"""
def buildForMeta(tree):
    # Create a dictionary for metavariables
    tmp_dico = buildDico(tree,0)
    
    # Iterate through the metavariables in the meta list
    for items in meta : 
        metavaraiable = items['metavariable']
        
        # If there is a regex pattern for the metavariable
        if 'regex' in items.keys():
            pattern = items['regex']
            tmp_dico = dict_to_reg(metavaraiable,pattern,tmp_dico)
        
        # If there are patterns for the metavariable
        elif 'patterns' in items.keys():
            pattern = items['patterns'] 
            tmp_dico = dict_to_patterns(metavaraiable,pattern,tmp_dico)
    # Convert the dictionary to a string
    new_str = dicTostr(tmp_dico)
    # Return the string without the last character
    return new_str[:-1]

"""
Build a tree inn string for the csv from the yaml file with all the patterns
:params pattern: {} content of the yaml rule
:return tree : string the tree build for the csv
"""
def buildTree(pattern):
    # Initialize tree string and counters
    tree = ""
    index = 0
    inside = 0
    # Loop through pattern elements
    for items in pattern:
        # Loop through label-value pairs within pattern element
        for labels in items:
            # If not inside an inside-not-regex construct
            if inside != 1:
                # Handle lists, ORs, ANDs, NOTs, and pattern elements
                if type(items[labels]) == list:
                    if labels == "patterns":
                        tree += "AND(" + buildTree(items[labels]) + ");"
                    elif labels == "pattern-either":
                        tree += "OR(" + buildTree(items[labels])+");"
                else:
                    if labels == "pattern-inside":
                        val = buildInsideTree(items,pattern[index+1:])
                        if len(val) == 1 and type(val[0]) ==str:
                            tree+=buildTree([{"pattern":val[0]}])
                        else: 
                            if len(val) == 1 : 
                                for keys in val[0]: 
                                        tree+= buildTree(val)
                            else: 
                                tree+= "(" + buildTree(val)+");"
                        inside = 1
                    elif labels == "pattern-not-inside":
                        val = buildInsideTree(items,pattern[index+1:])
                        if len(val) == 1 and type(val[0]) ==str:
                            tree+=buildTree([{"pattern-not":val[0]}])
                        else: 
                            tree+= "NOT(" + buildTree(val)+");"
                        inside = 1
                    elif labels == "pattern-not-regex":
                        tree += "NOT(r:"+items[labels]+");"
                    elif labels == "pattern-not":
                        tree += "NOT("+items[labels]+");"
                    elif "regex" in labels and "metavariable" not in labels: 
                        tree += "r:"+items[labels] + ";"
                    elif labels == "metavariable-pattern" or labels =="metavariable-regex":
                        meta.append(items[labels])
                    
                    elif "pattern" in labels:
                        tree += items[labels] + ";"
        index+=1
    tree = tree.replace("\n", "\\n")
    return tree[:-1]


dataframe = {"id":[],"tree":[]}
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
# for filename in range(1):
    # checking if it is a file
    if os.path.isfile(f):
    # if True:
        with open(f, 'r') as file:
        # with open("../myfolder/rule_set_3/hardcoded-http-auth-in-controller.yaml", 'r') as file:
            meta.clear()
            rules = yaml.safe_load(file)     
            item = rules["rules"]
            # print(item)
            finaltree = ""
            for labels in item[0]:
                if labels == "patterns" :
                    finaltree = "AND(" + buildTree(item[0][labels]) + ")"
                elif labels == "pattern-either" : 
                    finaltree = "OR(" + buildTree(item[0][labels]) + ")"
                elif "pattern" in labels : 
                    finaltree = "(" + buildTree([{labels:item[0][labels]}]) + ")"
                    finaltree = finaltree.replace("\n", "\\n")
            if(meta != []):
                finaltree = buildForMeta(finaltree)
            if finaltree != '()' : 
                dataframe["id"].append(item[0]["id"])
                # dataframe["tree"].append(parse(finaltree)[0])
                dataframe["tree"].append(finaltree)
df = pd.DataFrame(data=dataframe)
df = df.replace(' ', '', regex=True)
df = df.replace("',", "';", regex=True)
df.to_csv('out2.csv',index=False)  
Gui.run_gui()
                    
                    

                

