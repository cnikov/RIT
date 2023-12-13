import pandas as pd
import csv
import numpy as np
import re
from relation import *
from rule_set import *



class TreeNode:
    def __init__(self, value,child = []):
        # Initializing TreeNode with a value
        self.value = value
        # Creating an empty list to store child nodes
        self.children = child
    def __eq__(self, other):
        # Checking if other is not an instance of TreeNode
        if not isinstance(other, TreeNode):
            return False
        # Checking if TreeNode values and child nodes are equal
        return self.value == other.value and self.children == other.children

def parse(tree_str):
    # Counter to track nested parentheses
    counter = 0
    # List to store the parsed tree nodes
    tree_lst = []
    # Temporary string to store current node
    tmp_str = ""
    # Index to track current position in the input string
    index = 0
    # Loop through the input string
    while index < (len(tree_str)) : 
        # If current character is a semicolon and not nested in parentheses
        if(tree_str[index] == ";" and counter == 0):
            tree_lst.append(tmp_str)
            tmp_str = ""
        # If current character is an opening parenthesis
        elif tree_str[index] == "(":
            counter+=1
            if counter > 0:
                tmp_str+=tree_str[index]
        # If current character is a closing parenthesis
        elif tree_str[index] == ")" : 
            counter-=1
            # If no more nested parentheses
            if counter == -1:
                if tmp_str != "":
                    tree_lst.append(tmp_str)
                return tree_lst,index
            else:
                tmp_str+= tree_str[index]     
        # If current string is "AND" or "NOT"
        elif tree_str[index:index+4] == "AND(" or tree_str[index:index+4] == "NOT(" :
            tree_lst.append(tree_str[index:index+3])
            mystr, myindex = parse(tree_str[index+4:])
            tree_lst.append(mystr)
            index = index + myindex +5
        # If current string is "OR"
        elif tree_str[index:index+3] == "OR(":
            tree_lst.append(tree_str[index:index+2])
            mystr, myindex = parse(tree_str[index+3:])
            tree_lst.append(mystr)
            index = index + myindex +4
        # If current character is none of the above, append it to the current node
        else:
            tmp_str+= tree_str[index]
        index +=1
    # If tree_lst is empty, return the input string as a node
    if tree_lst == []:
        return [tree_str],len(tree_str)
    return tree_lst , index

"""
this function transform the tree into a data structure of tree with a node and children
:params tree_list : [] the tree parsed into a list
:return root : Node the root of the tree
"""
def parse_tree(tree_list):
    index = 0
    root_value = tree_list[0]
    root = TreeNode(root_value,[]) # create root node
    if len(tree_list) == 1:
        return root # if tree has only root
    while index < len(tree_list[1]):
        if 'AND' in tree_list[1][index] or 'OR' in tree_list[1][index] or 'NOT' in tree_list[1][index]:
            child_tree = parse_tree([tree_list[1][index], tree_list[1][index+1]]) # create child tree
            index += 1 # move to next index
            root.children.append(child_tree) # add child tree to root
        else:
            child_value = tree_list[1][index]
            child = TreeNode(child_value) # create child node
            root.children.append(child) # add child node to root
        index += 1 # move to next index
    return root # return root node


"""
This function rebuild the tree from the data structure to a string tree
:params tree: Node
:retrun res: string rebuild tree
"""
def rebuild(tree):
    res = tree.value # initialize result with root value
    if len(tree.children) == 0: # check if tree has no children
        return res # return root value if no children
    else: # tree has children
        res += "(" # start with '(' to represent children
        index = 0 # initialize index for child loop
        for child in tree.children: # iterate through each child
            if child.children == []: # check if child has no children
                res += child.value # append child value to result
                if index < len(tree.children) - 1: # check if not last child
                    res += ";" # append ';' if not last child
            else: # child has children
                res = res + rebuild(child) # recursively build string for child
                if index < len(tree.children) - 1: # check if not last child
                    res = res + ';' # append ';' if not last child
            index += 1 # increment index for next child
    return res + ')' # close '(' with ')' and return result




