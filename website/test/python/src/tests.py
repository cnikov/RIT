import unittest
import pandas as pd
import tree 
import tree_compare
import rule_set
from relation import *
from connection import *
# import required module

class TestparserMethods(unittest.TestCase):

    def test_parse(self):
        #good examples
        csv1 = "OR($OBJECT.open(...)"
        csv2 = "AND(NOT(frommarkupsafeimport$O\n...\nMarkup(...)\n...\n))"
        csv3 = "AND($M.update(DEBUG=True);$M.update(DEBUG=False);$M.config['DEBUG']=True;$M.config['DEBUG']=False)"
        csv4 = "AND(OR(AND(-----BEGIN(?i)([dr]sa|ec|openssh|encrypted)?PRIVATEKEY-----$KEY);AND(-----BEGINPRIVATEKEY-----\n$KEY\n)))"
        csv5 = "AND(OR(NOT($CONNECTION.execute($SQL+self._tables,...)\n);$CONNECTION.execute($SQL+...,...)\n;NOT($CONNECTION.execute($SQL%self._tables,...)\n);$CONNECTION.execute($SQL%...,...)\n;NOT($CONNECTION.execute($SQL.format(self._tables),...)\n);$CONNECTION.execute($SQL.format(...),...)\n;AND(NOT($QUERY=$SQL+self._tables\n...\n$CONNECTION.execute($QUERY,...)\n\n...\);$QUERY=$SQL+...\n...\n$CONNECTION.execute($QUERY,...)\n\n...\);AND(NOT($QUERY=$SQL%self._tables\n...\n$CONNECTION.execute($QUERY,...)\n\n...\);$QUERY=$SQL%...\n...\n$CONNECTION.execute($QUERY,...)\n\n...\);AND(NOT($QUERY=$SQL.format(self._tables)\n...\n$CONNECTION.execute($QUERY,...)\n\n...\);$QUERY=$SQL.format(...)\n...\n$CONNECTION.execute($QUERY,...)\n\n...\);AND(OR($QUERY=f""...{...}...""\n...\n$CONNECTION.execute($QUERY,...)\n\n...\n;$QUERY=f""...\n$CONNECTION.execute($QUERY,...)\n\n...{...}...""\n...\n;$QUERY=f""...{...\n$CONNECTION.execute($QUERY,...)\n\n...}...""\n...\n;$QUERY=f""...{...}...\n$CONNECTION.execute($QUERY,...)\n\n...""\n...\n))))"
        csv6 = "AND(OR($CONNECTION.execute($SQL+$VAL,...)\n;$CONNECTION.execute($SQL%$VAL,...)\n;$CONNECTION.execute($SQL.format($VAL),...)\n;cr.execute($SQL.format($VAL),...)\n;AND($QUERY=$SQL+$VAL\n...\n$CONNECTION.execute($QUERY,...)\n\n...\);AND($QUERY=$SQL%$VAL\n...\n$CONNECTION.execute($QUERY,...)\n\n...\);AND($QUERY=$SQL.format($VAL)\n...\n$CONNECTION.execute($QUERY,...)\n\n...\);AND(OR($QUERY=f""...{...}...""\n...\n$CONNECTION.execute($QUERY,...)\n\n...\n;$QUERY=f""...\n$CONNECTION.execute($QUERY,...)\n\n...{...}...""\n...\n;$QUERY=f""...{...\n$CONNECTION.execute($QUERY,...)\n\n...}...""\n...\n;$QUERY=f""...{...}...\n$CONNECTION.execute($QUERY,...)\n\n...""\n...\n)))"
        csv7 = "AND(OR(AND(OR($CONNECTION.error|log|debug|warn|warning(""...""+$VALUE);$CONNECTION.error|log|debug|warn|warning(""...""%$VALUE)))AND(OR(OR($CONNECTION.error(error);$CONNECTION.error(\blog\b);$CONNECTION.error(\bdebug\b);$CONNECTION.error(\bwarn\b);$CONNECTION.error(\bwarning\b);$CONNECTION.error(\be\b);$CONNECTION.error(\berr\b);$CONNECTION.error(\bcontent\b));OR($CONNECTION.log(error);$CONNECTION.log(\blog\b);$CONNECTION.log(\bdebug\b);$CONNECTION.log(\bwarn\b);$CONNECTION.log(\bwarning\b);$CONNECTION.log(\be\b);$CONNECTION.log(\berr\b);$CONNECTION.log(\bcontent\b));OR($CONNECTION.debug(error);$CONNECTION.debug(\blog\b);$CONNECTION.debug(\bdebug\b);$CONNECTION.debug(\bwarn\b);$CONNECTION.debug(\bwarning\b);$CONNECTION.debug(\be\b);$CONNECTION.debug(\berr\b);$CONNECTION.debug(\bcontent\b));OR($CONNECTION.warn(error);$CONNECTION.warn(\blog\b);$CONNECTION.warn(\bdebug\b);$CONNECTION.warn(\bwarn\b);$CONNECTION.warn(\bwarning\b);$CONNECTION.warn(\be\b);$CONNECTION.warn(\berr\b);$CONNECTION.warn(\bcontent\b));OR($CONNECTION.warning(error);$CONNECTION.warning(\blog\b);$CONNECTION.warning(\bdebug\b);$CONNECTION.warning(\bwarn\b);$CONNECTION.warning(\bwarning\b);$CONNECTION.warning(\be\b);$CONNECTION.warning(\berr\b);$CONNECTION.warning(\bcontent\b)))))"
        csv8 = "AND(OR(r:_?qcontext;r:_?eval_context);NOT(r:def\s[a-zA-Z0-9\_]*_qcontext);NOT(r:def\s[a-zA-Z0-9\_]*_eval_context);NOT(r:\bminimal_qcontext);NOT(r:\bminimal_eval_context))"
        

        self.assertEqual(tree_compare.parse(csv1),(['OR',['$OBJECT.open(...)']],22))
        self.assertEqual(tree_compare.parse(csv2),(['AND', ['NOT', ['frommarkupsafeimport$O\n...\nMarkup(...)\n...\n']]], 55))
        self.assertEqual(tree_compare.parse(csv3),(['AND', ['$M.update(DEBUG=True)', '$M.update(DEBUG=False)', "$M.config['DEBUG']=True", "$M.config['DEBUG']=False"]], 99))
        self.assertEqual(tree_compare.parse(csv4),(['AND', ['OR', ['AND', ['-----BEGIN(?i)([dr]sa|ec|openssh|encrypted)?PRIVATEKEY-----$KEY'], 'AND', ['-----BEGINPRIVATEKEY-----\n$KEY\n']]]], 117))
        self.assertEqual(tree_compare.parse(csv5),(['AND', ['OR', ['NOT', ['$CONNECTION.execute($SQL+self._tables,...)\n'], '$CONNECTION.execute($SQL+...,...)\n', 'NOT', ['$CONNECTION.execute($SQL%self._tables,...)\n'], '$CONNECTION.execute($SQL%...,...)\n', 'NOT', ['$CONNECTION.execute($SQL.format(self._tables),...)\n'], '$CONNECTION.execute($SQL.format(...),...)\n', 'AND', ['NOT', ['$QUERY=$SQL+self._tables\n...\n$CONNECTION.execute($QUERY,...)\n\n...\\'], '$QUERY=$SQL+...\n...\n$CONNECTION.execute($QUERY,...)\n\n...\\'], 'AND', ['NOT', ['$QUERY=$SQL%self._tables\n...\n$CONNECTION.execute($QUERY,...)\n\n...\\'], '$QUERY=$SQL%...\n...\n$CONNECTION.execute($QUERY,...)\n\n...\\'], 'AND', ['NOT', ['$QUERY=$SQL.format(self._tables)\n...\n$CONNECTION.execute($QUERY,...)\n\n...\\'], '$QUERY=$SQL.format(...)\n...\n$CONNECTION.execute($QUERY,...)\n\n...\\'], 'AND', ['OR', ['$QUERY=f...{...}...\n...\n$CONNECTION.execute($QUERY,...)\n\n...\n', '$QUERY=f...\n$CONNECTION.execute($QUERY,...)\n\n...{...}...\n...\n', '$QUERY=f...{...\n$CONNECTION.execute($QUERY,...)\n\n...}...\n...\n', '$QUERY=f...{...}...\n$CONNECTION.execute($QUERY,...)\n\n...\n...\n']]]]], 958))
        self.assertEqual(tree_compare.parse(csv6),(['AND', ['OR', ['$CONNECTION.execute($SQL+$VAL,...)\n', '$CONNECTION.execute($SQL%$VAL,...)\n', '$CONNECTION.execute($SQL.format($VAL),...)\n', 'cr.execute($SQL.format($VAL),...)\n', 'AND', ['$QUERY=$SQL+$VAL\n...\n$CONNECTION.execute($QUERY,...)\n\n...\\'], 'AND', ['$QUERY=$SQL%$VAL\n...\n$CONNECTION.execute($QUERY,...)\n\n...\\'], 'AND', ['$QUERY=$SQL.format($VAL)\n...\n$CONNECTION.execute($QUERY,...)\n\n...\\'], 'AND', ['OR', ['$QUERY=f...{...}...\n...\n$CONNECTION.execute($QUERY,...)\n\n...\n', '$QUERY=f...\n$CONNECTION.execute($QUERY,...)\n\n...{...}...\n...\n', '$QUERY=f...{...\n$CONNECTION.execute($QUERY,...)\n\n...}...\n...\n', '$QUERY=f...{...}...\n$CONNECTION.execute($QUERY,...)\n\n...\n...\n']]]]], 620))
        self.assertEqual(tree_compare.parse(csv7),(['AND', ['OR', ['AND', ['OR', ['$CONNECTION.error|log|debug|warn|warning(...+$VALUE)', '$CONNECTION.error|log|debug|warn|warning(...%$VALUE)'], 'AND', ['OR', ['OR', ['$CONNECTION.error(error)', '$CONNECTION.error(\x08log\x08)', '$CONNECTION.error(\x08debug\x08)', '$CONNECTION.error(\x08warn\x08)', '$CONNECTION.error(\x08warning\x08)', '$CONNECTION.error(\x08e\x08)', '$CONNECTION.error(\x08err\x08)', '$CONNECTION.error(\x08content\x08)'], 'OR', ['$CONNECTION.log(error)', '$CONNECTION.log(\x08log\x08)', '$CONNECTION.log(\x08debug\x08)', '$CONNECTION.log(\x08warn\x08)', '$CONNECTION.log(\x08warning\x08)', '$CONNECTION.log(\x08e\x08)', '$CONNECTION.log(\x08err\x08)', '$CONNECTION.log(\x08content\x08)'], 'OR', ['$CONNECTION.debug(error)', '$CONNECTION.debug(\x08log\x08)', '$CONNECTION.debug(\x08debug\x08)', '$CONNECTION.debug(\x08warn\x08)', '$CONNECTION.debug(\x08warning\x08)', '$CONNECTION.debug(\x08e\x08)', '$CONNECTION.debug(\x08err\x08)', '$CONNECTION.debug(\x08content\x08)'], 'OR', ['$CONNECTION.warn(error)', '$CONNECTION.warn(\x08log\x08)', '$CONNECTION.warn(\x08debug\x08)', '$CONNECTION.warn(\x08warn\x08)', '$CONNECTION.warn(\x08warning\x08)', '$CONNECTION.warn(\x08e\x08)', '$CONNECTION.warn(\x08err\x08)', '$CONNECTION.warn(\x08content\x08)'], 'OR', ['$CONNECTION.warning(error)', '$CONNECTION.warning(\x08log\x08)', '$CONNECTION.warning(\x08debug\x08)', '$CONNECTION.warning(\x08warn\x08)', '$CONNECTION.warning(\x08warning\x08)', '$CONNECTION.warning(\x08e\x08)', '$CONNECTION.warning(\x08err\x08)', '$CONNECTION.warning(\x08content\x08)']]]]]]], 1195))
        self.assertEqual(tree_compare.parse(csv8),(['AND', ['OR', ['r:_?qcontext', 'r:_?eval_context'], 'NOT', ['r:def\\s[a-zA-Z0-9\\_]*_qcontext'], 'NOT', ['r:def\\s[a-zA-Z0-9\\_]*_eval_context'], 'NOT', ['r:\x08minimal_qcontext'], 'NOT', ['r:\x08minimal_eval_context']]], 170))

class TestBuildTreeMethods(unittest.TestCase):
    directory = "odoo-rules"
    meta = []
    def test_build_Tree(self):
        tree.buildCSV("odoo-rules")
        df = pd.read_csv('out2.csv')
        test_df = pd.read_csv('test.csv')
        tree1 = df.loc[df['id'] == "odoo-avoid_hardcoded_config_DEBUG"]['tree'].values[0]
        test_tree1 = test_df.loc[test_df['id'] == "odoo-avoid_hardcoded_config_DEBUG"]['tree'].values[0]
        tree2 = df.loc[df['id'] == "odoo-avoid_hardcoded_config_ENV"]['tree'].values[0]
        test_tree2 = test_df.loc[test_df['id'] == "odoo-avoid_hardcoded_config_ENV"]['tree'].values[0]
        tree3 = df.loc[df['id'] == "odoo-detected-aws-access-key-id-value"]['tree'].values[0]
        test_tree3 = test_df.loc[test_df['id'] == "odoo-detected-aws-access-key-id-value"]['tree'].values[0]
        tree4 = df.loc[df['id'] == "odoo-database-secret"]['tree'].values[0]
        test_tree4 = test_df.loc[test_df['id'] == "odoo-database-secret"]['tree'].values[0]
        tree5 = df.loc[df['id'] == "odoo-detected-hardcoded-key"]['tree'].values[0]
        test_tree5 = test_df.loc[test_df['id'] == "odoo-detected-hardcoded-key"]['tree'].values[0]
        tree6 = df.loc[df['id'] == "odoo-external-control-of-file-name-or-path"]['tree'].values[0]
        test_tree6 = test_df.loc[test_df['id'] == "odoo-external-control-of-file-name-or-path"]['tree'].values[0]
        tree7 = df.loc[df['id'] == "odoo-jwt-hardcoded"]['tree'].values[0]
        test_tree7 = test_df.loc[test_df['id'] == "odoo-jwt-hardcoded"]['tree'].values[0]
        tree8 = df.loc[df['id'] == "odoo-markup"]['tree'].values[0]
        test_tree8 = test_df.loc[test_df['id'] == "odoo-markup"]['tree'].values[0]
        tree9 = df.loc[df['id'] == "odoo-qweb-eval"]['tree'].values[0]
        test_tree9 = test_df.loc[test_df['id'] == "odoo-qweb-eval"]['tree'].values[0]
        tree10 = df.loc[df['id'] == "odoo-sensitive-data-in-logs"]['tree'].values[0]
        test_tree10 = test_df.loc[test_df['id'] == "odoo-sensitive-data-in-logs"]['tree'].values[0]
        tree11 = df.loc[df['id'] == "odoo-unstrusted-console-output"]['tree'].values[0]
        test_tree11 = test_df.loc[test_df['id'] == "odoo-unstrusted-console-output"]['tree'].values[0]
        tree12 = df.loc[df['id'] == "odoo-cr_execute"]['tree'].values[0]
        test_tree12 = test_df.loc[test_df['id'] == "odoo-cr_execute"]['tree'].values[0]
        tree13 = df.loc[df['id'] == "odoo-safe_eval"]['tree'].values[0]
        test_tree13 = test_df.loc[test_df['id'] == "odoo-safe_eval"]['tree'].values[0]
        tree14 = df.loc[df['id'] == "odoo-sqlalchemy-execute-raw-query"]['tree'].values[0]
        test_tree14 = test_df.loc[test_df['id'] == "odoo-sqlalchemy-execute-raw-query"]['tree'].values[0]


        self.assertEqual(tree1,test_tree1)
        self.assertEqual(tree2,test_tree2)
        self.assertEqual(tree3,test_tree3)
        self.assertEqual(tree4,test_tree4)
        self.assertEqual(tree5,test_tree5)
        self.assertEqual(tree6,test_tree6)
        self.assertEqual(tree7,test_tree7)
        self.assertEqual(tree8,test_tree8)
        self.assertEqual(tree9,test_tree9)
        self.assertEqual(tree10,test_tree10)
        self.assertEqual(tree11,test_tree11)
        self.assertEqual(tree12,test_tree12)
        self.assertEqual(tree13,test_tree13)
        self.assertEqual(tree14,test_tree14)


    def test_find_occ(self):
        tree.buildCSV("odoo-rules")
        df = pd.read_csv('out2.csv')
        tree1 = df.loc[df['id'] == "odoo-avoid_hardcoded_config_DEBUG"]['tree'].values[0]
        tree2 = df.loc[df['id'] == "odoo-avoid_hardcoded_config_ENV"]['tree'].values[0]
        tree3 = df.loc[df['id'] == "odoo-detected-aws-access-key-id-value"]['tree'].values[0]
        tree4 = df.loc[df['id'] == "odoo-database-secret"]['tree'].values[0]
        tree5 = df.loc[df['id'] == "odoo-detected-hardcoded-key"]['tree'].values[0]
        tree6 = df.loc[df['id'] == "odoo-external-control-of-file-name-or-path"]['tree'].values[0]
        tree7 = df.loc[df['id'] == "odoo-jwt-hardcoded"]['tree'].values[0]
        tree8 = df.loc[df['id'] == "odoo-markup"]['tree'].values[0]
        tree9 = df.loc[df['id'] == "odoo-qweb-eval"]['tree'].values[0]
        tree10 = df.loc[df['id'] == "odoo-sensitive-data-in-logs"]['tree'].values[0]
        tree11 = df.loc[df['id'] == "odoo-unstrusted-console-output"]['tree'].values[0]
        tree12 = df.loc[df['id'] == "odoo-cr_execute"]['tree'].values[0]


        self.assertEqual(tree.find_occ(tree1,"...",0),0)
        self.assertEqual(tree.find_occ(tree2,"...",0),0)
        self.assertEqual(tree.find_occ(tree3,"...",0),0)
        self.assertEqual(tree.find_occ(tree4,"...",1),66)
        self.assertEqual(tree.find_occ(tree4,"...",2),73)
        self.assertEqual(tree.find_occ(tree4,"...",3),93)
        self.assertEqual(tree.find_occ(tree5,"...",0),0)
        self.assertEqual(tree.find_occ(tree6,"...",1),34)
        self.assertEqual(tree.find_occ(tree6,"...",2),45)
        self.assertEqual(tree.find_occ(tree6,"...",3),49)
        self.assertEqual(tree.find_occ(tree7,"...",1),49)
        self.assertEqual(tree.find_occ(tree7,"...",2),63)
        self.assertEqual(tree.find_occ(tree7,"...",3),68)
        self.assertEqual(tree.find_occ(tree7,"...",4),75)
        self.assertEqual(tree.find_occ(tree7,"...",5),90)
        self.assertEqual(tree.find_occ(tree7,"...",6),99)
        self.assertEqual(tree.find_occ(tree7,"...",7),104)
        self.assertEqual(tree.find_occ(tree7,"...",8),111)
        self.assertEqual(tree.find_occ(tree7,"...",9),126)
        self.assertEqual(tree.find_occ(tree7,"...",10),138)
        self.assertEqual(tree.find_occ(tree7,"...",11),143)
        self.assertEqual(tree.find_occ(tree7,"...",12),150)
        self.assertEqual(tree.find_occ(tree7,"...",13),165)
        self.assertEqual(tree.find_occ(tree7,"...",14),175)
        self.assertEqual(tree.find_occ(tree7,"...",15),180)
        self.assertEqual(tree.find_occ(tree7,"...",16),187)
        self.assertEqual(tree.find_occ(tree7,"...",17),202)
        self.assertEqual(tree.find_occ(tree7,"...",18),215)
        self.assertEqual(tree.find_occ(tree7,"...",19),220)
        self.assertEqual(tree.find_occ(tree7,"...",20),227)
        self.assertEqual(tree.find_occ(tree7,"...",21),242)
        self.assertEqual(tree.find_occ(tree7,"...",22),255)
        self.assertEqual(tree.find_occ(tree7,"...",23),260)
        self.assertEqual(tree.find_occ(tree7,"...",24),267)
        self.assertEqual(tree.find_occ(tree7,"...",25),282)
        self.assertEqual(tree.find_occ(tree7,"...",26),294)
        self.assertEqual(tree.find_occ(tree7,"...",27),299)
        self.assertEqual(tree.find_occ(tree7,"...",28),306)
        self.assertEqual(tree.find_occ(tree7,"...",29),338)
        self.assertEqual(tree.find_occ(tree7,"...",30),346)
        self.assertEqual(tree.find_occ(tree8,"...",1),32)
        self.assertEqual(tree.find_occ(tree8,"...",2),44)
        self.assertEqual(tree.find_occ(tree8,"...",3),50)
        self.assertEqual(tree.find_occ(tree9,"...",0),0)
        self.assertEqual(tree.find_occ(tree10,"...",1),7)
        self.assertEqual(tree.find_occ(tree10,"...",2),47)
        self.assertEqual(tree.find_occ(tree10,"...",3),58)
        self.assertEqual(tree.find_occ(tree11,"...",1),56)
        self.assertEqual(tree.find_occ(tree11,"...",2),111)
        self.assertEqual(tree.find_occ(tree12,"...",1),37)
        self.assertEqual(tree.find_occ(tree12,"...",2),74)
        self.assertEqual(tree.find_occ(tree12,"...",3),119)
        self.assertEqual(tree.find_occ(tree12,"...",4),155)
        self.assertEqual(tree.find_occ(tree12,"...",5),184)
        self.assertEqual(tree.find_occ(tree12,"...",6),216)
        self.assertEqual(tree.find_occ(tree12,"...",7),224)
        self.assertEqual(tree.find_occ(tree12,"...",8),252)
        self.assertEqual(tree.find_occ(tree12,"...",9),284)
        self.assertEqual(tree.find_occ(tree12,"...",10),292)
        self.assertEqual(tree.find_occ(tree12,"...",11),328)
        self.assertEqual(tree.find_occ(tree12,"...",12),360)
        self.assertEqual(tree.find_occ(tree12,"...",13),368)
        self.assertEqual(tree.find_occ(tree12,"...",14),390)
        self.assertEqual(tree.find_occ(tree12,"...",15),394)
        self.assertEqual(tree.find_occ(tree12,"...",16),398)
        self.assertEqual(tree.find_occ(tree12,"...",17),404)
        self.assertEqual(tree.find_occ(tree12,"...",18),436)
        self.assertEqual(tree.find_occ(tree12,"...",19),444)
        self.assertEqual(tree.find_occ(tree12,"...",20),459)
        self.assertEqual(tree.find_occ(tree12,"...",21),491)
        self.assertEqual(tree.find_occ(tree12,"...",22),499)
        self.assertEqual(tree.find_occ(tree12,"...",23),503)
        self.assertEqual(tree.find_occ(tree12,"...",24),507)
        self.assertEqual(tree.find_occ(tree12,"...",25),513)
        self.assertEqual(tree.find_occ(tree12,"...",26),528)
        self.assertEqual(tree.find_occ(tree12,"...",27),532)
        self.assertEqual(tree.find_occ(tree12,"...",28),564)
        self.assertEqual(tree.find_occ(tree12,"...",29),572)
        self.assertEqual(tree.find_occ(tree12,"...",30),576)
        self.assertEqual(tree.find_occ(tree12,"...",31),582)
        self.assertEqual(tree.find_occ(tree12,"...",32),597)
        self.assertEqual(tree.find_occ(tree12,"...",33),601)
        self.assertEqual(tree.find_occ(tree12,"...",34),605)
        self.assertEqual(tree.find_occ(tree12,"...",35),637)
        self.assertEqual(tree.find_occ(tree12,"...",36),645)
        self.assertEqual(tree.find_occ(tree12,"...",37),651)


    def testBuildTreeStructure(self) : 
        tree.buildCSV("odoo-rules")
        df = pd.read_csv('out2.csv')
        tree1 = tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-avoid_hardcoded_config_DEBUG"]['tree'].values[0])[0])
        test1_tree = tree_compare.TreeNode("AND",[tree_compare.TreeNode("$M.update(DEBUG=True)"),tree_compare.TreeNode("$M.update(DEBUG=False)"),tree_compare.TreeNode("$M.config['DEBUG']=True"),tree_compare.TreeNode("$M.config['DEBUG']=False")])
        tree2 = tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-avoid_hardcoded_config_ENV"]['tree'].values[0])[0])
        test2_tree = tree_compare.TreeNode("OR",[tree_compare.TreeNode("$M.update(ENV=\"=~/^development|production$/\")"),tree_compare.TreeNode("$M.config['ENV']=\"=~/^development|production$/\""),tree_compare.TreeNode("AND",[tree_compare.TreeNode("$M.update(ENV=\"=~/^development|production$/\")"),tree_compare.TreeNode("$M.config['ENV']=\"=~/^development|production$/\"")])])       
        tree3 = tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-detected-aws-access-key-id-value"]['tree'].values[0])[0])
        test3_tree = tree_compare.TreeNode("AND",[tree_compare.TreeNode("r:\\b(A3T[A-Z0-9]|AKIA|AGPA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}\\b"),tree_compare.TreeNode("NOT",[tree_compare.TreeNode("r:(?i)example|sample|test|fake")])])
        tree4 = tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-database-secret"]['tree'].values[0])[0])
        test4_tree = tree_compare.TreeNode("AND",[tree_compare.TreeNode("$SECRET=$SUDO.get_param(\"database.secret\")\\n"),tree_compare.TreeNode("NOT",[tree_compare.TreeNode("def$FUNCTION(...):\\n...\\n$SECRET.encode(...)\\n")])])
        tree5 = tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-detected-hardcoded-key"]['tree'].values[0])[0])
        test5_tree = tree_compare.TreeNode("AND",[tree_compare.TreeNode("OR",[tree_compare.TreeNode("AND",[tree_compare.TreeNode("-----BEGIN(?i)([dr]sa|ec|openssh|encrypted)?PRIVATEKEY-----$KEY")]),tree_compare.TreeNode("AND",[tree_compare.TreeNode("-----BEGINPRIVATEKEY-----\\n$KEY\\n")])])])
        tree6 = tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-external-control-of-file-name-or-path"]['tree'].values[0])[0])
        test6_tree = tree_compare.TreeNode("AND",[tree_compare.TreeNode("NOT",[tree_compare.TreeNode("open(^[a-zA-Z0-9_\-\.\"]+$,...)")]),tree_compare.TreeNode("open(...,...)")])
        tree7= tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-markup"]['tree'].values[0])[0])
        test7_tree = tree_compare.TreeNode("AND",[tree_compare.TreeNode("NOT",[tree_compare.TreeNode("frommarkupsafeimport$O\\n...\\nMarkup(...)\\n...\\n")])])
        tree8 = tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-qweb-eval"]['tree'].values[0])[0])
        test8_tree = tree_compare.TreeNode("AND",[tree_compare.TreeNode("OR",[tree_compare.TreeNode("r:_?qcontext"),tree_compare.TreeNode("r:_?eval_context")]),tree_compare.TreeNode("NOT",[tree_compare.TreeNode("r:def\s[a-zA-Z0-9\_]*_qcontext")]),tree_compare.TreeNode("NOT",[tree_compare.TreeNode("r:def\s[a-zA-Z0-9\_]*_eval_context")]),tree_compare.TreeNode("NOT",[tree_compare.TreeNode("r:\\bminimal_qcontext")]),tree_compare.TreeNode("NOT",[tree_compare.TreeNode("r:\\bminimal_eval_context")])])
        tree9 = tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-sensitive-data-in-logs"]['tree'].values[0])[0])
        test9_tree = tree_compare.TreeNode("(try:\\n...\\nexceptpsycopg2.$ERRORMSGas$ERROR:\\n...\\nprint(...,$ERROR)\\n)")
        

        self.assertEqual(tree1,test1_tree)
        self.assertEqual(tree2,test2_tree)
        self.assertEqual(tree3,test3_tree)
        self.assertEqual(tree4,test4_tree)
        self.assertEqual(tree5,test5_tree)
        self.assertEqual(tree6,test6_tree)
        self.assertEqual(tree7,test7_tree)
        self.assertEqual(tree8,test8_tree)
        self.assertEqual(tree9,test9_tree)

class TestCompareTreeMethods(unittest.TestCase):

    def testEquality(self):
        tree1 = tree_compare.parse_tree(tree_compare.parse("(a)")[0])
        tree2 = tree_compare.parse_tree(tree_compare.parse("(b)")[0])
        tree3 = tree_compare.parse_tree(tree_compare.parse("OR()")[0])
        tree4 = tree_compare.parse_tree(tree_compare.parse("OR(a;b;AND(c;d;OR(e;f;NOT(z))))")[0])
        tree5 = tree_compare.parse_tree(tree_compare.parse("OR(a;b;AND(c;d;OR(e;f;NOT(x))))")[0])
        tree6 = tree_compare.parse_tree(tree_compare.parse("OR(a;b;AND(c;d;OR(e;f;NOT(...))))")[0])
        tree7 = tree_compare.parse_tree(tree_compare.parse("AND(a;OR(b;c);AND(d;e;f))")[0])
        tree8 = tree_compare.parse_tree(tree_compare.parse("AND(...)")[0])
        tree9 = tree_compare.parse_tree(tree_compare.parse("(...)")[0])
        tree10 = tree_compare.parse_tree(tree_compare.parse("AND(a;OR(b;c);AND($D;e;f))")[0])
        tree11 = tree_compare.parse_tree(tree_compare.parse("($VAR)")[0])


        self.assertTrue(rule_set.RuleSet._equals(rule_set.RuleSet,tree1,tree1))
        self.assertFalse(rule_set.RuleSet._equals(rule_set.RuleSet,tree1,tree2))
        self.assertTrue(rule_set.RuleSet._equals(rule_set.RuleSet,tree3,tree3))
        self.assertFalse(rule_set.RuleSet._equals(rule_set.RuleSet,tree1,tree3))
        self.assertFalse(rule_set.RuleSet._equals(rule_set.RuleSet,tree4,tree5))
        self.assertTrue(rule_set.RuleSet._equals(rule_set.RuleSet,tree5,tree5))
        self.assertTrue(rule_set.RuleSet._equals(rule_set.RuleSet,tree5,tree6))
        self.assertFalse(rule_set.RuleSet._equals(rule_set.RuleSet,tree6,tree6))
        self.assertFalse(rule_set.RuleSet._equals(rule_set.RuleSet,tree6,tree7))
        self.assertFalse(rule_set.RuleSet._equals(rule_set.RuleSet,tree8,tree7))
        self.assertTrue(rule_set.RuleSet._equals(rule_set.RuleSet,tree9,tree1))
        self.assertTrue(rule_set.RuleSet._equals(rule_set.RuleSet,tree7,tree10))
        self.assertTrue(rule_set.RuleSet._equals(rule_set.RuleSet,tree11,tree9))

    def testInclusion(self):
        tree.buildCSV("odoo-rules")
        df = pd.read_csv('out2.csv')
        tree1 = tree_compare.parse_tree(tree_compare.parse("(a)")[0])
        tree2 = tree_compare.parse_tree(tree_compare.parse("(b)")[0])
        tree3 = tree_compare.parse_tree(tree_compare.parse("OR()")[0])
        tree4 = tree_compare.parse_tree(tree_compare.parse("OR(a;b;AND(c;d;OR(e;f;NOT(z))))")[0])
        tree5 = tree_compare.parse_tree(tree_compare.parse("OR(a;b;AND(c;d))")[0])
        tree6 = tree_compare.parse_tree(tree_compare.parse("OR(a;b;AND(c;d;OR(e;f;NOT(...))))")[0])
        tree7 = tree_compare.parse_tree(tree_compare.parse("AND(a;OR(b;c);AND(d;e;f))")[0])
        tree8 = tree_compare.parse_tree(tree_compare.parse("AND(...;OR(b;c);AND(d;e;f))")[0])
        tree9 = tree_compare.parse_tree(tree_compare.parse("(...)")[0])
        tree10 = tree_compare.parse_tree(tree_compare.parse("OR(a;c;AND(c;d))")[0])
        tree11 = tree_compare.parse_tree(tree_compare.parse("AND(...;OR(b;c);AND(...;e;...))")[0])
        tree12 = tree_compare.parse_tree(tree_compare.parse("AND(OR())")[0])
        tree13= tree_compare.parse_tree(tree_compare.parse("AND(OR($VAR))")[0])
        tree14 = tree_compare.parse_tree(tree_compare.parse("AND(OR(a))")[0])
        tree15 = tree_compare.parse_tree(tree_compare.parse("OR(a;b;AND(c;d;OR(e;f;NOT($VAR))))")[0])
        tree16 = tree_compare.parse_tree(tree_compare.parse(df.loc[df['id'] == "odoo-avoid_hardcoded_config_DEBUG"]['tree'].values[0])[0])


        self.assertTrue(rule_set.RuleSet._contains1(rule_set.RuleSet,[tree9],[tree1]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet,[tree2],[tree1]))
        self.assertTrue(rule_set.RuleSet._contains1(rule_set.RuleSet,[tree4], [tree5]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree4], [tree10]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree7], [tree8]))
        self.assertTrue(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree8], [tree7]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree8], [tree11]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree11], [tree8]))
        self.assertTrue(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree11], [tree7]))
        self.assertTrue(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree6], [tree4]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree4], [tree6]))
        self.assertTrue(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree12], [tree3]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree3], [tree12]))
        self.assertTrue(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree13], [tree14]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree14], [tree13]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree4], [tree13]))
        self.assertTrue(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree15], [tree4]))
        self.assertTrue(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree15], [tree6]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree4], [tree15]))
        self.assertFalse(rule_set.RuleSet._contains1(rule_set.RuleSet, [tree4], [tree16]))



    def testOverlap(self):
        tree.buildCSV("odoo-rules")
        df = pd.read_csv('out2.csv')
        tree1 = tree_compare.parse_tree(tree_compare.parse("AND(AND();b)")[0])
        tree2 = tree_compare.parse_tree(tree_compare.parse("AND(AND();c)")[0])
        tree3 = tree_compare.parse_tree(tree_compare.parse("AND(a;b)")[0])
        tree4 = tree_compare.parse_tree(tree_compare.parse("AND(a;c)")[0])
        tree5 = tree_compare.parse_tree(tree_compare.parse("AND(a;c)")[0])
        overlap_tree1 = tree_compare.parse_tree(tree_compare.parse("AND(a)")[0])
        self.assertEqual(rule_set.RuleSet._overlap(rule_set.RuleSet,[tree1],[tree2]), [])
        self.assertEqual(rule_set.RuleSet._overlap(rule_set.RuleSet,[tree3],[tree4]), [overlap_tree1])
       


if __name__ == '__main__':
    unittest.main()