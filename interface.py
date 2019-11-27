# coding=utf-8
import check
import process
import os
import glob

class Interface:
    c = None
    p = None
    __fileNames = []

    def __init__(self):
        self.p = process.Process()
        # 读取目录下的xml文件
        curPath = os.path.dirname(os.path.abspath(__file__))
        xmlFiles = glob.glob(curPath + "/*.xml")
        self.c = check.Check(xmlFiles)
        for xmlFile in xmlFiles:
            xmlFile = os.path.basename(xmlFile)
            self.__fileNames.append(xmlFile)
        #print(self.__fileNames)

    def loop(self):
        # 检查xml文件
        if not self.c.runCheck():
            print("xml files not right")
            return
        
        # 选择xml文件
        while(1):
            self.printMenu()
            num = raw_input("Please enter a number: ")
            if num == 'q':
                break
            try:
                num = int(num)
            except ValueError:
                print("Not a number")
                continue
            if num >= 1 and num <= len(self.__fileNames):
                # 处理xml文件
                self.p.processXml(self.__fileNames[num - 1])
                print("Process finish")
            else:
                print("Invalid number")
        print("Bye")

    def printMenu(self):
        print("-----Menu-----")
        for i, name in enumerate(self.__fileNames):
            print("%2d: %s"%(i + 1, name))
        print("(Enter 'q' to quit)")
