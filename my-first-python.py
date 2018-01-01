# encoding: utf-8
import os

def main():
   # print "hello world"
    a = 3
    print (os.getcwd())
    os.get_terminal_size()
    screenWidth = os.get_terminal_size().columns
    openedFile = FileOpen()
    if(openedFile!=0):
        for line in openedFile:
            print(line)
    openedFile.close()
    return 0

def FileOpen():
    f = open('./test.txt',mode='w')
    if(f.readable):
        print("Read OK")
        return f
    else:
        print("Read Fail")
        return 0



main()
