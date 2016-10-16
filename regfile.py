'''
Created on Apr 25, 2014

@author: hanggao
'''

class regfile(object):

    __Rs = []
    
    def __init__(self, regs):
        for line in regs:
            word = int(line, 2)
            self.__Rs.append(word)
    
    def getword(self, idx):
        return self.__Rs[idx]
    
    def putword(self, idx, word):
        self.__Rs[idx] = word