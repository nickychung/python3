# encoding: utf-8
import os

def main():
   # print "hello world"
    a = 3
    print (os.getcwd())
    os.get_terminal_size()
    screenWidth = os.get_terminal_size().columns
    screenHeight = os.get_terminal_size().lines
    for x in range(screenHeight-1):
        print ("Line:" + repr(x+1))
    print("Line:" + repr(x+2) + " <EOF>")
    return 0
main()
