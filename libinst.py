'''
Created on Apr 25, 2014

@author: hanggao
'''

class instruction(object):
   
    __inst = None
    __ready = False
    
    __type = None
    __rs = None
    __rt = None
    __rd = None
    __immediate = None
    __fori = None
    
    __rs_val = None
    __rt_val = None
    __rd_val = None
    
    __line = 0

    __decoded = False
    __WAWcheck = False
    __RAWcheck = False
    
    _WAW = False
    _RAW = False
    _STRUCT = False

    _IF_cycle = 0
    _ID_cycle = 0
    _EX_cycle = 0
    _WB_cycle = 0
    
    _PC = -1

    def __init__(self, inst):
        self.__inst = inst
    
    def setPC(self, PC):
        self._PC = PC
    
    def getPC(self):
        return self._PC
        
    def setIFcycle(self, cycle):
        self._IF_cycle = cycle
    
    def setIDcycle(self, cycle):
        self._ID_cycle = cycle
    
    def setEXcycle(self, cycle):
        self._EX_cycle = cycle
    
    def setWBcycle(self, cycle):
        self._WB_cycle = cycle
        
    def WAW(self):
        self._WAW = True
    
    def RAW(self):
        self._RAW = True
    
    def STRUCT(self):
        self._STRUCT = True
    
    def inst_s(self):
        return self.__inst    
    
    def setattrs(self, itype, rs, rt, rd, imd, fori):
        self.__type = itype
        self.__rs = rs
        self.__rt = rt
        self.__rd = rd
        self.__immediate = imd
        self.__fori = fori
    
    def getattrs(self):
        return [self.__type, self.__rs, self.__rt, self.__rd, self.__immediate, self.__fori]
    
    def getInst(self):
        return self.__inst

    def getissue(self):
        return self._ID_cycle

    def getfetch(self):
        return self._IF_cycle

    def to_string(self):
        s = self.__inst
        while len(s) < 30:
            s+=" "
        s = s +"\t"+str(self._IF_cycle)
        
        if self._ID_cycle is not None:
            s +="\t\t"+str(self._ID_cycle)
        else:
            s +="\t\t"
        
        if self._EX_cycle > 0:
            s +="\t\t"+str(self._EX_cycle)
        else:
            s +="\t\t"
        if self._WB_cycle > 0:
            s += "\t\t"+str(self._WB_cycle)
        else:
            s +="\t\t"
            
        if self._RAW:
            s +="\t\tY"
        else:
            s +="\t\tN"
        
        s +="\t\tN"
        
        if self._WAW:
            s +="\t\tY"
        else:
            s +="\t\tN"
            
        if self._STRUCT:
            s +="\t\tY"
        else:
            s +="\t\tN"
        
        return s
    
    def markunready(self):
        self.__ready = False
    
    def markready(self):
        self.__ready = True
    
    def isready(self):
        return self.__ready

    def getLine(self):
        return self._PC/4+1
    
    def setdecoded(self):
        self.__decoded = True
    
    def decoded(self):
        return self.__decoded
    
    def setWAW(self):
        self.__WAWcheck = True
    
    def WAWchecked(self):
        return self.__WAWcheck
    
    def setRAW(self):
        self.__RAWcheck = True
    
    def RAWchecked(self):
        return self.__RAWcheck
    
    def setrs(self, val):
        self.__rs_val = val
    
    def getrs(self):
        return self.__rs_val
    
    def setrt(self, val):
        self.__rt_val = val
    
    def getrt(self):
        return self.__rt_val
    
    def setrd(self, val):
        self.__rd_val = val
    
    def getrd(self):
        return self.__rd_val
    
    def getimd(self):
        return self.__immediate
    
    def setimd(self, imd):
        self.__immediate = imd