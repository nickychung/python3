# encoding: utf-8
import os

def main():
   # print "hello world"
    a = 3
    print (os.getcwd())
    os.get_terminal_size()
    screenWidth = os.get_terminal_size().columns
    print ("a".center(screenWidth))
    return 0

main()
