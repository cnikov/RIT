import yaml
# import required module
import os
import re
import pandas as pd
# assign directory
directory = 'odoo-rules'
 
# iterate over files in
# that directory
pattern = []
pattern_not = []
pattern_either = []
metavariable_pattern = []
metavariable_pattern_not = []
metavariable_pattern_either = []
metavariable = {}
d = {}


def sort_metavariables(dict,condition,condition2) :
    # print(dict)
    for keys in dict:
        if "metavariable" in keys : 
            pass
        elif type(dict[keys]) == list:
            for elem in dict[keys] : 
                for key in elem : 
                    # print("elem is : ",elem)
                    if "pattern" in key and "not" in key and "either" in keys: 
                        sort_metavariables(elem,True,True)
                    elif "pattern" in key and "not" in key : 
                        sort_metavariables(elem,True,False)
                    elif "pattern" in key and "either" in keys:  
                        if condition : 
                            sort_metavariables(elem,True,True)
                        else :
                            sort_metavariables(elem,False,True)
                    elif "pattern" in key :
                        if condition : 
                            sort_metavariables(elem,True,False)
                        else :
                            sort_metavariables(elem,False,False)
                    
        else:
            # print("dict is :",dict)
            if condition:
                if "regex" in keys : 
                    metavariable_pattern_not.append("re:"+dict[keys])
                else: 
                    metavariable_pattern_not.append(dict[keys])
            else : 
                if condition2:
                    if "regex" in keys : 
                        metavariable_pattern_either.append("re:"+dict[keys])
                    
                    else: 
                        metavariable_pattern_either.append(dict[keys])
                else:
                    if "regex" in keys : 
                        metavariable_pattern.append("re:"+dict[keys])
                    
                    else: 
                        metavariable_pattern.append(dict[keys])

def find_occ(string,val,counter):
    if len(val) >= len(string):
        return 0 
    l = []
    for i in range(len(string)-len(val)):
        if string[i:i+len(val)] == val:
            l.append(i)
    return l[counter]

def clean(list):
    index = 0
    print("here is the list : ", list)
    while ( "pattern-inside" not in list[index].keys() and index <len(list)-1):
        print(list[index].keys())
        index +=1
    if( index == len(list)-1):
        return list
    return list[index:]

def pattern_inside(list,val):
    list2 = clean(list.copy())
    l = []
    if len(list2) == 2:
        for i in range(val.count('...')):
            count = find_occ(val,"...",i)
            key = list2[1].keys()
            if  "pattern" in key and "not" in key :
                l.append({"pattern-not":val[:count]+str(list2[1]["pattern-not"][:-1])+ val[count:]})
            elif "pattern" in key :
                l.append({"pattern" : val[:count]+str(list2[1]["pattern"][:-1])+ val[count:]})
    elif len(list2) >2 :
        list3 = [] 
        for j in range(1,len(list2)):
            for i in range(val.count('...')):
                key = str(list2[j].keys())
                if "pattern-inside" in key  :
                    newl = pattern_inside(list2[j:],list2[j]["pattern-inside"])

                    list3 = list2[:j]
                    for elem in newl: 
                        list3.append(elem)
            break
        if list3 == []:
            list3 = list2.copy()
        for j in range(1,len(list3)):
            for i in range(val.count('...')):
                key = str(list3[j].keys())
                count = find_occ(val,"...",i)
                if  "pattern" in key and "not" in key : 
                    l.append({"pattern-not":val[:count]+str(list3[j]["pattern-not"][:-1])+ val[count:]})
                elif "pattern" in key :
                    print("hello",key)
                    print(list3)

                    l.append({"pattern" : val[:count]+str(list3[j]["pattern"][:-1])+ val[count:]})

    return l

def sort_patterns(dict,condition) :
    for keys in dict:
        if "metavariable" in keys and "focus" not in keys :
            sort_metavariables(dict[keys],False,False)
            metavariable[dict[keys]["metavariable"]] = {"pattern":metavariable_pattern.copy(),"pattern-not":metavariable_pattern_not.copy()}
            metavariable_pattern.clear()
            metavariable_pattern_not.clear()

        elif type(dict[keys]) == list:
            for elem in dict[keys] : 
                for key in elem : 
                    if "metavariable" in key and "focus" not in key:
                        # print(elem) 
                        sort_metavariables(elem[key],False,False)
                        metavariable[elem[key]["metavariable"]] = {"pattern":metavariable_pattern.copy(),"pattern-not":metavariable_pattern_not.copy(),"pattern-either":metavariable_pattern_either.copy()}
                        metavariable_pattern.clear()
                        metavariable_pattern_not.clear()
                        metavariable_pattern_either.clear()
                    elif "pattern-inside" in key :
                        # print("this is it :",dict[keys].copy().index(elem))
                        dict[keys] = pattern_inside(dict[keys].copy(),elem[key])
                        # print(dict[keys])
                        sort_patterns({"patterns":dict[keys]},condition)

                    elif "pattern" in key and "not" in key : 
                        sort_patterns(elem,True)
                    elif "pattern" in key:  
                        if condition : 
                            sort_patterns(elem,True)
                        else :
                            sort_patterns(elem,False)
        else:
            if condition:
                if "regex" in keys : 
                    pattern_not.append("re:"+dict[keys])
                else: 
                    pattern_not.append(dict[keys])
            else : 
                if "regex" in keys : 
                    pattern.append("re:"+dict[keys])
                else: 
                    pattern.append(dict[keys])
    return

def toregex(val1):
    regex1 = re.escape(val1)
    if re.search(r"\\\.\\\.\\\.", regex1):
        regex1 =  re.sub(r"\\\.\\\.\\\.", r".*", regex1)
    if re.search(r"\\\$", regex1):
        regex1 =  re.sub(r"\\\$[A-Z]+", r".*", regex1)
    return regex1

def transform_file(dict):
    for key in dict:
        for meta in dict[key]["metavariable"]:
            for pat in dict[key]["metavariable"][meta]: 
                for i in range(len(dict[key]["metavariable"][meta][pat])):
                    if dict[key]["metavariable"][meta][pat][i][:3] != "re:":
                        dict[key]["metavariable"][meta][pat][i] = toregex(dict[key]["metavariable"][meta][pat][i])
                    else : dict[key]["metavariable"][meta][pat][i] = dict[key]["metavariable"][meta][pat][i][2:]
            if len(dict[key]["metavariable"][meta]["pattern-either"]) >0 : 
                newlist =   dict[key]["metavariable"][meta]["pattern-either"][0][3:]
                for i in range(1,len(dict[key]["metavariable"][meta]["pattern-either"])) : 
                    newlist += "|" + dict[key]["metavariable"][meta]["pattern-either"][i][3:]
                dict[key]["metavariable"][meta]["pattern-either"] = [newlist]                

def ToString(list) : 
    newlist = "["
    for item in list:
        new_item=item
        newitem = new_item.replace("\n", "\\n")
        newlist+=newitem
        newlist+=";"
    if(newlist[-1] ==";"):
        return newlist[:-1]+"]"
    return newlist +"]"
    
def fill_df(dataframe,dict):
    for i in dict:
      
        dataframe['id'].append(i)
        if dict[i]["pattern"]== []:
            dataframe["pattern"].append("*")
        else:
            dataframe["pattern"].append(ToString(dict[i]["pattern"]))


        if dict[i]["pattern-not"]== []:
            dataframe["pattern-not"].append("*")
        else:
            dataframe["pattern-not"].append(ToString(dict[i]["pattern-not"]))


        if dict[i]["pattern-either"]== []:
            dataframe["pattern-either"].append("*")
        else:
            dataframe["pattern-either"].append(ToString(dict[i]["pattern-either"]))
        l1 = ""
        l2 = ""
        l3 = ""
        for j in dict[i]["metavariable"] : 
            # print( dict[i]["metavariable"][j])
            if dict[i]["metavariable"][j]["pattern"]!= []:
                l1 +=j + ":" + str(dict[i]["metavariable"][j]["pattern"])[1:-1] +";"


            if dict[i]["metavariable"][j]["pattern-not"]!= []:
                l2 += j + ":" + str(dict[i]["metavariable"][j]["pattern-not"])[1:-1] +";"

                
            if dict[i]["metavariable"][j]["pattern-either"]!= []:
              l3 += j + ":" + str(dict[i]["metavariable"][j]["pattern-either"])[1:-1] + ";"
        if l1=="":
            dataframe["metavariable-pattern"].append("*")
        else:
            dataframe["metavariable-pattern"].append(str("["+l1[:-1]+"]"))

        if l2=="":
            dataframe["metavariable-pattern-not"].append("*")
        else:
            dataframe["metavariable-pattern-not"].append("["+l2[:-1]+"]")

        if l3=="":
            dataframe["metavariable-pattern-either"].append("*")
        else:
            dataframe["metavariable-pattern-either"].append("["+l3[:-1]+"]")
    
    return dataframe
      
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
# for filename in range(1):

    pattern = []
    pattern_not = []
    metavariable = {}
    metavariable_pattern = []
    metavariable_pattern_not = []
    metavariable_pattern_either = []

    # checking if it is a file
    if os.path.isfile(f):
    # if True:
        with open(f, 'r') as file:

            prime_service = yaml.safe_load(file)     

            i = prime_service["rules"]
            print(i)
            # for f in i[0]['patterns']:
            #     print(f)
            for j in i[0] :
                if "pattern" in j and "not" in j:
                    sort_patterns({j:i[0][j]},True)
                elif "pattern" in j:
                    # print({j:i[0][j]})
                    sort_patterns({j:i[0][j]},False)
    d[i[0]['id']] = {"pattern": pattern, "pattern-not": pattern_not,"pattern-either":pattern_either ,"metavariable" : metavariable}
transform_file(d)
dataframe = {"id":[],"pattern":[],"pattern-not":[],"pattern-either":[],"metavariable-pattern":[],"metavariable-pattern-not":[],"metavariable-pattern-either":[]}

# print(d)
dataframe = fill_df(dataframe,d)
# print(dataframe)
df = pd.DataFrame(data=dataframe)
df = df.replace(' ', '', regex=True)

df.to_csv('out.csv',index=False) 



    
