"""
Created on Apr 25, 2014

@author: hanggao
"""

import func_unit


class cpu(object):
    __fp_adder = None
    __fp_multiplier = None
    __fp_divider = None
    __icache = None
    __dcache = None
    __iu = None
    __wb = None
    __dc = None
    __ft = None
    __lookuptable = None
    __orderlist = None
    __regfile = None
    __mem = None
    _clock = None

    def __init__(self, fp_adder, fp_multiplier, fp_divider, icache, dcache, lookuptable, orderlist, reg, mem):
        self.__fp_adder = fp_adder
        self.__fp_multiplier = fp_multiplier
        self.__fp_divider = fp_divider
        self.__icache = icache
        self.__dcache = dcache
        self.__regfile = reg
        self.__dc = func_unit.decoder(lookuptable, reg)
        self.__wb = func_unit.wb(self.__dc, reg)
        self.__ft = func_unit.fetcher()
        self.__lookuptable = lookuptable
        self.__orderlist = orderlist
        self.__iu = func_unit.integer_unit()
        self.__mem = mem
        self.__mem.cpu(self)
        self.__icache.cpu(self)
    
    def sort(self, printqueue):
        for i in range(len(printqueue)-1):
            for j in range(i+1, len(printqueue)):
                if printqueue[i].getissue() > printqueue[j].getissue():
                    tmp = printqueue[i]
                    printqueue[i] = printqueue[j]
                    printqueue[j] = tmp
                
                if printqueue[i].getissue() is None:
                    tmp = printqueue[i]
                    printqueue[i] = printqueue[j]
                    printqueue[j] = tmp
                    
                if printqueue[i].getfetch() > printqueue[j].getfetch():
                    tmp = printqueue[i]
                    printqueue[i] = printqueue[j]
                    printqueue[j] = tmp
        return printqueue
    
    def cycle(self):
        return self._clock
    
    def run(self):
        clock = 0
        PC = 0
        inst = None
        stop = 0
        stall = False
        branched = False
        printqueue = []
        last_branched = False
        
        while True:
            clock +=1
            self._clock = clock
            
            if (not self.__icache.cache_hit(PC)) and self.__mem.getServe() != 2 and self.__mem.validinst(PC):
                self.__icache.occupymem()
            
            NPC = PC+4

        # start of printer
            if not self.__wb.empty():
                if self.__wb.getInst().isready():
                    inst = self.__wb.getInst()
                    inst.setWBcycle(clock-1)
                    self.__wb.clear()
                    printqueue.append(inst)
        
            inst = None

        # start of WB stage
            readylist = []
            if (not self.__dcache.empty()) and self.__dcache.getInst().isready():
                readylist.append((self.__dcache, "mem"))
            
            if (not self.__fp_adder.empty()) and self.__fp_adder.getInst().isready():
                readylist.append((self.__fp_adder, "adder"))
            
            if (not self.__fp_multiplier.empty()) and self.__fp_multiplier.getInst().isready():
                readylist.append((self.__fp_multiplier, "multiplier"))
            
            if (not self.__fp_divider.empty()) and self.__fp_divider.getInst().isready():
                readylist.append((self.__fp_divider, "divider"))
            
            div = None
            orderitem = None
            order = 10
            for ele in readylist:
                for item in self.__orderlist:
                    if item[0] == ele[1]:
                        idx = self.__orderlist.index(item)
                        if idx < order:
                            div = ele[0]
                            orderitem = ele
                            order = idx
            
            if div is not None:
                alter = []
                for item in self.__orderlist:
                    if item != orderitem:
                        if item[1] == orderitem[1] and item[2] == orderitem[2]:
                            alter.append(item)

                for ele in alter:
                    mdiv = None
                    if ele[0] == "mem":
                        mdiv = self.__mem
                    elif ele[0] == "adder":
                        mdiv = self.__fp_adder
                    elif ele[0] == "multiplier":
                        mdiv = self.__fp_multiplier
                    elif ele[0] == "divider":
                        mdiv = self.__fp_divider
                    
                    if mdiv is not None and mdiv != div:
                        if mdiv.getInst().getissue() < div.getInst().getissue():
                            div = mdiv
        
            for ele in readylist:
                if ele[0] != div:
                    ele[0].getInst().STRUCT()
            
            if div is not None:
                inst =  div.clear()
                inst.setEXcycle(clock-1)
                self.__wb.consume(inst)
                self.__wb.work()
        # end of WB stage
        
            inst = None

        # start of EX stage
            self.__fp_adder.run()
            self.__fp_multiplier.run()
            self.__fp_divider.run()
            
            # memory
            if self.__dcache.empty():
               
                if (not self.__iu.empty()) and self.__iu.getInst().isready():
                    self.__dcache.consume(self.__iu.clear())
                    self.__dcache.work()
                    pass
            else:
                # memory is occupied
                self.__dcache.work()
                if (not self.__iu.empty()) and self.__iu.getInst().isready():
                    self.__iu.getInst().STRUCT()
                    pass
            
            # start of the first slot
            # get the content of decoder
            if not self.__dc.empty():
                inst = self.__dc.getInst()
                if inst.isready():
                    itype = inst.getattrs()[0]
                    if itype=="add.d" or itype=="sub.d":
                        if self.__fp_adder.available():
                            self.__fp_adder.consume(inst)
                            self.__dc.clear()
                            inst.setIDcycle(clock-1)
                        else:
                            inst.STRUCT()
                    elif itype=="mul.d":
                        if self.__fp_multiplier.available():
                            self.__fp_multiplier.consume(inst)
                            self.__dc.clear()
                            inst.setIDcycle(clock-1)
                            pass
                        else:
                            inst.STRUCT()
                    elif itype=="div.d":
                        if self.__fp_divider.available():
                            self.__fp_divider.consume(inst)
                            self.__dc.clear()
                            inst.setIDcycle(clock-1)
                            pass
                        else:
                            inst.STRUCT()
                    elif itype=="beq" or itype=="bne" or itype=="hlt" or itype=="j":
                        pass
                    else:
                        if self.__iu.available():
                            self.__iu.consume(inst)
                            self.__dc.clear()
                            inst.setIDcycle(clock-1)
                            pass
                        else:
                            inst.STRUCT()
        # end of EX stage    
            
        # start of ID stage
            # stall has to set
            if not self.__dc.empty():
                stall = True
            else:
                stall = False
            
            inst = None
            
            dPC = 0
            # if not stalled and IF is ready, decode next instruction
            if (not self.__ft.empty()) and self.__ft.getInst().isready() and not stall:
                inst = self.__ft.getInst()
                if inst is not None:
                    self.__ft.clear()
                    inst.setIFcycle(clock-1)
                    dPC = inst.getPC()
                    if not last_branched:
                        if self.__ft.empty():
                            if PC != dPC+4:
                                PC = dPC+4
                    
                    if stop > 0:
                        inst.setIDcycle(None)
                        printqueue.append(inst)
                        inst = None                
           
            # if inst is a new instruction, decode it; otherwise, decode the old one
            self.__dc.decode(inst)
           
            # check if the instruction is a branch instruction and is ready
            inst = self.__dc.getInst()
            if inst is not None and inst.isready():    
                itype = inst.getattrs()[0]
                if itype == "beq":
                    if inst.getrs() == inst.getrt():
                        NPC = inst.getimd()
                        branched = True
                    self.__dc.clear()
                    inst.setIDcycle(clock)
                    printqueue.append(inst)
                    stall = False
                elif itype == "bne":
                    if inst.getrs() != inst.getrt():
                        NPC = inst.getimd()
                        branched = True
                    self.__dc.clear()
                    inst.setIDcycle(clock)
                    printqueue.append(inst)
                    stall = False
                elif itype == "j":
                    NPC = inst.getimd()
                    branched = True
                    self.__dc.clear()
                    inst.setIDcycle(clock)
                    printqueue.append(inst)
                    stall = False
                elif itype == "hlt":
                    stop = 1
                    self.__dc.clear()
                    inst.setIDcycle(clock)
                    printqueue.append(inst)
                    if inst.getPC() != PC-4:
                        PC = inst.getPC()+4
                    stall = False
        # end of ID stage      

        # start of IF stage    
            if stop < 2 or self.__mem.getServe() > 0:        
                if self.__ft.empty():
                    self.__ft.fetch(self.__icache, PC)
                   
                    if branched and not self.__ft.empty():
                        inst = self.__ft.clear()
                        inst.setIFcycle(clock)
                        inst.setIDcycle(None)
                        printqueue.append(inst)
                        pass
                
                elif branched:
                    # flush
                    inst = self.__ft.clear()
                    inst.setIFcycle(clock)
                    inst.setIDcycle(None)
                    printqueue.append(inst)
                    pass
                else:
                    NPC = PC
        # end of IF stage
           
            if stop == 1:
                stop += 1
           
            # stalled or icache miss or nothing to fetch
            if (self.__ft.empty() and not branched) or stall:
                NPC = PC
            PC = NPC

            last_branched = branched
            branched = False
    
            if stop > 0 and self.__ft.empty() and self.__mem.getServe()<1 and self.__dc.empty() and self.__iu.empty() and self.__dcache.empty() and self.__fp_adder.free() and self.__fp_multiplier.free() and self.__fp_divider.free() and self.__wb.empty():
                break
           
            if clock>100:
                break;
        printqueue = self.sort(printqueue)
        
        s = "instruction"
        while len(s)<30:
            s += " "
        s += "\tIF\t\tID\t\tEX\t\tWB\t\tRAW\t\tWAR\t\tWAW\t\tStruct"
        print s
        
        for i in printqueue:
            print i.to_string()
            
        print 
        print "Total number of requests to instruction cache ", self.__icache.numreq()
        print "Total number of instruction cache hit ",self.__icache.numhit()
        print "Total number of requests to data cache ", self.__dcache.numreq()
        print "Total number of data cache hit ", self.__dcache.numhit()
