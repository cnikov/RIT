import PySimpleGUI as sg
import pandas as pd
import copy
import collections as col

import tkinter as tk

import parser_1 as parser_1
from rule_set import * 
from connection import *


## ADD a popup for check

ruleset = RuleSet([])
## END of popup for check
def run_gui():
    rules = parser_1.parse_csv("out2.csv") # Load rules from CSV
    ruleset = RuleSet(rules) # Create rule set object
    if len(ruleset.idm) == 0: # If IDM is empty
        ruleset.build_IDM() # Build IDM
        ruleset.build_PM() # Build PM
    for i in range(ruleset.n): # Loop through rule set
        for j in range(ruleset.n):
            if ruleset.connection(i, j) != Connection.DISCONNECTED : # If connected
                if ruleset.connection(i, j) != Connection.REFERENCE : # If not reference
                    print(ruleset.set.iloc[i,0]) # Print rule ID
                    print(ruleset.set.iloc[j,0])
                    print(str(ruleset.connection(i, j))) # Print connection type
                        
def erase(window,headers=False,values=False,connections=False):
    if headers:
        [window[(-1,j)].update('') for j in range(nbr_cols)] #empty headers
    if values:
        [window[(i,j)].update('') for j in range(nbr_cols) for i in range(nbr_rows)] #empty values
    if connections:
        [window[('connection',i)].update('') for i in range(nbr_rows)] #empty connections
        for i in range(nbr_rows):
            for j in range(nbr_cols):
                window[(i,j)].Widget.configure(background='white')         

def resize_window(rows,cols):
    global nbr_rows
    global nbr_cols
    global width
    global window
    nbr_rows = rows; nbr_cols = cols
    intro = [sg.Text('Energy rules',key = 'txt1')]
    header_row = [[sg.Text('', size=(4,1))] + [sg.Input(size=(width,1), pad=(0,0), key=(-1,attr)) for attr in range(nbr_cols)]]
    input_rows = [[sg.Text(str(row), size=(4,1))] + [sg.Input(size=(width,1), pad=(0,0), key=(row,attr)) for attr in range(nbr_cols)] + [sg.Text('', size=(2*width,1), key=('connection',row))] for row in range(nbr_rows)]
    n = min(25,nbr_rows); m = min(15,nbr_cols)
    scrollable_set = [sg.Column(header_row + input_rows, size=(width*m*8,n*25), scrollable=True)]
    actions1 = [sg.Text('Index of rule to check connections with:'), sg.Input(size=(4,1),key='to_check'),sg.Button('Check')]
    actions2 = [sg.Button('Update'), sg.Button('Delete rule:'), sg.Input(size=(4,1),key='del_rule'), sg.Button('Delete attribute:'), sg.Input(size=(width,1),key='del_attr')]
    actions3 = [sg.Open(), sg.Button('Increase Table size'), sg.Button('Remove changes'), sg.Button('Delete rule set'), sg.Button('Update & Save'), ]
    layout = [intro, scrollable_set, actions1, actions2, actions3]
    new_window = sg.Window('Window Title', return_keyboard_events=True).Layout(layout)
    window.close()
    window = new_window
    
def display_set(window):
    global ruleset
    for k in range(ruleset.m):
        elem = window[(-1,k)]
        val = ruleset.attr_names[k]
        elem.update(val)
    for i in range(ruleset.n):
        for j in range(ruleset.m):
            try:
                elem = window[(i,j)]
                val = ruleset.get_val(i,j)
                if elem is not None:# and val is not float('nan'):
                    if type(val) is bool:
                        #Necessary to avoid a change from boolean to int
                        if val: elem.update('True')
                        else: elem.update('False')
                    else:
                        elem.update(val)
            except:
                pass

def update(values):
    global ruleset
    global nbr_rows
    global nbr_cols
    print("start update")
    problem = False
    name_change = False
    rule_to_add = False
    attr_to_add = False
    old_set = copy.deepcopy(ruleset)
    warning = "\nNo changes were saved. Try again after fixing values."

    #filling in ruleset that was empty, no previous loop has been entered since self.m == 0 and self.n == 0
    if ruleset.n == 0 and (values[0,0] != '' or values[-1,0] != ''):
        if values[(-1,0)] != 'Rec' and values[(-1,0)] != 'Recommendation':
            problem = True
            sg.popup_ok("Your ruleset needs attributes names with the first one being 'Rec' or 'Recommendation.")
        if values[0,0] == '':
            problem = True
            sg.popup_ok("Your ruleset needs at least one rule to be created")
        attributes = []; j=0
        while values[(-1,j)] != '' and j < nbr_cols:
            attributes += [values[(-1,j)]]
            j += 1
        rules_list = []
        i = 0
        while values[(i,0)] != '' and i < nbr_rows:
            vals = [values[(i,0)]]
            for j in range(1,len(attributes)):
                input_str = values[(i,j)]
                try:
                    input_val = parser_1.parse_val(input_str)
                    vals += [input_val]
                except ValueError as ve:
                    problem = True
                    sg.popup_ok(str(ve) + " Position: ("+str(i)+","+str(j)+")"+warning)
                    break
            rule_dict = col.OrderedDict({k:v for k,v in zip(attributes,vals)})
            print("rule dict: "+str(rule_dict))
            rules_list += [rule_dict]
            i+=1
        ruleset = RuleSet(rules_list)
        print("ruleset has been created with rule list:" + str(rules_list))
    
    #Check for change in attribute names
    for j in range(old_set.m):
        if values[(-1,j)] != old_set.attr_names[j]:
            old_set.attr_names[j] = values[(-1,j)]
            name_change = True
    if name_change:
        try:
            ruleset.update_attr(old_set.attr_names)
        except ValueError as ve:
            problem = True
            sg.popup_ok(str(ve)+warning)

    #Check for new rules (without verifying compatibility of attribute value types)
    for i in range(ruleset.n,nbr_rows):
        if values[(i,0)] != '':
            if i != ruleset.n:
                problem = True
                sg.popup_ok("New rule must be added on first available row."+warning)
            else:
                rec_str = values[(i,0)]
                val_list = []
                for j in range(1,ruleset.m):
                    input_str = values[(i,j)]
                    try:
                        input_val = parser_1.parse_val(input_str)
                        val_list += [input_val]
                        rule_to_add = True
                    except ValueError:
                        problem = True
                        sg.popup_ok("Value in new rule doesn't have an appropriate format. Value: "+str(input_str)+ " Position: ("+str(i)+","+str(j)+")"+warning)
                if rule_to_add:
                    try:
                        print("rule to add: " + str(rec_str)+" "+str(val_list))
                        ruleset.add_rule(rec_str,val_list)
                    except ValueError as ve:
                        problem = True
                        sg.popup_ok(str(ve)+warning)
                    except TypeError as te:
                        problem = True
                        sg.popup_ok(str(te)+warning)

    #Check for new attributes (without verifying compatibility of attribute value types)
    for j in range(ruleset.m,nbr_cols):
        print(ruleset.m)
        if values[(-1,j)] != '':
            if ruleset.n > 0 and j != ruleset.m:
                problem = True
                sg.popup_ok("New attribute must be added on first available column."+warning)
            else:
                attributes = values[(-1,j)]
                val_list = []
                for i in range(0,ruleset.n):
                        input_str = values[(i,j)]
                        try:
                            input_val = parser_1.parse_val(input_str)
                            val_list += [input_val]
                            attr_to_add = True
                        except ValueError:
                            problem = True
                            sg.popup_ok("Value in new attribute doesn't have an appropriate format. Value: "+str(input_str)+ " Position: ("+str(i)+","+str(j)+")"+warning)
                if attr_to_add:
                    try:
                        ruleset.add_attr(attributes,val_list)
                    except ValueError as ve:
                        problem = True
                        sg.popup_ok(str(ve)+warning)
                    except TypeError as te:
                        problem = True
                        sg.popup_ok(str(te)+warning)

    print("n: "+str(ruleset.n))
    
    #Check for changes in values and verifies compatibility between types (includes values of new rules and attributes to include them in the type compatibility check)
    if not problem:
        #Check in recommendations (type is string so no verification to perform)
        for i in range(old_set.n):
            input_str = values[(i,0)]
            if input_str != ruleset.get_val(i,0): #recommendation has been changed
                ruleset.update_val(i,0,input_str)
        #Check for other values
        for j in range(1,ruleset.m):
            col_type = None
            for i in range(ruleset.n):
                input_str = values[(i,j)]
                try:
                    input_val = parser_1.parse_val(input_str)
                    old_val = ruleset.get_val(i,j)
                    #Check for type mismatch within column
                    if col_type is None and not pd.isna(input_val):
                        col_type = type(input_val)
                    if (not pd.isna(input_val)) and (col_type is not None) and (not ruleset.has_type(input_val,col_type)):
                            problem = True
                            sg.popup_ok("Wrong value type for attribute " + ruleset.attr_names[j] + " in rule " + str(i) + " or a preceding one."+warning)
                            print("inputval: "+str(type(input_val))+str(input_val)+" old_val: "+str(type(old_val))+str(old_val)+ " col_type: "+str(col_type))
                            print("ruleset.same_type(input_val,col_type): " + str(ruleset.same_type(input_val,col_type)))
                            break #Avoid to show error for every following rule
                    else:
                        #Check for value change. Necessary to check for types to notice difference between int 1 or 0 and booleans
                        if input_val != old_val or not ruleset.same_type(input_val,old_val):
                            #print("input_val type: " +str(type(input_val)) + "old_val type: " +str(type(old_val)))
                            try:
                                #print("input_val type: " +str(type(input_val)) + str(input_val)+ "old_val type: " +str(type(old_val))+str(old_val) + " col_type "+str(col_type))
                                ruleset.update_val(i,j,input_val)
                            except TypeError as te:
                                problem = True
                                sg.popup_ok("All values of an attribute must have the same type which can't be modified after it has been defined.\nError for attribute " + ruleset.attr_names[j] +warning)
                except ValueError as ve:
                    problem = True
                    sg.popup_ok(str(ve) + " Position: ("+str(i)+","+str(j)+")"+warning)

    #check for the presence of inputs outside of the range of considered rules and attributes
    if not problem:
        for i in range(ruleset.n,nbr_rows):
            for j in range(1,nbr_cols):
                if values[(i,j)] != '':
                    sg.popup_ok("The input at position ("+str(i)+","+str(j)+") falls outside of the considered rules and attributes and was not saved in the ruleset.")
        for j in range(ruleset.m,nbr_cols):
            for i in range(ruleset.n):
                if values[(i,j)] != '':
                    sg.popup_ok("The input at position ("+str(i)+","+str(j)+") falls outside of the considered rules and attributes and was not saved in the ruleset.")

    if problem:
        # update could not be completed => restore original state of ruleset in memory
        ruleset = copy.deepcopy(old_set)
        print("problem")
        print(ruleset)
        print("n: "+str(ruleset.n))
        #print("---idm---")
        #print(ruleset.idm)
        #print("---pm---")
        #print(ruleset.pm)
        return False
    else:
        print("success")
        print(ruleset)
        #print("---idm---")
        #print(ruleset.idm)
        #print("---pm---")
        #print(ruleset.pm)
        return True


if __name__ == '__main__':
    run_gui()
