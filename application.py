'''
Created on Apr 25, 2014

@author: hanggao
'''

import sys
import lib
import regfile
import func_unit
import cpu

def read_file(fpath):
    fp = open(fpath)
    return fp.readlines()

def preprocess(lines):
    nlines = []
    for line in lines:
        line = line.lower()
        while line[0]==' ' or line[0]=='\n' or line[0]=='\r' or line[0]=='\r\n':
            line = line[1:]
        while line[len(line)-1]==' ' or line[len(line)-1]=='\n' or line[len(line)-1]=='\r' or line[len(line)-1]=='\r\n':
            line = line[0:len(line)-1]
        nlines.append(line)
    return nlines

def compare(ele1, ele2):
    ("adder", True, cycle)
    if ele1[1] == True and ele2[1] == False:
        return 1
    elif ele1[1] == False and ele2[1] == True:
        return -1
    elif ele1[2] < ele2[2]:
        return 1
    elif ele1[2] > ele2[2]:
        return -1
    else:
        return 0

def sort(orderlist):
    for i in range(len(orderlist)-1):
        for j in range(i+1, len(orderlist)):
            if compare(orderlist[i], orderlist[j]) > 0:
                tmp = orderlist[i]
                orderlist[i] = orderlist[j]
                orderlist[j] = tmp
    return orderlist

def parse_config(configs):
    params = []
    for line in configs:
        l = []
        ma = line.split(':')
        if len(ma) > 1:
            map2 = ma[1].split(",")
            l.append(ma[0])
            l.append(map2)
        else:
            l.append(ma[0])
        params.append(l)
    return params

if __name__ == '__main__':
        
    if(len(sys.argv) != 5):
        lib.usage()
        
    inst_file = sys.argv[1]
    data_file = sys.argv[2]
    reg_file = sys.argv[3]
    config_file = sys.argv[4]
    
    insts = read_file(inst_file)
    data = read_file(data_file)
    regs = read_file(reg_file)
    configs = read_file(config_file)
    
    'preprocess raw data'
    insts = preprocess(insts)
    data = preprocess(data)
    regs = preprocess(regs)
    configs = preprocess(configs)
    
    'load data to memory'
    reg = regfile.regfile(regs)
    
    fp_adder = None
    fp_multiplier = None
    fp_divider = None
    icache = None
    dcache = None
    mem = None
    
    orderlist = []
    
    ' analyze the config file'
    params = parse_config(configs)
    for param in params:
        if param[0]=='fp adder':
            if len(param[1]) == 2:
                try:
                    cycle = int(param[1][0])
                    if cycle <= 0:
                        raise 
                    
                    if param[1][1]=='yes':
                        fp_adder = func_unit.fp_adder(cycle,True)
                        orderlist.append(("adder", True, cycle))
                    elif param[1][1]=='no':
                        fp_adder = func_unit.fp_adder(cycle,False)
                        orderlist.append(("adder", False, cycle))
                    else:
                        lib.error("Error: Invalid config file: invalid or missing attribute [Line "+str(params.index(param)+1)+"]")
                except:
                    lib.error("Error: Invalid config file: invalid cycle number [Line "+str(params.index(param)+1)+"]")
            else:
                lib.error("Error: Invalid config file: invalid number of attributes [Line "+str(params.index(param)+1)+"]")
        elif param[0]=='fp multiplier':
            if len(param[1]) == 2:
                try:
                    cycle = int(param[1][0])
                    if cycle <= 0:
                        raise 
                   
                    if param[1][1]=='yes':
                        fp_multiplier = func_unit.fp_multiplyer(cycle,True)
                        orderlist.append(("multiplier", True, cycle))
                    elif param[1][1]=='no':
                        fp_multiplier = func_unit.fp_multiplyer(cycle,False)
                        orderlist.append(("multiplier", False, cycle))
                    else:
                        lib.error("Error: Invalid config file: invalid or missing attribute [Line "+str(params.index(param)+1)+"]")
                except:
                    lib.error("Error: Invalid config file: invalid cycle number [Line "+str(params.index(param)+1)+"]")
            else:
                lib.error("Error: Invalid config file: invalid number of attributes [Line "+str(params.index(param)+1)+"]")
        elif param[0]=='fp divider':
            if len(param[1]) == 2:
                try:
                    cycle = int(param[1][0])
                    if cycle <= 0:
                        raise 

                    if param[1][1]=='yes':
                        fp_divider = func_unit.fp_divider(cycle,True)
                        orderlist.append(("divider", True, cycle))
                    elif param[1][1]=='no':
                        fp_divider = func_unit.fp_divider(cycle,False)
                        orderlist.append(("divider", False, cycle))
                    else:
                        lib.error("Error: Invalid config file: invalid or missing attribute [Line "+str(params.index(param)+1)+"]")
                except:
                    lib.error("Error: Invalid config file: invalid cycle number [Line "+str(params.index(param)+1)+"]")
            else:
                lib.error("Error: Invalid config file: invalid number of attributes [Line "+str(params.index(param)+1)+"]")
        elif param[0]=='main memory':
            try:
                cycle = int(param[1][0])
                mem = func_unit.memory(insts, data, cycle)
                orderlist.append(("mem", True, cycle))
            except:
                lib.error("Error: Invalid config file: invalid cycle number [Line "+str(params.index(param)+1)+"]")
        elif param[0]=='i-cache':
            try:
                cycle = int(param[1][0])
                icache = func_unit.icache(cycle, mem)
            except:
                lib.error("Error: Invalid config file: invalid cycle number [Line "+str(params.index(param)+1)+"]") 
        elif param[0]=='d-cache':
            try:
                cycle = int(param[1][0])
                dcache = func_unit.dcache(cycle, mem)
            except:
                lib.error("Error: Invalid config file: invalid cycle number [Line "+str(params.index(param)+1)+"]") 
        else:
            lib.error("Error: Invalid config file: unknown configuration [Line "+str(params.index(param)+1)+"]")  
        pass
    
    'check the function units'
    if fp_adder is None or fp_multiplier is None or fp_divider is None or mem is None or icache is None or dcache is None:
        lib.error("Error: Invalid config file: missing configuration")
    
    orderlist = sort(orderlist)
    cpu = cpu.cpu(fp_adder, fp_multiplier, fp_divider, icache, dcache, mem.getLookupTable(), orderlist, reg, mem)
    cpu.run()