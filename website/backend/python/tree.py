import yaml
# import required module
import src.gui as Gui
import src.parser_1 as parser_1
import src.compare as compare

import os
import re
import pandas as pd
import sys
import shutil

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

# directory = "../myfolder/odoo-rules"
# assign directory

 

meta = []

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
    if(l != []):        
        return l[counter-1]
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

def buildInsideTree(inside,patterns):
    insideTree = []

    index = 0
    inside2 = ""
    for i in inside : 
        inside2 = inside[i]
    for pattern in patterns:
        for key in pattern : 
            if key == "pattern-not-inside":
                insideTree = [inside]
                newl = buildInsideTree(pattern,patterns[index+1:])
                if len(newl) == 1 and type(newl[0]) ==str:
                            insideTree.append({"pattern-not":newl[0]})
                else:
                    for e in newl:
                        insideTree.append(e)
            elif key == "pattern-inside" :
                insideTree = [inside]
                newl = buildInsideTree(pattern,patterns[index+1:])
                if len(newl) == 1 and type(newl[0]) ==str:
                            insideTree.append({"pattern":newl[0]})
                else:
                    for e in newl:
                        insideTree.append(e)

        index +=1
        if index == len(patterns) and insideTree == []:
            
            new_inside  = inside_replace(inside2,patterns)
            return new_inside
    if patterns == []:
        insideTree = [inside2]
    return insideTree

def buildDico(tree,value): 
    dico = []
    pointer = 0
    tmp = ""
    breaker = value
    while pointer < len(tree):
        tmp+=tree[pointer]
        if(tree[pointer] == "("):
            breaker += 1
        elif (tree[pointer] == ")"):
            breaker -= 1
            if breaker == 0:
                if(tmp != ')'):
                    dico.append(tmp[:-1])
                return dico
        if tree[pointer] == ";" and tmp !=';':
            dico.append(tmp)
            tmp=""
        elif tree[pointer] == ";" and tmp ==';':
            tmp=""

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
        
        pointer+=1

    return dico
def dicTostr(tmp_dico):
    mystr = ""
    i = 0
    for elem in tmp_dico : 
        if type(elem) == list : 
            tmp_str = dicTostr(elem)
            if tmp_str[-1] == ";" : 
                mystr += '(' + tmp_str[:-1]+');'
            else : 
                if i< len(tmp_dico) and (tmp_dico[i] != "AND" and tmp_dico[i] != 'OR' and tmp_dico[i] != 'NOT'):
                    mystr += '(' + tmp_str+';'
                elif tmp_str[-1] != ")" : 
                    mystr += '(' + tmp_str+');'
                else: 
                    mystr += '(' + tmp_str+')'
    
        else : 
            if i< len(tmp_dico) and (tmp_dico[i] != "AND" and tmp_dico[i] != 'OR' and tmp_dico[i] != 'NOT') and elem[-1]!=';':
                mystr += str(elem) +';'
            else: 
                mystr += str(elem)
        i+=1
            
    return mystr

def dict_to_patterns(metavariable,pattern,dict):
    new_dict = []
    not_cond = False
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
                                not_cond = True
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
def dict_to_reg(metavariable,pattern,dict):
    new_dict = []
    for elem in dict:
        if type(elem) == list:
            new_dict.append(dict_to_reg(metavariable,pattern,elem))
        else:
            if metavariable in elem:
                
                new_dict.append(elem.replace(metavariable,pattern))
            else:
                new_dict.append(elem)
    return new_dict

def buildForMeta(tree):
    tmp_dico = buildDico(tree,0)
    for items in meta : 
        metavaraiable = items['metavariable']
        if 'regex' in items.keys():
            pattern = items['regex']
            tmp_dico = dict_to_reg(metavaraiable,pattern,tmp_dico)
        elif 'patterns' in items.keys():
            pattern = items['patterns'] 
            tmp_dico = dict_to_patterns(metavaraiable,pattern,tmp_dico)
    new_str = dicTostr(tmp_dico)
    return new_str[:-1]

def buildTree(pattern):
    tree = ""
    index = 0 
    inside  = 0 
    for items in pattern :
        
        for labels in items :  
            if inside != 1 : 
                if type(items[labels]) == list:
                    if labels == "patterns" : 
                        tree += "AND(" + buildTree(items[labels]) + ");"
                    elif labels == "pattern-either" : 
                        tree += "OR(" + buildTree(items[labels])+");"
                else : 
                    if labels == "pattern-inside": 
                        val = buildInsideTree(items,pattern[index+1:])
                        if len(val) == 1 and type(val[0]) ==str:
                            tree+=buildTree([{"pattern":val[0]}])
                        else: 
                            if len(val) == 1 : 
                                for keys in val[0]: 
                                        tree+=  buildTree(val)
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
                    elif "regex" in labels and "metavariable" not in labels : 
                        tree += "r:"+items[labels] + ";"
                    elif labels == "metavariable-pattern" or labels =="metavariable-regex":
                        meta.append(items[labels])
                    
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
        # with open("../myfolder/odoo-rules/odoo-external-control-of-file-name-or-path.yaml", 'r') as file:
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
                    
                    

                

