"""
Created on Apr 25, 2014

@author: hanggao
"""
import lib
import libinst


class slot(object):
    
    __instruction = None

    def __init__(self):
        pass
    
    def addinst(self, instruction):
        self.__instruction = instruction

    def removeinst(self):
        i =  self.__instruction
        self.__instruction = None
        return i
    
    def getinst(self):
        return self.__instruction

    def empty(self):
        return self.__instruction == None


class function_unit(object):
    _cycle = -1
    _slot = None
    _remain = -1
    
    def __init__(self, cycle):
        self._cycle = cycle
        self._slot = slot() 
    
    def getslot(self):
        return self._slot

    def empty(self):
        return self._slot.empty()
        
    def getInst(self):
        return self._slot.getinst()
    
    def clear(self):
        return self._slot.removeinst()

    def consume(self, inst):
        self._slot.addinst(inst)
        self._remain = self._cycle
    
    def work(self):
        if self.empty(): return
        self._remain -= 1
        if self._remain == 0:
            self._slot.getinst().markready()
        pass


class fp_adder(object):
    
    __fu = None
    __cycle = 0
    __piped = False
    
    def __init__(self, cycles, pipeline):
        self.__cycle = cycles
        self.__piped = pipeline
        self.__fu = []
        
        if pipeline:
            for _ in range(cycles):
                fu = function_unit(1)
                self.__fu.append(fu)     
        else:
            self.__fu.append(function_unit(cycles))
        pass
    
    def free(self):
        rs = True
        for ele in self.__fu:
            rs = rs and ele.empty()
        return rs
    
    def getInst(self):
        return self.__fu[len(self.__fu)-1].getInst()
    
    def empty(self):
        return self.__fu[len(self.__fu)-1].empty()
    
    def clear(self):
        return self.__fu[len(self.__fu)-1].clear()
    
    def consume(self, inst):
        self.__fu[0].consume(inst)
        inst.markunready()
        self.__fu[0].work()
        
    def available(self):
        return self.__fu[0].empty()
    
    def run(self):
        for i in range(len(self.__fu)):
            idx = len(self.__fu)-1-i
            if idx == 0:
                self.__fu[idx].work()
            else:
                if self.__fu[idx].empty():
                    # slot empty
                    if (not self.__fu[idx-1].empty()) and self.__fu[idx-1].getInst().isready():
                        self.__fu[idx].consume(self.__fu[idx-1].clear())
                        self.__fu[idx].work()
                    pass
                else:
                    self.__fu[idx].work()
                    # structural hazard
                    inst = self.__fu[idx-1].getInst()
                    if inst is not None:
                        inst.STRUCT()


class fp_multiplyer(object):
    
    __cycle = 0
    __piped = False
    __fu = None
    
    def __init__(self, cycles, pipeline):
        self.__cycle = cycles
        self.__piped = pipeline
        self.__fu = []
        if pipeline:
            for _ in range(cycles):
                fu = function_unit(1)
                self.__fu.append(fu)
        else:
            self.__fu.append(function_unit(cycles))
        pass

    def free(self):
        rs = True
        for ele in self.__fu:
            rs = rs and ele.empty()
        return rs
    
    def getInst(self):
        return self.__fu[len(self.__fu)-1].getInst()
    
    def clear(self):
        return self.__fu[len(self.__fu)-1].clear()
    
    def empty(self):
        return self.__fu[len(self.__fu)-1].empty()

    def consume(self, inst):
        self.__fu[0].consume(inst)
        inst.markunready()
        self.__fu[0].work()

    def available(self):
        return self.__fu[0].empty()
    
    def run(self):
        for i in range(len(self.__fu)):
            idx = len(self.__fu)-1-i
            if idx == 0:
                self.__fu[idx].work()
            else:
                if self.__fu[idx].empty():
                    # slot empty
                    if (not self.__fu[idx-1].empty()) and self.__fu[idx-1].getInst().isready():
                        self.__fu[idx].consume(self.__fu[idx-1].clear())
                        self.__fu[idx].work()
                    pass
                else:
                    self.__fu[idx].work()
                    # structural hazard
                    inst = self.__fu[idx-1].getInst()
                    if inst is not None:
                        inst.STRUCT()


class fp_divider(object):
    
    __cycle = 0
    __piped = False
    __fu = None
    
    def __init__(self, cycles, pipeline):
        self.__cycle = cycles
        self.__piped = pipeline
        self.__fu = []
        if pipeline:
            for _ in range(cycles):
                fu = function_unit(1)
                self.__fu.append(fu)
        else:
            self.__fu.append(function_unit(cycles))
        pass

    def free(self):
        rs = True
        for ele in self.__fu:
            rs = rs and ele.empty()
        return rs

    def getInst(self):
        return self.__fu[len(self.__fu)-1].getInst()
    
    def empty(self):
        return self.__fu[len(self.__fu)-1].empty()
 
    def clear(self):
        return self.__fu[len(self.__fu)-1].clear()
    
    def consume(self, inst):
        self.__fu[0].consume(inst)
        inst.markunready()
        self.__fu[0].work()

    def available(self):
        return self.__fu[0].empty()

    def run(self):
        for i in range(len(self.__fu)):
            idx = len(self.__fu)-1-i
            if idx == 0:
                self.__fu[idx].work()
            else:
                if self.__fu[idx].empty():
                    # slot empty
                    if (not self.__fu[idx-1].empty()) and self.__fu[idx-1].getInst().isready():
                        self.__fu[idx].consume(self.__fu[idx-1].clear())
                        self.__fu[idx].work()
                    pass
                else:
                    self.__fu[idx].work()
                    # structural hazard
                    inst = self.__fu[idx-1].getInst()
                    if inst is not None:
                        inst.STRUCT()


class icache(object):
    __cycle = 0
    __mem = None
    __request_num = 0
    __miss = 0
    __last_request = -1
    
    __blocks = None
    __fetch_cycle = 0
    __fetch_block = None
    __cpu = None
    
    def __init__(self, cycle, mem):
        self.__cycle = cycle
        self.__mem = mem
        self.__blocks = []
        for _ in range(4):
            self.__blocks.append([False,-1,[0,0,0,0]])
    
    def cpu(self, cpu):
        self.__cpu = cpu 
    
    def cache_hit(self, PC):
        idx = (PC & 48) >> 4
        tag = (PC & (~63)) >> 6

        if self.__blocks[idx][1] == tag and self.__blocks[idx][0] :
            return True
        else:
            return False
    
    def occupymem(self):
        self.__mem.serve(1)
    
    def fetch(self, PC):
        idx = (PC & 48) >> 4
        widx = (PC & 12) >> 2
        return self.__blocks[idx][2][widx]
    
    def numreq(self):
        return self.__request_num
    
    def setnumreq(self, num):
        self.__request_num = num
    
    def numhit(self):
        return self.__request_num-self.__miss
    
    def setnummiss(self, num):
        self.__miss = num
    
    def request(self, PC):
        
        def new_request():
            def fetch_block():
                idx = (PC & 48) >> 4
                tag = (PC & (~63)) >> 6
                addr = PC & (~15)
                words = self.__mem.fetch_inst_block(addr)
                
                if words is None:
                    return -1
                
                self.__miss+=1
                
                self.__blocks[idx][0] = False
                self.__blocks[idx][1] = tag
                self.__blocks[idx][2][0] = words[0]
                self.__blocks[idx][2][1] = words[1]
                self.__blocks[idx][2][2] = words[2]
                self.__blocks[idx][2][3] = words[3]
                self.__fetch_block = self.__blocks[idx]
                return 1
            
            self.__last_request = PC
            if self.cache_hit(PC):
                self.__fetch_cycle = self.__cycle
            else:
                if self.__mem.getServe() != 2 and self.__cpu.cycle() != self.__mem.servecycle():
                    
                    self.__fetch_cycle = 2*(self.__mem.getCycle()+self.__cycle)
                    if fetch_block() < 0:
                        self.__fetch_cycle = 1
                        self.__mem.serve(-1)
                    else:
                        self.__mem.serve(1)

                else:
                    self.__fetch_cycle = 0
            pass
        
        if PC != self.__last_request:
            if self.__mem.validinst(PC):
                self.__request_num += 1
            self.__last_request = PC
        
        #no current request served
        if self.__fetch_cycle <= 0:
            new_request()
    
        self.__fetch_cycle -= 1

        if self.__fetch_cycle == 0:
            if self.__mem.getServe() == 1:
                self.__mem.serve(-1)
                self.__fetch_block[0] = True
            
            if self.cache_hit(PC):
                return self.fetch(PC)
            #PC has changed
            else:
                new_request()
        return None


class dcache(function_unit):
    __mem = None
    __blocks = []
    __request_num = 0
    __miss = 0
    __last_request = -1
    __fetch_cycle = 0
    
    __cycle = 0
    
    def __init__(self, cycle, mem):
        self._cycle = cycle
        self._slot = slot()
        self.__mem = mem
        bset1 = [[False,-1,-1,[0,0,0,0]],[False,-1,-1,[0,0,0,0]]]
        bset2 = [[False,-1,-1,[0,0,0,0]],[False,-1,-1,[0,0,0,0]]]
        self.__blocks.append(bset1)
        self.__blocks.append(bset2)
          
    def numreq(self):
        return self.__request_num
    
    def numhit(self):
        return self.__request_num-self.__miss
    
    def consume(self, inst):
        self._slot.addinst(inst)
        inst.markunready()
        self._remain = self._cycle    
    
    def fetch(self, PC):
        idx = (PC & 16) >> 4
        widx = (PC & 12) >> 2
        tag = (PC & (~31)) >> 5
        if tag == self.__blocks[0][idx][2]:
            self.__blocks[0][idx][1] = self.__cycle
            return self.__blocks[0][idx][3][widx]
        
        if tag == self.__blocks[1][idx][2]:
            self.__blocks[1][idx][1] = self.__cycle
            return self.__blocks[1][idx][3][widx]
        
        return None
    
    def write(self, PC, val):
        idx = (PC & 16) >> 4
        widx = (PC & 12) >> 2
        tag = (PC & (~31)) >> 5
        
        if tag == self.__blocks[0][idx][2]:
            self.__blocks[0][idx][1] = self.__cycle
            self.__blocks[0][idx][3][widx] = val
            self.__blocks[0][idx][0] = False
        
        if tag == self.__blocks[1][idx][2]:
            self.__blocks[1][idx][1] = self.__cycle
            self.__blocks[1][idx][3][widx] = val
            self.__blocks[1][idx][0] = False
            
    def request(self, PC):
        
        def new_request():
            def fetch_block():
                idx = (PC & 16) >> 4
                tag = (PC & (~31)) >> 5
                addr = PC & (~15)
                words = self.__mem.fetch_data_block(addr)
                
                if words is None:
                    return -1
                
                self.__miss+=1
                
                block = None
                if (not self.__blocks[0][idx][0]) and self.__blocks[0][idx][1] == -1:
                    block = self.__blocks[0][idx]
                elif not self.__blocks[1][idx][0] and self.__blocks[1][idx][1] == -1:
                    block = self.__blocks[0][idx]
                else:
                    if self.__blocks[0][idx][1] > self.__blocks[1][idx][1]:
                        block = self.__blocks[1][idx]
                        if not block[0]:
                            baddr = (block[2] << 5)|(idx<<4)
                            self.__mem.writeBlock(block[3], baddr)
                    else:
                        block = self.__blocks[0][idx]
                        if not block[0]:
                            baddr = (block[2] << 5)|(idx<<4)
                            self.__mem.writeBlock(block[3], baddr)
                
                block[0] = False
                block[1] = self.__cycle
                block[2] = tag
                block[3][0] = words[0]
                block[3][1] = words[1]
                block[3][2] = words[2]
                block[3][3] = words[3]
                self.__fetch_block = block
                return 1
            
            self.__last_request = PC
          
            if self.cache_hit(PC): 
                self.__fetch_cycle = self._cycle
            else:
                if self.__mem.getServe() != 1:
                    self.__fetch_cycle = 2*(self.__mem.getCycle()+self._cycle)
                    if fetch_block() < 0:
                        self.__fetch_cycle = 1
                        self.__mem.serve(-1)
                    else:
                        self.__mem.serve(2)
                else:
                    self.__fetch_cycle = 0
            pass
        
        if PC != self.__last_request:
            self.__request_num += 1
            self.__last_request = PC
        
        #no current request served
        if self.__fetch_cycle <= 0:
            new_request()
        
        self.__fetch_cycle -= 1
        if self.__fetch_cycle == 0:
            if self.__mem.getServe() == 2:
                self.__mem.serve(-1)
                self.__fetch_block[0] = True
            
            if self.cache_hit(PC):
                self.__last_request = None
                return self.fetch(PC)
            #PC has changed
            else:
                new_request()
        
        return None
    
    def work(self):
        self.__cycle+=1
        inst = self.getInst()
        if inst is not None:
            if inst.isready():
                return
            
            attrs = inst.getattrs()
            itype = attrs[0]
            if itype=="lw":
                data = self.request(inst.getimd())  
        
                if data is not None:
                    inst.setimd(data)
                    inst.markready()
        
            elif itype=="sw":
                data = self.request(inst.getimd())
                if data is not None:
                    self.write(inst.getimd(), inst.getrt())
                    inst.markready()
                    
            elif itype=="l.d":
                data = self.request(inst.getimd())
                if data is not None:
                    # second time
                    if inst.getrs() == "l.d":
                        inst.setimd(0)
                        inst.markready()
                    # first time
                    else:
                        inst.setrs("l.d")
                        inst.setimd(inst.getimd()+4)
                pass
            elif itype=="s.d":
                data = self.request(inst.getimd())
                if data is not None:
                    # second time
                    if inst.getrs() == "s.d":
                        inst.setimd(0)
                        inst.markready()
                    # first time
                    else:
                        inst.setrs("s.d")
                        self.write(inst.getimd(), 0)
                        inst.setimd(inst.getimd()+4)                       
                pass
            else:
                inst.markready()
        pass
    
    def cache_hit(self, PC):
        idx = (PC & 16) >> 4
        tag = (PC & (~31)) >> 5
        judge1 = self.__blocks[0][idx][2] == tag
        judge2 = self.__blocks[1][idx][2] == tag
        
        return judge1 or judge2
        
    def occupymem(self):
        self.__mem.serve(2)


class memory(object):
    '''
    classdocs
    '''
    DATA_START = 0x100
    INST_START = 0x0
    
    __data = []
    __inst = []
    __cycle = 0
    __serve = -1
    __cpu = None
    __serve_cycle = -1
    
    def __init__(self, insts, data, cycle):
        self.__inst = insts
        self.__cycle = cycle
            
        for line in data:
            word = int(line,2)
            self.__data.append(word)
    
    def cpu(self, cpu):
        self.__cpu = cpu
        
    def servecycle(self):
        return self.__serve_cycle
        
    def getCycle(self):
        return self.__cycle
    
    def getLookupTable(self):
        idict = {}
        for i in range(len(self.__inst)):
            line = self.__inst[i]
            idx = line.find(":")
            if idx != -1:
                label = line[:idx].strip()
                idict[label] = i*4
        return idict
    
    def fetch_inst_block(self, addr):
        if addr < 0x0 or addr >= 0x100:
            lib.error("Error: Runtime Error: Invalid instruction address")
        words = []
        addr = addr/4
        
        if addr >= len(self.__inst):
            return None
        
        for _ in range(4):
            if addr < len(self.__inst):
                words.append(self.__inst[addr])
            else:
                words.append(None)
            addr += 1
        return words
    
    def fetch_data_block(self, addr):
        if addr < 0x100:
            lib.error("Error: Runtime Error: Invalid instruction address")
        words = []
        addr = addr-0x100
        addr = addr/4
        
        if addr >= len(self.__inst):
            return None
        
        for _ in range(4):
            if addr < len(self.__data):
                words.append(self.__data[addr])
            else:
                words.append(None)
            addr += 1
        return words
    
    def writeBlock(self, words, addr):
        if addr < 0x100:
            lib.error("Error: Runtime Error: Invalid instruction address")
        addr = addr-0x100
        addr = addr/4
        for i in range(4):
            self.__data[addr] = words[i]
            addr += 1
    
    def serve(self, role):
        if role == -1:
            self.__serve_cycle = self.__cpu.cycle()
        self.__serve = role
    
    def getServe(self):
        return self.__serve
    
    def validinst(self,addr):
        return (addr/4)>=0 and (addr/4)<len(self.__inst)


class wb(function_unit):
    
    __dc = None
    __regfile = None
    
    def __init__(self, dc, reg):
        self._cycle = 1
        self._slot = slot()   
        self.__dc = dc
        self.__regfile = reg 
    
    def consume(self, inst):
        self._slot.addinst(inst)
        inst.markunready()
        self._remain = self._cycle
        
    def work(self):
        inst = self.getInst()
        if inst is not None:
            attrs = inst.getattrs()
            if attrs[3] is not None:
                if attrs[5] == "r":
                    self.__regfile.putword(attrs[3], inst.getimd())
                    self.__dc.unmarkr(attrs[3])
                elif attrs[5] == "f":
                    self.__dc.unmarkf(attrs[3])
            inst.markready()


class decoder(function_unit):
    
    __Rs = []
    __Fs = []
    __table = None
    __regfile = None
    
    def __init__(self, lookuptable, regfile):
        self._cycle = 1
        self._slot = slot() 
        self.__table = lookuptable
        self.__regfile = regfile
        
        for _ in range(32):
            self.__Rs.append(None)  
            self.__Fs.append(None) 
    
    def unmarkr(self, idx):
        self.__Rs[idx] = None
    
    def unmarkf(self, idx):
        self.__Fs[idx] = None
    
    def decode(self, inst):
        if inst is not None:
            self._slot.addinst(inst)
            inst_s = inst.getInst()
            idx = inst_s.find(":")
            if idx != -1:
                inst_s = inst_s[idx+1:]
            inst_s = inst_s.strip()
            idx = inst_s.find(" ")
            itype = inst_s
            if idx > 0:
                itype = inst_s[0:idx]
                    
            # decode the instruction
            if itype=="dadd" or itype=="dsub" or itype=="and" or itype=="or":
                components = inst_s[idx:]
                components = components.split(",")
                if len(components) != 3:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                    
                for i in range(len(components)):
                    components[i] = components[i].strip()
                    if components[i][0] != 'r' or int(components[i][1:]) < 0 or int(components[i][1:]) >31:
                        lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                rd = int(components[0][1:])
                rs = int(components[1][1:])
                rt = int(components[2][1:])
                inst.setattrs(itype, rs, rt, rd, None, 'r')
            
            elif itype=="daddi" or itype=="dsubi" or itype=="andi" or itype=="ori":
                components = inst_s[idx:]
                components = components.split(",")
                if len(components) != 3:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                    
                for i in range(len(components)-1):
                    components[i] = components[i].strip()
                    if components[i][0] != 'r' or int(components[i][1:]) < 0 or int(components[i][1:]) >31:
                        lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                rd = int(components[0][1:])
                rs = int(components[1][1:])
                try:
                    imd = int(components[2])
                except:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                inst.setattrs(itype, rs, None, rd, imd, 'r')
            
            elif itype=="add.d" or itype=="div.d" or itype=="sub.d" or itype=="mul.d":
                components = inst_s[idx:]
                components = components.split(",")
                if len(components) != 3:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                    
                for i in range(len(components)):
                    components[i] = components[i].strip()
                    if components[i][0] != 'f' or int(components[i][1:]) < 0 or int(components[i][1:]) >31:
                        lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                rd = int(components[0][1:])
                rs = int(components[1][1:])
                rt = int(components[2][1:])
                inst.setattrs(itype, rs, rt, rd, None, 'f')
            
            elif itype=="lw":
                components = inst_s[idx:]
                components = components.split(",")
               
                if len(components) != 2:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                
                for i in range(len(components)):
                    components[i] = components[i].strip()
                
                if components[0][0] != "r" or int(components[0][1:]) < 0 or int(components[0][1:]) >31:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                
                try:
                    idx = components[1].find("(")                
                    imd = int(components[1][:idx])
                    coms = components[1][idx:][1:-1]
                    if coms[0] != "r" or int(coms[1:]) < 0 or int(coms[1:]) > 31:
                        lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                    inst.setattrs(itype, int(coms[1:]), None, int(components[0][1:]), imd , 'r')
                except:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
            
            elif itype=="sw":
                components = inst_s[idx:]
                components = components.split(",")
                if len(components) != 2:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                
                for i in range(len(components)):
                    components[i] = components[i].strip()
                
                if components[0][0] != "r" or int(components[0][1:]) < 0 or int(components[0][1:]) >31:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                
                try:
                    idx = components[1].find("(")
                    imd = int(components[1][:idx])
                    coms = components[1][idx:][1:-1]
                    if coms[0] != "r" or int(coms[1:]) < 0 or int(coms[1:]) > 31:
                        lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                    inst.setattrs(itype, int(coms[1:]), int(components[0][1:]), None, imd , 'r')
                except:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
            elif itype=="l.d":
                components = inst_s[idx:]
                components = components.split(",")
                if len(components) != 2:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                
                for i in range(len(components)):
                    components[i] = components[i].strip()
                
                if components[0][0] != "f" or int(components[0][1:]) < 0 or int(components[0][1:]) >31:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                
                try:
                    idx = components[1].find("(")
                    imd = int(components[1][:idx])
                    coms = components[1][idx:][1:-1]
                    if coms[0] != "r" or int(coms[1:]) < 0 or int(coms[1:]) > 31:
                        lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                    inst.setattrs(itype, int(coms[1:]), None, int(components[0][1:]), imd , 'f')
                except:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")  
            elif itype=="s.d":
                components = inst_s[idx:]
                components = components.split(",")
                if len(components) != 2:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                
                for i in range(len(components)):
                    components[i] = components[i].strip()
                
                if components[0][0] != "f" or int(components[0][1:]) < 0 or int(components[0][1:]) >31:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                
                try:
                    idx = components[1].find("(")
                    imd = int(components[1][:idx])
                    coms = components[1][idx:][1:-1]
                    if coms[0] != "r" or int(coms[1:]) < 0 or int(coms[1:]) > 31:
                        lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                    inst.setattrs(itype, int(coms[1:]), int(components[0][1:]), None, imd , 'f')
                except:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")  
            
            elif itype=="bne" or itype=="beq":
                components = inst_s[idx:]
                components = components.split(",")
                if len(components) != 3:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                    
                for i in range(len(components)-1):
                    components[i] = components[i].strip()
                    if components[i][0] != 'r' or int(components[i][1:]) < 0 or int(components[i][1:]) >31:
                        lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                rs = int(components[0][1:])
                rt = int(components[1][1:])
                try:
                    imd = self.__table[components[2]]
                except:
                    lib.error("Error: Invalid instruction: missing label [Line "+str(inst.getLine())+"]")
                inst.setattrs(itype, rs, rt, None, imd, 'j')      
            
            elif itype=="j":
                components = inst_s[idx:].strip()
                try:
                    imd = self.__table[components]
                except:
                    lib.error("Error: Invalid instruction [Line "+str(inst.getLine())+"]")
                inst.setattrs(itype, None, None, None, imd, 'j')
            
            elif itype =="hlt":
                inst.setattrs(itype, None, None, None, None, 'h')
            
            else:
                lib.error("Error: Unknown instruction [Line "+str(inst.getLine())+"]")
            
            inst.setdecoded()
            inst.markunready()
        
        # check WAW hazard
        if not self._slot.empty():
            inst = self._slot.getinst()
            if not inst.WAWchecked():
                attrs = inst.getattrs()
                if attrs[5] == 'r':
                    if attrs[3] is not None:
                        if self.__Rs[attrs[3]] == None:
                            self.__Rs[attrs[3]] = inst
                            inst.setWAW()
                        else:
                            inst.WAW()
                    else:
                        inst.setWAW()
                elif attrs[5] == "f":
                    if attrs[3] is not None:
                        if self.__Fs[attrs[3]] == None:
                            self.__Fs[attrs[3]] = inst
                            inst.setWAW()
                        else:
                            inst.WAW()
                    else:
                        inst.setWAW()
                else:
                    inst.setWAW()
        
        # check RAW hazard
        if not self._slot.empty():
            inst = self._slot.getinst()
            attrs = inst.getattrs()
            if attrs[5] == "r":
                allset = True
                # read rs
                if attrs[1] is not None:
                    # RAW hazard
                    if self.__Rs[attrs[1]] is not None and self.__Rs[attrs[1]] != inst:
                        allset = False
                    else:
                        inst.setrs(self.__regfile.getword(attrs[1]))
                
                if attrs[2] is not None:         
                    # RAW hazard
                    if self.__Rs[attrs[2]] is not None and self.__Rs[attrs[2]] != inst:
                        allset = False
                    else:
                        inst.setrt(self.__regfile.getword(attrs[2]))
                
                if allset:
                    inst.setRAW()
                else:
                    inst.RAW()
                    
            elif attrs[5] == "f":
                if attrs[0] == "l.d":
                    allset = True
                    # read rs
                    if attrs[1] is not None:
                        # RAW hazard
                        if self.__Rs[attrs[1]] is not None and self.__Rs[attrs[1]] != inst:
                            allset = False
                        else:
                            inst.setrs(self.__regfile.getword(attrs[1]))
                    
                    if allset:
                        inst.setRAW()
                    else:
                        inst.RAW()
                        
                elif attrs[0] == "s.d":
                    allset = True
                    # read rs
                    if attrs[1] is not None:
                        # RAW hazard
                        if self.__Rs[attrs[1]] is not None and self.__Rs[attrs[1]] != inst:
                            allset = False
                        else:
                            inst.setrs(self.__regfile.getword(attrs[1]))
                
                    if attrs[2] is not None:
                        # RAW hazard
                        if self.__Fs[attrs[2]] is not None and self.__Rs[attrs[2]] != inst:
                            allset = False
                        else:
                            inst.setrt(0)
                
                    if allset:
                        inst.setRAW()
                    else:
                        inst.RAW()
                        
                else:
                    allset = True
                    # read rs
                    if attrs[1] is not None:
                        # RAW hazard
                        if self.__Fs[attrs[1]] is not None and self.__Fs[attrs[1]] != inst:
                            allset = False
                        else:
                            inst.setrs(0)
                
                    if attrs[2] is not None:
                        # RAW hazard
                        if self.__Fs[attrs[2]] is not None and self.__Fs[attrs[2]] != inst:
                            allset = False
                        else:
                            inst.setrt(0)
                
                    if allset:
                        inst.setRAW()
                    else:
                        inst.RAW()
          
            elif attrs[5] == "j":
                itype = attrs[0]
                if itype=="bne" or itype=="beq":
                    allset = True
                    # read rs
                    if attrs[1] is not None:
                        # RAW hazard
                        if self.__Rs[attrs[1]] is not None and self.__Rs[attrs[1]] != inst:
                            allset = False
                        else:
                            inst.setrs(self.__regfile.getword(attrs[1]))
                
                    if attrs[2] is not None:
                        # RAW hazard
                        if self.__Rs[attrs[2]] is not None and self.__Rs[attrs[2]] != inst:
                            allset = False
                        else:
                            inst.setrt(self.__regfile.getword(attrs[2]))
                
                    if allset:
                        inst.setRAW()
                    else:
                        inst.RAW()
                else:
                    inst.setRAW()
            else:
                inst.setRAW()
       
        if not self._slot.empty():    
            inst = self._slot.getinst()
            if inst.decoded() and inst.WAWchecked() and inst.RAWchecked():
                inst.markready()


class integer_unit(function_unit):
    
    def __init__(self):
        self._cycle = 1
        self._slot = slot()
    pass

    def work(self):
        inst = self._slot.getinst()
        itype = inst.getattrs()[0]
        if itype == "lw" or itype=="sw" or itype=="l.d" or itype=="s.d":
            imd = inst.getrs()+inst.getimd()
            inst.setimd(imd)
        elif itype=="dadd":
            imd = inst.getrs()+inst.getrt()
            inst.setimd(imd)
        elif itype=="daddi":
            imd = inst.getrs()+inst.getimd()
            inst.setimd(imd)
        elif itype=="dsub":
            imd = inst.getrs()-inst.getrt()
            inst.setimd(imd)
        elif itype=="dsubi":
            imd = inst.getrs()-inst.getimd()
            inst.setimd(imd)
        elif itype=="and":
            imd = inst.getrs() & inst.getrt()
            inst.setimd(imd)
        elif itype=="andi":
            imd = inst.getrs() & inst.getimd()
            inst.setimd(imd)
        elif itype=="or":
            imd = inst.getrs() | inst.getrt()
            inst.setimd(imd)
        elif itype=="ori":
            imd = inst.getrs() | inst.getimd()
            inst.setimd(imd)
       
        self._remain -= 1
        if self._remain == 0:
            inst.markready()
        pass

    def consume(self, inst):
        inst.markunready()
        self._slot.addinst(inst)
        self._remain = self._cycle
        self.work()

    def available(self):
        return self._slot.empty()


class fetcher(function_unit):
    def __init__(self):
        self._cycle = 1
        self._slot = slot()
    
    def fetch(self, icache, PC):
        insts = icache.request(PC)
        if insts is None:
            self._slot.addinst(None)
        else:
            inst = libinst.instruction(insts)
            inst.setPC(PC)
            inst.markready()
            self._slot.addinst(inst)