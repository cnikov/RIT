import yaml
# import required module
import gui 
import parser_1 as parser_1
import compare as compare
import tree
import os
import re
import pandas as pd
import sys
import shutil
import sys
import csv 

def main() :
    directory = "odoo-rules"
    # assign directory
    tree.buildCSV(directory)
    gui.run_gui()



if __name__ == '__main__':
    main()