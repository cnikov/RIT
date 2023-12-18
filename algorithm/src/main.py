# import required module
import gui 
import parser_1 as parser_1
import compare as compare
import tree
import sys


def main() :
    directory = "../odoo-rules"
    with open('output.txt', 'w') as file:
        # Redirect stdout to the file
        sys.stdout = file
        # assign directory
        tree.buildCSV(directory)
        gui.run_gui()



if __name__ == '__main__':
    main()