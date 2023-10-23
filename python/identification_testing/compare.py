import pandas as pd
import csv
import numpy as np
import re
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



def equals(tree1,tree2):
    """
    Check if tree2 equals tree1.

    Args:
        tree1 : The first tree as a root.
        tree2 : The second tree as a root.

    Returns:
        bool: True if tree2 equals tree1 , False otherwise.
    """
    if tree1.value == tree2.value:
        if(len(tree1.children) != len(tree2.children)):
            return False
        for i in range(len(tree1.children)):
            #recursion on every children for tree1 and tree2 to check if they are totally equal
            if equals(tree1.children[i],tree2.children[i]) == False : 
                return False
        return True
    else : 
        return False



def contains2(t1,t2):
    """
    Check if tree2 is contained in tree1.

    Args:
        tree1 (list): The first tree as a list of nodes.
        tree2 (list): The second tree as a list of nodes which are actually childrens of the root node used in contains1.

    Returns:
        bool: True if tree2 is contained in tree1 , False otherwise.
    """
    # Compare the root of tree2 with every node of tree 1 to find same nodes

    #edge case of no t1 and t2 are empty list
    if t1 == t2: 
        return True
    for node2 in t2:
        check = False
        for node1 in t1:
            if node1.value == node2.value:
                #compare values and do recursion to check entire tree
                check = contains2(node1.children,node2.children)
        if check == False:
            return False      
    return True

def contains1(tree1,tree2):
    """
    Check if tree2 is contained in tree1 by doing a bfs on tree1.

    Args:
        tree1 (list): The first tree as a list of nodes.
        tree2 (list): The second tree as a list of nodes.

    Returns:
        bool: True if tree2 is contained in tree1 , False otherwise.
    """
    # Compare the root of tree2 with every node of tree 1 to find same nodes
    for node2 in tree2:
        child = []
        for node1 in range(len(tree1)):
            if tree1[node1].value == node2.value:
                #If same node check if the rest of tree2 is the same of the child of the node of tree1 that match
                if contains2(tree1[node1].children,node2.children) == True:
                    return True
                #if the entire tree2 does not match node1 children then pass to another node of tree1
                else : 
                    for item in tree1[node1].children : 
                        child.append(item) 
            #if there is no matching on the current floor of tree1  then create a new floor with all the children of the actual floor
            elif tree1[node1].children != []:
                for item in tree1[node1].children : 
                    child.append(item)  
        #if the tree1 is not over and no matching we keep looking deeper     
        if(child != []):
            return(contains1(child,tree2))
        #No matching return false
        else :return False



#tell if overlap 
#TODO : ADD a way to check how much the trees overlaps  
def overlap(tree1,tree2):
    """
    Check if tree2 overlap tree1.

    Args:
        tree1 (list): The first tree as a list of nodes.
        tree2 (list): The second tree as a list of nodes.

    Returns:
        bool: True if tree2 and tree1 have a same node , False otherwise.
    """
    child1=[]
    for n2 in tree2:
        child2 = []
        
        for node1 in tree1:
            if node1.value == n2.value :
                if n2.value in {"OR","AND","NOT"}: 
                    for elem1 in node1.children:
                        for elem2 in n2.children:
                            if elem1.value == elem2.value and (elem2.value not in {"AND","OR","NOT"}):
                                return True
                else:    
                    return True
            
            elif node1.children != []:
                for item in node1.children : 
                    child2.append(item) 
        if child2 != []:
            return overlap(child2,tree2) 
        child2 = []

        for item in n2.children : 
                    child1.append(item) 
    if child1 != []:
        return(overlap(tree1,child1))
    return False



# Input tree strings to compare in the specified format.

t0 = parse_tree(parse("AND(OR($CONNECTION.execute($SQL+$VAL,...)\n;$CONNECTION.execute($SQL%$VAL,...)\n;$CONNECTION.execute($SQL.format($VAL),...)\n;AND($QUERY=$SQL+$VAL\n$CONNECTION.execute($QUERY,...)\n..\n;$CONNECTION.execute($QUERY,...)\n);AND($QUERY=$SQL%$VAL\n$CONNECTION.execute($QUERY,...)\n..\n;$CONNECTION.execute($QUERY,...)\n);AND($QUERY=$SQL.format($VAL)\n$CONNECTION.execute($QUERY,...)\n..\n;$CONNECTION.execute($QUERY,...)\n);AND(OR($QUERY=f""$CONNECTION.execute($QUERY,...)\n..{...}...""\n...\n;$QUERY=f""...{$CONNECTION.execute($QUERY,...)\n..}...""\n...\n;$QUERY=f""...{...}$CONNECTION.execute($QUERY,...)\n..""\n...\n;$QUERY=f""...{...}...""\n$CONNECTION.execute($QUERY,...)\n..\n);$CONNECTION.execute($QUERY,...)\n)))")[0])
t1 = parse_tree(parse("OR(h;h;OR(s;s;OR(a;b)))")[0])
t2 =  parse_tree(parse("OR(a;b))")[0])
t3 = parse_tree(parse("AND(OR($CONNECTION.execute($SQL+$VAL,...)\n;$CONNECTION.execute($SQL%$VAL,...)\n;$CONNECTION.execute($SQL.format($VAL),...)\n;cr.execute($SQL.format($VAL),...)\n;AND($QUERY=$SQL+$VAL\n$CONNECTION.execute($QUERY,...)\n..\n;$CONNECTION.execute($QUERY,...)\n);AND($QUERY=$SQL%$VAL\n$CONNECTION.execute($QUERY,...)\n..\n;$CONNECTION.execute($QUERY,...)\n);AND($QUERY=$SQL.format($VAL)\n$CONNECTION.execute($QUERY,...)\n..\n;$CONNECTION.execute($QUERY,...)\n);AND(OR($QUERY=f""$CONNECTION.execute($QUERY,...)\n..{...}...""\n...\n;$QUERY=f""...{$CONNECTION.execute($QUERY,...)\n..}...""\n...\n;$QUERY=f""...{...}$CONNECTION.execute($QUERY,...)\n..""\n...\n;$QUERY=f""...{...}...""\n$CONNECTION.execute($QUERY,...)\n..\n);$CONNECTION.execute($QUERY,...)\n)))")[0])
if (equals(t1,t2)):
    print("egalité")
elif(contains1([t1],[t2])):
    print("t1 contient t2")
elif(contains1([t2],[t1])):
    print("t2 contient t1")
elif(overlap([t1],[t2]) ):
    print("overlap")
else: 
    print("rien")


