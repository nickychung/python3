# encoding: utf-8
import os

def main():
   # print "hello world"
    a = 3
    fileName = 'test.txt'
    print (os.getcwd())
    os.get_terminal_size()
    screenWidth = os.get_terminal_size().columns
    openedFile = FileOpen(fileName)
    if(openedFile!=0):
        for line in openedFile:
            print(line)
        openedFile.close()
    return 0

def FileOpen(fileToOpen):
    try:
        f = open(fileToOpen,mode='r')
        print("Read OK")
        return f
    except FileNotFoundError:
        print("Read Fail")
        return 0
