import re
from src.relation import *
import pandas as pd


def escape(string):
    newstring = ""
    for i in range(len(string)):
        if string[i] == "\\" and string[i+1] == "\\":
            newstring += "\\"
            i += 1
        elif string[i] == "\\":
            pass
        else :
            newstring += string[i]
    return newstring

def toregex(val1):
    regex1 = re.escape(val1)
    if re.search(r"\\\.\\\.\\\.", regex1):
        regex1 =  re.sub(r"\\\.\\\.\\\.", r".*", regex1)
    if re.search(r"\\\$", regex1):
        regex1 =  re.sub(r"\\\$[A-Z]+", r".*", regex1)
    return regex1

        
def compare(val1,val2):
    # check wether val1 is a regex or not :
    isRegex = False 
    isRegex2 = False
    escape2= ""
    if val1[0:2] =="r:":
        isRegex = True
        val1 = val1[2:]
    if val2[0:2] == "r:" :
        isRegex2 = True
        val2 = val2[2:]
        escape2 = escape(val2)
    if not isRegex:
        regex1 = toregex(val1)
   
    else : 
        regex1 = val1
    if isRegex2:
        regex1 = str(regex1)
        if regex1 == val2:
            return Relation.EQUALITY.value
        match1 = re.fullmatch(regex1, escape2)
        if match1:
            return Relation.OVERLAP.value
        else :
            return Relation.DIFFERENCE.value

    elif isRegex and not isRegex2 :
        regex2 = toregex(val2)
        if regex1 == regex2: 
            return Relation.EQUALITY.value

        match1 = re.fullmatch(regex1, val2)
        if match1:
            return Relation.OVERLAP.value
        else :
            return Relation.DIFFERENCE.value
    
    match1 = re.fullmatch(regex1, val2)
    if match1:
        return Relation.OVERLAP.value
    else :
        return Relation.DIFFERENCE.value
    # Helper methods to build rule set

def interval(val1, val2):
    result1 = _intervals_IDC_(val1, val2)
    result2 = _intervals_IDC_(val2, val1)
    if result1 == Relation.OVERLAP.value or result2 == Relation.OVERLAP.value:
        return Relation.OVERLAP.value
    return result1
        
    

def _intervals_IDC_(val1,val2):
    #check wheter two intervals are the same or not, if they overlap, ...
    results = []
    count = 0
    for v1 in val1:
        for v2 in val2:
            results.append(compare(v1,v2))
            count+=1
    equality = 0
    counter = 0
    for i in results:
        if i == Relation.EQUALITY.value:
            equality +=1
        if i == Relation.DIFFERENCE.value:
            counter +=1
    if equality == len(val1) and len(val1) == len(val2):
        return Relation.EQUALITY.value
    if (equality == len(val1) or equality == len(val2)) and len(val2) < len(val1):
        return Relation.INCLUSION_IJ.value
    if (equality == len(val1) or equality == len(val2)) and len(val2) > len(val1):
        return Relation.INCLUSION_JI.value
    if counter != count:
        return Relation.OVERLAP.value
    return Relation.DIFFERENCE.value
   
