'''
   Python package that makes it easier to write code that uses the BoostSRL java package, without having
   to create the data then run the jar manually.

   Name:         boostsrl.py
   Author:       Alexander L. Hayes
   Updated:      August 8, 2017
   License:      GPLv3
'''

from __future__ import print_function
import os
import re
import sys

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

def call_process(call):
    '''Create a subprocess and wait for it to finish. Error out if errors occur.'''
    try:
        p = subprocess.Popen(call, shell=True)
        os.waitpid(p.pid, 0)
    except:
        raise(Exception('Encountered problems while running process: ', call))

    
def write_to_file(content, path):
    '''Takes a list (content) and a path/file (path) and writes each line of the list to the file location.'''
    with open(path, 'w') as f:
        for line in content:
            f.write(line + '\n')
    f.close()

class modes(object):
    
    def __init__(self, background, loadAllLibraries=False, useStdLogicVariables=False, usePrologVariables=False,
                 recursion=False, lineSearch=False, resampleNegs=False,
                 treeDepth=None, maxTreeDepth=None, nodeSize=None, numOfClauses=None, numOfCycles=None, minLCTrees=None, incrLCTrees=None):
        self.loadAllLibraries = loadAllLibraries
        self.useStdLogicVariables = useStdLogicVariables
        self.usePrologVariables = usePrologVariables
        # Note to self: check further into the difference between treeDepth and maxTreeDepth
        self.treeDepth = treeDepth
        self.maxTreeDepth = maxTreeDepth
        self.nodeSize = nodeSize
        self.numOfClauses = numOfClauses
        self.numOfCycles = numOfCycles
        self.minLCTrees = minLCTrees
        self.incrLCTrees = incrLCTrees
        self.recursion = recursion
        self.lineSearch = lineSearch
        self.resampleNegs = resampleNegs
        #self.queryPred = 'advisedby/2'

        # Many of the arguments in the modes object are optional this shows us the values of the ones that are neither false nor none.
        relevant = [[attr, value] for attr, value in self.__dict__.iteritems() if (value is not False) and (value is not None)]

        background_knowledge = []
        for a, v in relevant:
            if v is True:
                s = a + ': ' + str(v).lower() + '.'
                background_knowledge.append(s)
            else:
                s = 'setParam: ' + a + '=' + str(v) + '.'
                background_knowledge.append(s)

        for pred in background:
            background_knowledge.append('mode: ' + pred)

        # Write the newly created background_knowledge to a file: background.txt
        write_to_file(background_knowledge, 'boostsrl/background.txt')
            
    def check_exists(self, predicate):
        pass

    def infer_modes(self, background):
        pass
        
class train(object):
    
    def __init__(self, target, train_pos, train_neg, train_facts, save=False, advice=False, softm=False, alpha=0.5, beta=-2, trees=10):
        self.target = target
        self.train_pos = train_pos
        self.train_neg = train_neg
        self.train_facts = train_facts
        self.advice = advice
        self.softm = softm
        self.alpha = alpha
        self.beta = beta
        self.trees = trees

        write_to_file(self.train_pos, 'boostsrl/train/train_pos.txt')
        write_to_file(self.train_neg, 'boostsrl/train/train_neg.txt')
        write_to_file(self.train_facts, 'boostsrl/train/train_facts.txt')
        
        CALL = '(cd boostsrl; java -jar v1-0.jar -l -train train/ -target ' + self.target + \
               ' -trees ' + str(self.trees) + ' > train_output.txt 2>&1)'
        call_process(CALL)

    def test_cases(self):
        # test that train_pos, train_neg (etc.) are lists of strings
        # tests that each string is in predicate-logic notation.
        # check to make sure there are no references that are not present in the modes object.
        # check that train_bk.txt and test_bk.txt exist, and both point to a background file.
        pass
        
    def tree(self, treenumber):
        # Tree number is between 0 and the self.trees.
        if (treenumber > (self.trees - 1)):
            raise Exception('Tried to find a tree that does not exist.')
        else:
            tree_file = 'boostsrl/train/models/bRDNs/Trees/' + self.target + 'Tree' + str(treenumber) + '.tree'
            with open(tree_file, 'r') as f:
                tree_output = f.read()
            return tree_output

    def get_training_time(self):
        '''Return the training time as a float representing the total number of seconds seconds.'''
        import re
        text = open('boostsrl/train_output.txt').read()
        line = re.findall(r'% Total learning time \(\d* trees\):.*', text)
        # Remove the last character "." from the line and split it on spaces.
        splitline = line[0][:-1].split()
        seconds = []
        if 'milliseconds' in splitline:
            seconds.append((float(splitline[splitline.index('milliseconds') - 1])) / 1000)
        if 'seconds' in splitline:
            seconds.append(float(splitline[splitline.index('seconds') - 1]))
        if 'minutes' in splitline:
            seconds.append(float(splitline[splitline.index('minutes') - 1]) * 60)
        if 'hours' in splitline:
            seconds.append(float(splitline[splitline.index('hours') - 1]) * 3600)
        if 'days' in splitline:
            seconds.append(float(splitline[splitline.index('days') - 1]) * 86400)
        return sum(seconds)

class test(object):

    def __init__(self, model, test_pos, test_neg, test_facts, trees=10):
        write_to_file(test_pos, 'boostsrl/test/test_pos.txt')
        write_to_file(test_neg, 'boostsrl/test/test_neg.txt')
        write_to_file(test_facts, 'boostsrl/test/test_facts.txt')

        self.target = model.target

        CALL = '(cd boostsrl; java -jar v1-0.jar -i -model train/models/ -test test/ -target ' + self.target + \
               ' -trees ' + str(trees) + ' -aucJarPath . > test_output.txt 2>&1)'
        call_process(CALL)
    
    def summarize_results(self):
        import re
        text = open('boostsrl/test_output.txt').read()
        line = re.findall(r'AUC ROC.*|AUC PR.*|CLL.*|Precision.*|Recall.*|%   F1.*', text)
        line = [word.replace(' ','').replace('\t','').replace('%','').replace('atthreshold=',',') for word in line]
        
        results = {
            'AUC ROC': line[0][line[0].index('=')+1:],
            'AUC PR': line[1][line[1].index('=')+1:],
            'CLL': line[2][line[2].index('=')+1:],
            'Precision': line[3][line[3].index('=')+1:],
            'Recall': line[4][line[4].index('=')+1:],
            'F1': line[5][line[5].index('=')+1:]
        }
        return results
        
    def inference_results(self):

        results_file = 'boostsrl/test/results_' + self.target + '.db'
        inference_dict = {}
        
        with open(results_file, 'r') as f:
            for line in f.read().splitlines():
                line = line.split()
                inference_dict[line[0]] = float(line[1])
        return inference_dict
