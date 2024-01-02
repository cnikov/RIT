# RIT (Relation identification Tool)
This project is about providing a tool with a graphical interface that identify relationship between security rules. The results of those relationship can be (overlap, equality, inclusion or difference). This tool works with security rules made with the Open source tool semgrep and is useful to detect relation between those rules and indicate where to modify them to get a rule set more efficient for code security testing.

### Table of Contents

- [Installation](#installation)
- [Alternative Installation](#installation2)
- [Usage](#usage)


## Installation
<!-- Add this anchor link at the beginning of the section -->
<a name="installation"></a>

1. Clone the repository `git clone <url>`
2. Go to website folder: `cd website`
3. Open 2 terminal to be able to launch the backend and the web application.
4. First go to the backend folder `cd backend`
5. Install dependencies: `npm install`
6. Run the backend: `npm run dev`
7. In the other terminal go to my_web folder `cd my_web`
8. Install dependencies: `npm install`
9. Run the web application: `npm run start`

## Alternative installation
<!-- Add this anchor link at the beginning of the section -->
<a name="installation2"></a>
In the case of you do not want to use the graphical interface it is possible to run the python code directly

1. Clone the repository `git clone <url>`
2. Go to website folder: `cd algorithm`
3. The rule folder is currently named odoo-rules but you can add your own rule folder.
4. go to the src folder `cd src`
5. Open the main.py and modify the line 10 with the name of your rule folder.
6. Run the main.py `python main.py`

## Usage

<a name="usage"></a>

In order to use the tool you have to create a zip archive that contains all the semgrep security rules that needs to be compared. On the main page of the tool it is possible to upload this archive.
**Warning:** this needs to be a .zip archive.
Once uploaded the algorithm run on the rules and after computing the results it display a list of relation between the rules.
It is possible to click on results individually to get the two rules that are compared and have an access to an online editor that allows to live modify the rules and download new versions of those rules.
In case of an overlap relation between two rules the editor will highlight the subtrees that match the overlapping pattern to indicate where to focus for the rule modification