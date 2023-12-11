import pandas as pd
import csv
import numpy as np
import re
from src.relation import *
from src.rule_set import *
# Define a TreeNode class to represent nodes in the semantic tree.
# with open("out2.csv", 'r') as csv_file:
#     reader = csv.DictReader(csv_file)
#     # print(reader)
    
#     for r in reader:
#         r['tree'] = r["tree"].replace("',", "';")
#         print(r['tree']) 



class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def __eq__(self, other):
        if not isinstance(other, TreeNode):
            return False

        return self.value == other.value and self.children == other.children


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


#tell if overlap 


def parse_tree(tree_list):
    index = 0
    root_value = tree_list[0]
    root = TreeNode(root_value)
    if len(tree_list) == 1:
        return root
    while index < len(tree_list[1]):
        if 'AND' in tree_list[1][index] or 'OR' in tree_list[1][index] or 'NOT' in tree_list[1][index]:
            child_tree = parse_tree([tree_list[1][index],tree_list[1][index+1]])
            index +=1
            root.children.append(child_tree)
        else:
            child_value = tree_list[1][index]
            child = TreeNode(child_value)
            root.children.append(child)
        index +=1
    return root
def rebuild(tree):
    res=tree.value
    if len(tree.children) == 0:
        return res
    else : 
        res += "("
        index = 0
        for child in tree.children:
            if child.children == []:

                res += child.value
                if index <len(tree.children)-1:
                    res += ";"
            else:
                res = res  + rebuild(child)
                if index <len(tree.children)-1:
                    res = res + ';'
            index+=1

    return res + ')'




