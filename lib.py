import sys

def error(msg):
    print msg
    sys.exit(0)
    
def usage():
    print "Usage: simulator libinst.txt data.txt reg.txt config.txt result.txt"
    sys.exit()