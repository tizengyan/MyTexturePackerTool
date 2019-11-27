import os

class Check:
    __fileNames = []
    cwd = os.getcwd()

    def __init__(self, names):
        print(self.cwd)
        __fileNames = names

    def runCheck(self):
        for fileName in self.__fileNames:
            pass
        return True