import numpy as np
import pandas as pd
import re 

from src.relation import *
from src.connection import *
from src.tree_compare import *

class RuleSet:
    #############################
    # Methods to build rule set #
    #############################
    def __init__(self,rules_list):
        ''' @rules_list: list of ordered dictionnaries each representing a rule with their attributes as keys'''
        self.set = pd.DataFrame(rules_list)
        if len(rules_list) > 0:
            self.m = len(rules_list[0]) #number of attributes (considering the recommendation)
        else:
             self.m = 0
        self.n = len(rules_list) #number of rules
        self.idm = np.empty(0) #Inter-Difference Matrix
        self.pm = np.empty(0) #Product Matrix (holds products of IDC for each pair of rules)
        self.attr_names = self.set.columns.tolist()

    def build_IDM(self):
        if self.n > 1: #needs at least two rules to compare them
            self.idm = np.zeros((self.m, self.n, self.n))
            #fill in IDC's for all attributes relationships
            for k in range(1,self.m):
                for i in range(self.n):
                    for j in range(i+1,self.n):
                        self.idm[k,i,j] = self._val_IDC(self.set.iloc[i,k],self.set.iloc[j,k],self.set.iloc[i,0],self.set.iloc[j,0])
            #fill in IDC's for recommendation relationships
            for i in range(self.n):
                for j in range(i+1,self.n):
                    self.idm[0,i,j] = self._rec_IDC(self.set.iloc[i,0],self.set.iloc[j,0])
    
    def build_PM(self):
        if(len(self.idm) > 0):
            self.pm = np.prod(self.idm,axis=0)
            return True
        else:
            return False

    # Helper methods to build rule set
    def _val_IDC(self, val1, val2,n1,n2):
        #Check for nan values
        if not isinstance(val1,str) and not isinstance(val2,str):
            if pd.isna(val1) and pd.isna(val2):
                return Relation.EQUALITY.value  #val1 and val2 are both nan
        elif not isinstance(val1,str) or not isinstance(val2,str): #one of them is NaN
            if isinstance(val1,str): # and not pd.isna(val2):
                return Relation.INCLUSION_IJ.value #val1 is nan and val2 is included in it
            else:
                return Relation.INCLUSION_JI.value #val2 is nan and val1 is included in it
        #check for type mismatch
        elif not self.same_type(val1,val2):  
            raise TypeError("val1 and val2 should have the same type when neither of them are NaN. val1: "+str(type(val1))+str(val1) + " val2: "+str(type(val2))+str(val2))
        #Both values are valid (not nan) and have the same type
        
        elif isinstance(val1,str):
            return self._interval(val1,val2,n1,n2)


    def escape(self,string):
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
    
    
    def toregex(self,val1):
        regex1 = re.escape(val1)
        if re.search(r"\\\.\\\.\\\.", regex1):
            regex1 =  re.sub(r"\\\.\\\.\\\.", r".*", regex1)
        if re.search(r"\\\$", regex1):
            regex1 =  re.sub(r"\\\$[A-Z]+", r".*", regex1)
        return regex1
    def clean(self,input_string):
            # Define a pattern to match the specified words and characters
        pattern = re.compile(r'(AND|OR|NOT|\\\n|\\n|\(|\)|\}|\{|\.\.\.|;)', re.IGNORECASE)

        # Use the pattern to replace matches with an empty string
        cleaned_string = re.sub(pattern, '', input_string)

        return cleaned_string

        
    def _compare(self,val1,val2):
        # check wether val1 is a regex or not :
        try : 
            isRegex = False 
            isRegex2 = False
            escape2= ""
            if val1[0:2] =="r:":
                isRegex = True
                val1 = val1[2:]
            if val2[0:2] == "r:" :
                isRegex2 = True
                val2 = val2[2:]
                escape2 = self.escape(val2)
            if not isRegex:
                regex1 = self.toregex(val1)
        
            else : 
                regex1 = val1
                #.* too simple, should write a more complex regex, where it can contain anything but a , or ) -- not true either, since a variable can be a function call...
            if isRegex2:
                regex1 = str(regex1)
                # print(regex1)
                if regex1 == val2:
                    return Relation.EQUALITY.value
                match1 = re.fullmatch(regex1, escape2)
                if match1:
                    return Relation.EQUALITY.value
                else :
                    return Relation.DIFFERENCE.value

            elif isRegex and not isRegex2 :
                regex2 = self.toregex(val2)
                if regex1 == regex2: 
                    return Relation.EQUALITY.value

                match1 = re.fullmatch(regex1, val2)
                if match1:
                    return Relation.EQUALITY.value
                else :
                    return Relation.DIFFERENCE.value
            
            match1 = re.fullmatch(regex1, val2)
            if match1:
                return Relation.EQUALITY.value
            else :
                return Relation.DIFFERENCE.value
        except: 
            return Relation.DIFFERENCE.value

        
        # Helper methods to build rule set

   
   
   
    def _contains2(self,t1,t2):
        if t1 == t2: 
            return True
        for node2 in t2:
            check = False
            for node1 in t1:
                if self._compare(node1.value,node2.value) == Relation.EQUALITY.value and (node2.value != '' and node1.value !='\\n') and ( node1.value !='...' and node2.value !='...' and not(self.isMeta(node1.value) or self.isMeta(node2.value))): 
                    check = self._contains2(node1.children,node2.children)
            if check == False:
                return False      
        return True

    def _contains1(self,tree1,tree2):
        for node2 in tree2:
            child = []
            for node1 in range(len(tree1)):
                if self._compare(tree1[node1].value,node2.value) == Relation.EQUALITY.value and (node2.value != '' and tree1[node1].value !='\\n') and ( tree1[node1].value !='...' and node2.value !='...' and not(self.isMeta(tree1[node1].value) or self.isMeta(node2.value))):
                    if self._contains2(tree1[node1].children,node2.children) == True:

                        return True
                    else : 
                        for item in tree1[node1].children : 
                            child.append(item) 
                elif tree1[node1].children != []:
                    for item in tree1[node1].children : 
                        child.append(item)     
            if(child != []):
                return(self._contains1(child,tree2))
            else :return False

    def _equals(self,tree1,tree2):
        if self._compare(tree1.value,tree2.value) == Relation.EQUALITY.value and (tree2.value != '' and tree1.value !='\\n') and ( tree1.value !='...' and tree2.value !='...' and not(self.isMeta(tree1.value) or self.isMeta(tree2.value))):
            if(len(tree1.children) != len(tree2.children)):
                return False
            for i in range(len(tree1.children)):
                if self._equals(tree1.children[i],tree2.children[i]) == False : 
                    return False
            return True
        else : 
            return False

    def isMeta(self,string):
        if string[0] == '$':
            if(string[1:].isupper()) : 
                return True
            return False
        else: return False
    #tell if overlap 
    #TODO : ADD a way to check how much the trees overlaps  
    def _overlap2(self,sub1,sub2):
        tmpTree = TreeNode(sub2.value)
        if sub1 == sub2: 
            return sub2
        for node2 in sub2.children:
            for node1 in sub1.children:
                if self._compare(node1.value,node2.value) == Relation.EQUALITY.value and (node2.value!= '' and node1.value!='\\n') and ( node1.value!='...' and node2.value!='...' and not(self.isMeta(node1.value) or self.isMeta(node2.value))):
                    tmpval = self._overlap2(node1,node2)
                    if tmpval != None : 
                        if not ((tmpval.value == 'OR' or tmpval.value == 'AND' or tmpval.value == 'NOT') and tmpval.children == []):
                            tmpTree.children.append(tmpval)
        if (tmpTree.value == 'OR' or tmpTree.value == 'AND' or tmpTree.value == 'NOT') and tmpTree.children == []:
            return None
        return tmpTree

    def _overlap(self,tree1,tree2):
        child1=[]
        subtreeList = []
        for n2 in tree2:
            child2 = []
            
            for node1 in tree1:
                if self._compare(node1.value,n2.value) == Relation.EQUALITY.value and (n2.value != '' and node1.value !='\\n') and ( node1.value !='...' and n2.value !='...' and not(self.isMeta(node1.value) or self.isMeta(n2.value))):
                    if n2.value == "OR" or n2.value == "AND" or n2.value == "NOT": 
                        myl = []
                        for elem1 in node1.children:
                            for elem2 in n2.children:
                                if self._compare(elem1.value,elem2.value) == Relation.EQUALITY.value and (elem2.value != '' and elem2.value !="\\n"):
                                    if( elem1.value !='...' and elem2.value !='...' and not(self.isMeta(elem1.value) or self.isMeta(elem2.value))) : 
                                        # print(elem1.value + ' is equal to ' + elem2.value)
                                        # In this case the similar nodes are from a similar parent so it can start a subtree that overlap we have to check the neighbours to find if there are other overlapping node from this parent.
                                        # check the whole childrens
                                   
                                        myl.append((elem1,elem2))
                                        
                        if myl != [] :
                            tmpTree = TreeNode(n2.value) 
                            # Here create the subtrees that overlaps
                            for sub in myl : 
                                tmpVal = self._overlap2(sub[0],sub[1])
                            
                                if tmpVal != None and tmpVal.children != [] :
                                    tmpTree.children.append(tmpVal)
                            if tmpTree.children != []:
                                subtreeList.append(tmpTree)
            
                                
    
                    # else:  
                    #     # print(node1.value + ' is equal to ' + n2.value)  
                    #     # In this case the parent is not a condition node so this is a single node in common not interesting 
                    #     return True
                
                elif node1.children != []:
                    for item in node1.children : 
                        child2.append(item) 
            
            if child2 != []:
                return self._overlap(child2,tree2) 
            child2 = []

            for item in n2.children : 
                        child1.append(item) 
        if len(subtreeList) <2: 
            return subtreeList
        if child1 != []:
            return(self._overlap(tree1,child1))
        return subtreeList



    def _interval(self,val1, val2,n1,n2):
        t1 = parse_tree(parse(val1)[0])
        t2 = parse_tree(parse(val2)[0])
        if (self._equals(t1,t2)):
            return Relation.EQUALITY.value
        elif(self._contains1([t1],[t2])):
            print(n2)
            print(n1)
            print('Connection.INCLUSION')
            return Relation.INCLUSION_IJ.value
        elif(self._contains1([t2],[t1])):
            print(n1)
            print(n2)
            print('Connection.INCLUSION')
            return Relation.INCLUSION_JI.value
        elif( self._overlap([t1],[t2]) != [] ):
            v = self._overlap([t1],[t2])
            subtr = rebuild(v[0])
            clean_tr = self.clean(subtr)
            if clean_tr =="": 
                return Relation.DIFFERENCE.value 
            print(n1)
            print(n2)
            print(subtr)
            return Relation.OVERLAP.value
        else: 
            return Relation.DIFFERENCE.value     
   
          


    def _isclosed(self,inter,side):
        ''' Return true if interval 'inter' is closed on side 'side', False if it is open on that side
            @inter: an interval pandas.Interval
            @side: 'left', 'right', 'both' or 'neither'
        '''
        if inter.closed == side or inter.closed == 'both':
            return True
        else:
            return False   

    def _rec_IDC(self, rec1, rec2):
        if(rec1 == rec2):
            return Relation.SAME_REC.value
        else:
            return Relation.DIFF_REC.value

    #############################################
    # Methods to get information about rule set #
    #############################################

    def get_val(self,rule,attr):
        ''' returns the value that 'rule' has for attribute 'attr'
            @rule: index of the rule (int)
            @attr: either index (int) or name (str) of the attribute 
        '''
        if type(rule) is not int or rule < 0 or rule >= self.n:
            raise ValueError("'rule' must be an integer in [0,"+str(self.n-1)+"]")
        if type(attr) is str:
            if attr not in self.attr_names:
                raise ValueError("Attribute given doesn't exist. attr="+attr)
            return self.set[attr][rule]
        elif type(attr) is int and attr >= 0 and attr < self.m:
            #print("set before set.iloc:")
            #print(self.set)
            return self.set.iloc[rule,attr]
        else:
            raise ValueError("'attr' must be either an integer in [0,"+str(self.m-1)+"] or an existing attribute name")

    def connection(self, r1, r2):
        ''' Returns the Relation enum that corresponds to the relation between rules with indexes 'r1' and 'r2'
            or the enum ERROR if the PM matrix hasn't been built yet
            rules indexes start at 0; r1 and r2 may be given in any order
        '''
        if len(self.pm) == 0: #build_PM needs to be called to create PM matrix
            return Connection.ERROR
        elif r1 >= self.n or r2 >= self.n:
            raise ValueError("indexes given for connections are too high r1:"+str(r1)+" r2:"+str(r1)+" maxVal:"+str(self.n-1))
        else:
            if r1 == r2:
                return Connection.REFERENCE
            if r1 > r2:
                r = r1; r1 = r2; r2 = r
            p = self.pm[r1][r2]
            #print("r1: "+str(r1)+" r2: "+str(r2)+" p: "+str(p))
            if p == Relation.DIFFERENCE.value: return Connection.DISCONNECTED
            elif p == Relation.EQUALITY.value : return Connection.EQUAL_SAME
            elif p == -Relation.EQUALITY.value : return Connection.EQUAL_DIFF
            elif p % Relation.OVERLAP.value == 0 and p > 0: return Connection.OVERLAP_SAME
            elif p % Relation.OVERLAP.value == 0 and p < 0 : return Connection.OVERLAP_DIFF
            elif (p % Relation.INCLUSION_IJ.value == 0 or p % Relation.INCLUSION_JI.value == 0) and p*Relation.SAME_REC.value > 0 : return Connection.INCLUSION_SAME
            elif (p % Relation.INCLUSION_IJ.value == 0 or p % Relation.INCLUSION_JI.value == 0) and p*Relation.DIFF_REC.value > 0 : return Connection.INCLUSION_DIFF
            else:
                raise ValueError("pm has illegal value at indices ["+str(r1)+","+str(r2)+']')

    def same_type(self,val1,val2):
        ''' Redefine same type relationships to ignore difference between numpy and regular types '''
        if type(val1) == type(val2):
            return True
        elif (isinstance(val1,np.bool_) and isinstance(val2,bool)) or (isinstance(val1,bool) and isinstance(val2,np.bool_)):
            return True
        elif (isinstance(val1,np.float64) and isinstance(val2,float)) or (isinstance(val1,float) and isinstance(val2,np.float64)):
            return True
        else:
            return False
    
    def has_type(self,val,checked_type):
        if isinstance(val,checked_type):
            return True
        elif ((checked_type == bool) and isinstance(val,np.bool_)) or ((checked_type == np.bool_) and isinstance(val,bool)):
            return True
        elif ((checked_type == float) and isinstance(val,np.float64)) or ((checked_type == np.float64) and isinstance(val,float)):
            return True
        else:
            return False

    def __str__(self):
        header = "Rules in set:\n"
        size = "AttributeNbr: " + str(self.m) + "RulesNbr: " + str(self.n) + "\n"
        return header + str(self.set)

    ###############################
    # Methods to modifiy rule set #
    ###############################

    def recompute_m(self):
        ''' recompute the matrix idm and pm if they already exist'''
        if len(self.idm) > 0:
                self.build_IDM()
                if len(self.pm) > 0:
                    self.build_PM()

    def update_idm(self,rule,attr):
        if len(self.idm) > 0:
            #update idm
            for i in range(self.n):
                #update of regular value
                if attr > 0 and i < rule:
                    self.idm[attr,i,rule] = self._val_IDC(self.set.iloc[i,attr],self.set.iloc[rule,attr])
                elif attr > 0 and i > rule:
                    self.idm[attr,rule,i] = self._val_IDC(self.set.iloc[rule,attr],self.set.iloc[i,attr])
                #update of recommendation
                if attr == 0 and i < rule:
                    self.idm[attr,i,rule] = self._rec_IDC(self.set.iloc[i,attr],self.set.iloc[rule,attr])
                elif attr == 0 and i > rule:
                    #print("update_idm : i="+str(i)+" attr="+str(attr)+"rule="+str(rule)+str(self.n))
                    #print("-- set in update_idm --")
                    #print(self.set)
                    #print("-- ism in update_idm --")
                    #print(self.idm)
                    self.idm[attr,rule,i] = self._rec_IDC(self.set.iloc[i,attr],self.set.iloc[rule,attr])
    
    def update_pm(self,rule):
        if len(self.pm) > 0:
            #update pm
            self.pm[rule,:] = np.prod(self.idm[:,rule,:],axis=0)
            self.pm[:,rule] = np.prod(self.idm[:,:,rule],axis=0)

    def update_val(self, rule, attr, val, update=True):
        ''' Update value of an attribute by setting value in position [rule,attr] in de DataFrame rules to value val
            if update = True, recompute self.idm and self.pm, leave them unchanged otherwise
            rule and attr must be int with rule < n and 0 <attr < m
            val must either be nan or have the same type as the rest of the values in the column
            (No checks are performed on val for performance reasons)
            (Method designed for attributes and not for the recommendation)
        '''
        if attr >= self.m or rule >= self.n:
            raise ValueError("Index condition not respected: rule ("+str(rule)+") must be lower than "+str(self.n)+" and attr ("+str(attr)+") must be lower than "+str(self.m))
        self.set.iloc[rule,attr] = val
        if update:
            self.update_idm(rule,attr)
            self.update_pm(rule)
            
    def update_attr(self,attr_list):
        ''' update attr by giving a new attr list
         '''
        for i in range(len(attr_list)):
            if attr_list[i] == '':
                raise ValueError("Attribute name cannot be an empty string.")
            for j in range(i+1,len(attr_list)):
                if attr_list[i] == attr_list[j]:
                    raise ValueError("Two attributes can't have the same name.")
        if attr_list[0] != 'Rec' and attr_list[0] != 'Recommendation':
            raise ValueError("First column must have name 'Rec' or 'Recommendation")
        self.set.columns = attr_list
        self.attr_names = attr_list
    
    '''
    def update_attr(self,new_attr,position):
        if new_attr in self.attr_names and new_attr!=self.attr_names[position]:
            raise ValueError("New attribute name can't be the same as an already existing one.")
        if position == 0 and (new_attr == 'Rec' or new_attr == 'Recommendation'):
            raise ValueError("First column must have name 'Rec' or 'Recommendation")
        self.attr_names[position] = new_attr
        self.set.columns = self.attr_names
    '''
   
    def add_attr(self,attr_name,val_list=None):
        ''' @val_list: list containing the value of that attribute for each rule
            verification of correct type is not guaranteed because is only done if idm > 0
        '''
        if self.n == 0:
            raise ValueError("Cannot add attribute to empty ruleset. Add a rule first.")
        if attr_name == '':
                raise ValueError("Attribute name cannot be an empty string.")
        if attr_name in self.attr_names:
            raise ValueError("The new attribute name must not already be used. Error with attr_name="+str(attr_name))
        if val_list is None:
            self.set[attr_name] = pd.Series(float('nan'),index=range(self.n))
            #new idm layer for this attr has 1's for all rules since all values are the same
            if len(self.idm) > 0:
                new_idm_layer = np.zeros((1,self.n,self.n))
                for i in range(1,self.n):
                    for j in range(i+1,self.n):
                        new_idm_layer[0,i,j] = 1
                self.idm = np.concatenate((self.idm,new_idm_layer))
            #No changes to pm needed since all new values are one's
        else:
            if len(val_list) != self.n:
                raise ValueError("Length of list value ("+str(len(val_list))+") must be equal to number of rules ("+str(self.n)+")")
            self.set[attr_name] = pd.Series(val_list)
            #build new idm layer and add it to idm
            if len(self.idm) > 0:
                new_idm_layer = np.zeros((1,self.n,self.n))
                for i in range(0,self.n):
                    for j in range(i+1,self.n):
                        try:
                            new_idm_layer[0,i,j] = self._val_IDC(self.set[attr_name][i],self.set[attr_name][j])
                        except TypeError:
                            raise TypeError("New attribute contains values with different types.")
                self.idm = np.concatenate((self.idm,new_idm_layer))
                #recompute pm
                if len(self.pm) > 0:
                    self.build_PM()        
        self.m += 1
        self.attr_names = self.set.columns.tolist()
    
    def add_rule(self,rec,val_list=None):
        ''' @val_list: list containing the values for all attributes of this rule (recommendation excluded)
            verification of correct type is not guaranteed because is only done if idm > 0
        '''
        if self.n == 0:
            names = ['Recommendation']
            values = [rec]
            if val_list is not None:
                for i in range(len(val_list)):
                    names += ['Attr '+str(i+1)]
                values = [rec] + val_list
            rule_dict = {k:v for k,v in zip(names,values)}
            self.set = pd.DataFrame([rule_dict])[names]
            self.m = len(names)
            self.n = 1
            self.attr_names = names
        else:
            old_n = self.n
            new_n = self.n+1
            self.n += 1 #update needs to be done before call to update_idm()
            if val_list == None:
                rule = pd.DataFrame(None,index=[old_n])
                self.set = pd.concat([self.set,rule],sort=False)
                self.set.iloc[old_n,0] = rec
            else:
                if len(val_list) != self.m-1:
                    self.n = old_n
                    raise ValueError("The number of values given ("+str(len(val_list))+") is not the same as the number of attributes ("+str(self.m-1)+").")
                keys = self.attr_names
                values = [rec] + val_list
                val_dict = {k:v for k,v in zip(keys,values)}
                rule = pd.DataFrame(val_dict,index=[old_n])
                self.set = pd.concat([self.set,rule],sort=False)
            #add new rows and columns to idm
            if len(self.idm) > 0:
                rows = np.zeros((self.m,1,old_n))
                self.idm = np.concatenate((self.idm,rows),axis=1)
                cols = np.zeros((self.m,old_n+1,1))
                self.idm = np.concatenate((self.idm,cols),axis=2)
                for attr in range(self.m):
                    try:
                        #print("-- ruleset--")
                        #print(self.set)
                        #print("i: "+str(old_n)+" attr: "+str(attr))
                        #print("-- idm --")
                        #print(self.idm)
                        #print()
                        self.update_idm(old_n,attr)
                    except TypeError:
                        self.n = old_n
                        raise TypeError("New rule contains value with inadequate type.")
                #add new rows and columns in pm
                if len(self.pm) > 0:
                    rows = np.zeros((old_n,1))
                    self.pm = np.concatenate((self.pm,rows),axis=1)
                    cols = np.zeros((1,old_n+1))
                    self.pm = np.concatenate((self.pm,cols),axis=0)
                    self.pm[:,old_n] = np.prod(self.idm[:,:,old_n],axis=0)

    def delete_attr(self,attr):
        if attr == 0 or attr == 'Rec' or attr == 'Recommendation':
            raise ValueError("Recommendation cannot be deleted from ruleset")
        if isinstance(attr,int):
            if attr < 0 or attr >= self.m:
                raise ValueError("The recommendation index for deletion has to be in [1,"+str(self.m-1)+"]. attr="+str(attr))
            else:
                index = attr
                name = self.attr_names[attr]
        else:
            if attr not in self.attr_names:
                raise ValueError("The recommendation given for deletion ("+str(attr)+"is not found in the ruleset.")
            else:
                index = self.attr_names.index(attr)
                name = attr
        del self.set[name]
        self.attr_names = self.set.columns.tolist()
        self.m -= 1 #has to be before update of idm
        if len(self.idm) > 0:
            self.idm = np.delete(self.idm,index,axis=0)
            if len(self.pm) > 0:
                self.build_PM()

    def delete_rule(self,rule):
        '''  '''
        if rule < 0 or rule >= self.n:
            raise ValueError("The rule index for deletion has to be in [0,"+str(self.m-1)+"]. rule="+str(rule))
        self.n -= 1 #has to be before update of set indexes
        new_set = self.set.drop(rule)
        self.set = new_set
        new_set.index = range(self.n)
        if len(self.idm) > 0:
            if self.n > 1: #needs at least two rules to compare them in idm and pm
                temp_idm = np.delete(self.idm,rule,axis=1)
                self.idm = np.delete(temp_idm,rule,axis=2)
                if len(self.pm) > 0:
                    temp_pm = np.delete(self.pm,rule,axis=0)
                    self.pm = np.delete(temp_pm,rule,axis=1)
            else:
                self.idm = np.empty(0)
                self.pm = np.empty(0)
                
    
    def to_csv(self,file_name):
        self.set.to_csv(file_name,index=False)
