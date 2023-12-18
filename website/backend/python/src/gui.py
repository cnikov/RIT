import src.parser_1 as parser_1
from src.rule_set import * 
from src.connection import *


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

if __name__ == '__main__':
    run_gui()
