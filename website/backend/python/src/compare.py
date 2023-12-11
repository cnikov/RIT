import re
from src.relation import *
import pandas as pd


"""
This function escape a string 
:params string : string to escape
:return newstring : string escaped
"""
def escape(string): # initialize escape function
    newstring = "" # initialize empty string for newstring
    for i in range(len(string)): # iterate through string
        if string[i] == "\\" and string[i+1] == "\\": # check for double backslash
            newstring += "\\" # append single backslash to newstring
            i += 1 # increment index
        elif string[i] == "\\": # check for single backslash
            pass # ignore single backslash
        else : # if character is not a backslash
            newstring += string[i] # append character to newstring
    return newstring # return newstring with escape characters processed

"""
This function transform a string to regular expression
:params val1: string to transform
:return regex1 : string transformed
"""
def toregex(val1):
    # convert to regex pattern
    regex1 = re.escape(val1)
    # handle 3-dots (match any)
    if re.search(r"\\\.\\\.\\\.", regex1):
        regex1 = re.sub(r"\\\.\\\.\\\.", r".*", regex1)
    # handle end of line ($)
    if re.search(r"\\\$", regex1):
        regex1 = re.sub(r"\\\$[A-Z]+", r".*", regex1)
    return regex1

"""
This function compare two string by using regular expression match
:params val1,val2 : string,string the two string that we want to compare
:return Relation value : int
"""
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

"""
This function check for a relation between two value
:params val1,val2: string,string two string to compare
:return Relation value: int 
"""
def interval(val1, val2):
    """Check relation between intervals."""
    result1 = _intervals_IDC_(val1, val2)
    result2 = _intervals_IDC_(val2, val1)
    if result1 == Relation.OVERLAP.value or result2 == Relation.OVERLAP.value:
        """Intervals overlap."""
        return Relation.OVERLAP.value
    return result1
        
    
"""
This function check for a relation between two value
:params val1,val2: string,string two string to compare
:return Relation value: int 
"""
def _intervals_IDC_(val1,val2):
    # Compare intervals, store results
    results = []
    count = 0
    for v1 in val1:
        for v2 in val2:
            results.append(compare(v1,v2))
            count+=1
    # Check for equality, inclusion, or overlap
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
   
