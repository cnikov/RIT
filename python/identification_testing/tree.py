import yaml
# import required module
import os
import re
import pandas as pd
# assign directory
directory = 'odoo-rules'
 
# iterate over files in
# that directory

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

def toregex(val1):
    regex1 = re.escape(val1)
    if re.search(r"\\\.\\\.\\\.", regex1):
        regex1 =  re.sub(r"\\\.\\\.\\\.", r".*", regex1)
    if re.search(r"\\\$", regex1):
        regex1 =  re.sub(r"\\\$[A-Z]+", r".*", regex1)
    return regex1

def find_occ(string,val,counter):
    if len(val) >= len(string):
        return 0 
    l = []
    for i in range(len(string)-len(val)):
        if string[i:i+len(val)] == val:
            l.append(i)
    return l[counter]


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
                                d2["pattern-either"].append({key2:inside[:count]+nest[key2] +inside[count+1:]})
                    else:
                        d2["pattern-either"].append({key:inside[:count]+pattern[items][key] +inside[count+1:]})
            d.append(d2)

        elif occurences == 1 :
            count = find_occ(inside,"...",0)
            for key in pattern[items]:
                if key == "pattern-either":
                    d3 = {key:[]}
                    for nest in pattern[items][key]:
                        for key2 in nest : 
                            # print(nest)
                            d3[key].append({key2:inside[:count]+nest[key2] +inside[count+1:] })
                    d.append(d3)
                else: 
                    d.append({key:inside[:count]+pattern[items][key] +inside[count+1:]})     
    return d

def buildInsideTree(inside,patterns):
    insideTree = []
    index = 0
    inside2 = ""
    for i in inside : 
        inside2 = inside[i]
    for pattern in patterns:
        for key in pattern : 
            if key == "pattern-inside":
                insideTree = [inside]
                newl = buildInsideTree(pattern,patterns[index+1:])
                for e in newl:
                    insideTree.append(e)

        index +=1
        if index == len(patterns) and insideTree == []:
            
            new_inside  = inside_replace(inside2,patterns)
            return new_inside
    return insideTree

def buildTree(pattern):
    tree = ""
    index = 0 
    for items in pattern :

        for labels in items :  
            if type(items[labels]) == list:
                if labels == "patterns" : 
                    tree += "AND(" + buildTree(items[labels]) + ");"
                elif labels == "pattern-either" : 
                    tree += "OR(" + buildTree(items[labels])+");"
            else : 
                if labels == "pattern-inside": 
                    tree+= buildTree(buildInsideTree(items,pattern[index+1:])) +";"
                elif labels == "pattern-not-regex":
                    tree += "NOT(r:"+items[labels]+");"
                elif labels == "pattern-not":
                    tree += "NOT("+items[labels]+");"
                elif "regex" in labels and "metavariable" not in labels : 
                    tree += "r:"+items[labels] + ";"
                elif labels == "metavariable-pattern" or labels =="metavariable-regex":
                    for dic in items[labels] : 
                        for key in dic : 
                            if "pattern" in key : 
                                substring =buildTree(items[labels][key])
                                tree = tree.replace( items[labels]["metavariable"],substring)
                
                elif "pattern" in labels:
                     tree += items[labels] + ";"
        index+=1
    tree  = tree.replace("\n", "\\n")
    return tree[:-1]


dataframe = {"id":[],"tree":[]}

for filename in os.listdir(directory):
    f = os.path.join(directory, filename)


# for filename in range(1):

    # checking if it is a file
    if os.path.isfile(f):
    # if True:
        with open(f, 'r') as file:
        # with open("odoo-rules/odoo-kn64kbnw.yaml", 'r') as file:

            rules = yaml.safe_load(file)     

            item = rules["rules"]
            print(item)
            # print(item)
            finaltree = ""
            for labels in item[0]:
                if labels == "patterns" :
                    finaltree = "AND(" + buildTree(item[0][labels]) + ")"
                elif labels == "pattern-either" : 
                    finaltree = "OR(" + buildTree(item[0][labels]) + ")"
                elif "pattern" in labels : 
                    print(labels)
                    finaltree = "(" + buildTree([{labels:item[0][labels]}]) + ")"
                    finaltree = finaltree.replace("\n", "\\n")

            # print(finaltree)
            dataframe["id"].append(item[0]["id"])
            # dataframe["tree"].append(parse(finaltree)[0])
            dataframe["tree"].append(finaltree)
df = pd.DataFrame(data=dataframe)
df = df.replace(' ', '', regex=True)
df = df.replace("',", "';", regex=True)

df.to_csv('out2.csv',index=False) 

                    
                    

                

