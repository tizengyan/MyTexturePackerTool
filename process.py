# coding=utf-8
import xml.etree.ElementTree as ET
import os
import platform
import subprocess
import re
import plistlib
import glob

class Config:
    hasModifyType = False
    _type = "png"
    _type2 = "RGBA8888"
    scale = "1.0"

    packSingle = "0"
    originalName = "0"
    alphaRate = "0"
    rgbRate = "0"

    boderPadding = "2"
    shapePadding = "2"

    forceSquared = False
    combinPkm = False
    joinPkm = False  # 是否上下拼接

    etcPotNoAlphaReplace = False
    etcPotNoAlphaReplaceType = "jpg"

    sizeConstraints = "POT"
    maxSize = "2048"
    trimmode = ""
    pathAddition = ""


    def __init__(self, root):
        packAttrib = []
        for child in root.iter("pack"):
            packAttrib = child.attrib
            #print(packAttrib)

        if "etcPotNoAlphaReplace" in packAttrib:
            temp = packAttrib["etcPotNoAlphaReplace"]
            self.etcPotNoAlphaReplace = (temp != "0")

        if "type" in packAttrib:
            temp = packAttrib["type"]
            if temp == "jpg" or temp == "png" or temp == "webp" or temp == "pkm" or temp == "pvr" or temp == "pvr.ccz":
                self._type = temp
        
        if "type2" in packAttrib:
            temp = packAttrib["type2"]
            if temp == "RGBA8888" or temp == "BGRA8888" or temp == "RGBA4444" or temp == "RGB888" or temp == "RGB565" or temp == "RGBA5551" or temp == "RGBA5555" or temp == "PVRTC2" or temp == "PVRTC4" or temp == "PVRTC2_NOALPHA" or temp == "PVRTC4_NOALPHA" or temp == "ALPHA" or temp == "ALPHA_INTENSITY" or temp == "ETC1":
                self._type2 = temp

        if "scale" in packAttrib:
            self.scale = packAttrib["scale"]

        if "etcPotNoAlphaReplaceType" in packAttrib:
            temp = packAttrib["etcPotNoAlphaReplaceType"]
            if(temp == "jpg" or temp == "webp" or temp == "png" or temp == "pkm" or temp == "pvr" or temp == "pvr.ccz"):
                self.etcPotNoAlphaReplaceType = temp

        if "packSingle" in packAttrib:
            self.packSingle = packAttrib["packSingle"]

        if "originalName" in packAttrib:
            self.originalName = packAttrib["originalName"]
            
        if "maxSize" in packAttrib:
            self.maxSize = packAttrib["maxSize"]

        if "rgbRate" in packAttrib:
            self.rgbRate = packAttrib["rgbRate"]

        if "alphaRate" in packAttrib:
            self.alphaRate = packAttrib["alphaRate"]

        if "sizeConstraints" in packAttrib:
            self.sizeConstraints = packAttrib["sizeConstraints"]

        if "forceSquared" in packAttrib:
            self.forceSquared = (packAttrib["forceSquared"] != 0)
            
        if "boderPadding" in packAttrib:
            self.boderPadding = (packAttrib["boderPadding"] != 0)
            
        if "shapePadding" in packAttrib:
            self.shapePadding = (packAttrib["shapePadding"] != 0)

        if "joinPkm" in packAttrib:
            self.joinPkm = (packAttrib["joinPkm"] != 0)

        if "combinPkm" in packAttrib:
            self.combinPkm = (packAttrib["combinPkm"] != 0)

        if "trimmode" in packAttrib:
            temp = packAttrib["trimmode"]
            if temp == "None" or temp == "Trim" or temp == "Crop"or temp == "CropKeepPos":
                self.trimmode = temp

        if "pathAddition" in packAttrib:
            self.pathAddition = packAttrib["pathAddition"] + os.sep


class Process:
    imgType = "tga"
    currentDir = os.path.dirname(os.path.abspath(__file__))
    config = None

    def initConfig(self, root):
        self.config = Config(root)

    def processXml(self, fileName):
        print("Processing {}".format(fileName))

        # 读取xml，得到src和dest路径
        try:
            tree = ET.parse(self.currentDir + os.sep + fileName)
        except IOError:
            print("No such file")
            return
        
        root = tree.getroot()
        texturePackerPath = "\"" + root.attrib["cmdPath1"] + "\""
        if platform.system() == "Darwin":
            texturePackerPath = root.attrib["cmdPath2"]
        #print(texturePackerPath)

        self.initConfig(root)

        for pack in root.iter("pack"):
            packAttrib = pack.attrib
            #print(packAttrib)
            try:
                src = packAttrib["src"]
                dest = packAttrib["dest"]
            except:
                print("src/dest path not exist")
                return


            srcPath = "../../../" + src
            destPath = "../../../" + dest

            srcPath = self.currentDir + os.sep + srcPath
            destPath = self.currentDir + os.sep + destPath

            srcPath = os.path.abspath(srcPath)
            destPath = os.path.abspath(destPath)
            #print("Path: {0}, {1}".format(srcPath, destPath))

            if self.config.packSingle != "0":
                self.packSingleTexture(srcPath, destPath, texturePackerPath)
            else:
                self.packMultiple(srcPath, destPath, texturePackerPath)

    def packSingleTexture(self, srcPath, destPath, texturePackerPath):
        thisType = self.config._type
        thisType2 = self.config._type2
        
        if self.config._type == "pkm":
            if self.config.sizeConstraints == "POT" and self.config.etcPotNoAlphaReplace:
                self.config.hasModifyType = True
                thisType = self.config.etcPotNoAlphaReplaceType
                if thisType == "pvr" or thisType == "pvr.ccz":
                    thisType2 = "RGBA4444"

        #files = glob.glob(srcPath + "/*." + self.imgType)
        paramBase = texturePackerPath
        paramBase += " --format cocos2d-x"
        paramBase += " --allow-free-size"
        #paramBase += " --dither-fs-alpha"
        paramBase += " --pack-mode Best"
        paramBase += " --border-padding 0"
        paramBase += " --padding 0"
        paramBase += " --shape-padding 0"
        paramBase += " --scale " + self.config.scale
        paramBase += " --alpha-handling KeepTransparentPixels"

        for rt, dirs, files in os.walk(srcPath):
            if files and not dirs:
                for _file in files:

                    if thisType == "pkm":
                        outputName = _file.split(".")[0]
                        outputName = re.split(" |_", outputName)[0]

                        midPath = rt[len(srcPath): ]
                        #folderName = os.path.dirname(midPath)
                        folderName = os.path.basename(midPath)
                        folderName = re.split(" |_", folderName)[0]

                        tempDest = destPath + os.sep + folderName + os.sep + outputName
                        tempPlistDest = tempDest + ".plist"

                        hasAlpha = self.config.sizeConstraints == "POT" or self.config.forceSquared # 待处理

                        tempTextureType = "png"

                        tempPngPath = tempDest + "pngTemp." + tempTextureType
                        tempPngParam = paramBase
                        tempPngParam += " --size-constraints " + self.config.sizeConstraints
                        tempPngParam += " --max-size " + self.config.maxSize

                        if self.config.forceSquared:
                            tempPngParam += " --force-squared"
                        tempPngParam += " --trim-mode " + "Trim" if self.config.trimmode == "" else self.config.trimmode
                        tempPngParam += " --data " + tempPlistDest
                        tempPngParam += " --sheet " + tempPngPath
                        tempPngParam += " \"" + rt + "\""
                        self.callTP(tempPngParam)
                        
                        finalTexturePath = ""
                        if hasAlpha:
                            tempAlphaPngPath = tempDest + "pngTempAlpha." + tempTextureType
                            tempAlphaPngParam = paramBase
                            if self.config.forceSquared:
                                tempAlphaPngParam += " --force-squared"
                            tempAlphaPngParam += " --size-constraints " + self.config.sizeConstraints
                            tempAlphaPngParam += " --max-size " + self.config.maxSize
                            tempAlphaPngParam += " --trim-mode " + "Trim" if self.config.trimmode == "" else self.config.trimmode
                            tempAlphaPngParam += " --opt ALPHA"
                            tempAlphaPngParam += " --sheet " + tempAlphaPngPath
                            tempAlphaPngParam += " \"" + rt + "\""
                            self.callTP(tempAlphaPngParam)

                            plistConfig = plistlib.readPlist(tempPlistDest)
                            if "TextureWidth" in plistConfig:
                                imgWidth = plistConfig["TextureWidth"]
                            else:
                                print("---TextureWidth dosen't exist!")
                            if "TextureHeight" in plistConfig:
                                imgHeight = plistConfig["TextureHeight"]
                            else:
                                print("---TextureHeight dosen't exist!")
                            
                            canJoinTexture = False
                            if self.config.joinPkm:
                                if imgWidth > 0 and imgWidth <= 1024 and imgHeight > 0 and imgHeight <= 1024:
                                    canJoinTexture = True

                            if canJoinTexture:
                                tempJoinTexturePath = tempDest + "-joinTemp." + tempTextureType
                                rempJoinTexturePackerParam = paramBase
                                rempJoinTexturePackerParam += " --size-constraints AnySize"
                                rempJoinTexturePackerParam += " --disable-rotation"
                                rempJoinTexturePackerParam += " --trim-mode None"
                                rempJoinTexturePackerParam += " --width " + imgWidth
                                rempJoinTexturePackerParam += " --sheet " + tempJoinTexturePath
                                rempJoinTexturePackerParam += " " + tempPngPath + " " + tempAlphaPngPath
                                self.callTP(rempJoinTexturePackerParam)

                                rgbTexturePath = tempDest + "-a." + thisType
                                tempRgbTexturePackerParam = paramBase
                                tempRgbTexturePackerParam += " --size-constraints AnySize"
                                tempRgbTexturePackerParam += " --trim-mode None"
                                tempRgbTexturePackerParam += " --sheet " + rgbTexturePath
                                tempRgbTexturePackerParam += " " + tempJoinTexturePath
                                self.callTP(tempRgbTexturePackerParam)

                                if self.config.combinPkm:
                                    scaleValue = float(self.config.scale) * 10000
                                    self.packPkm(rgbTexturePath, "JOIN", scaleValue, 0)
                                    finalTexturePath = rgbTexturePath.replace("-a." + self.config._type, ".ab")
                                else:
                                    finalTexturePath = rgbTexturePath

                            else:
                                rgbTexturePath = tempDest + "-a." + thisType
                                tempRgbTexturePackerParam = paramBase
                                tempRgbTexturePackerParam += " --size-constraints AnySize"
                                tempRgbTexturePackerParam += " --trim-mode None"
                                tempRgbTexturePackerParam += " --sheet " + rgbTexturePath
                                tempRgbTexturePackerParam += " " + tempPngPath
                                self.callTP(tempRgbTexturePackerParam)

                                alphaPkmTexturePath = tempDest + "alpha." + thisType
                                alphaPkmTexturePackerParam = paramBase
                                alphaPkmTexturePackerParam += " --size-constraints AnySize"
                                alphaPkmTexturePackerParam += " --trim-mode None"
                                alphaPkmTexturePackerParam += " --sheet " + alphaPkmTexturePath
                                alphaPkmTexturePackerParam += " " + tempAlphaPngPath
                                self.callTP(alphaPkmTexturePackerParam)

                                if self.config.combinPkm:
                                    scaleValue = float(self.config.scale * 10000)
                                    self.packPkm(rgbTexturePath, alphaPkmTexturePath, scaleValue, 0)
                                    #RemoveFile(rgbTexturePath)
                                    #RemoveFile(alphaPkmTexturePath)

                                    finalTexturePath = rgbTexturePath.replace("-a." + self.config._type, ".ab")
                                else:
                                    finalTexturePath = rgbTexturePath

                        else:
                            tempRgbTexturePath = tempDest + "." + thisType
                            #RemoveFile(tempRgbTexturePath)
                            tempRgbTexturePackerParam = paramBase
                            tempRgbTexturePackerParam += " --size-constraints AnySize"
                            tempRgbTexturePackerParam += " --trim-mode " + "Trim" if self.config.trimmode == "" else self.config.trimmode
                            tempRgbTexturePackerParam += " --data " + tempPlistDest
                            tempRgbTexturePackerParam += " --sheet " + tempRgbTexturePath
                            tempRgbTexturePackerParam += " " + tempPngPath
                            self.callTP(tempRgbTexturePackerParam)

                            finalTexturePath = tempRgbTexturePath

                        newTextureFileName = os.path.basename(finalTexturePath)
                        newTextureFileName = newTextureFileName.split(" ")[0]
                        newTextureName = "<string>" + newTextureFileName + "</string>"

                        oldTextureFileName = os.path.basename(tempPngPath)
                        oldTextureFileName = oldTextureFileName.split(" ")[0]
                        oldTextureName = "<string>" + oldTextureFileName + "</string>"

                        self.replacePlistName(tempPlistDest, oldTextureName, newTextureName)
                    else:
                        params = paramBase
                        params += " --trim-mode " + "Trim" if self.config.trimmode == "" else self.config.trimmode

                        if not self.config.hasModifyType:
                            params += " --size-constraints " + self.config.sizeConstraints
                            params += " --max-size " + self.config.maxSize
                            if self.config.forceSquared:
                                params += " --force-squared"
                        else:
                            params += " --size-constraints AnySize"

                        if thisType == "jpg":
                            params += " --jpg-quality " + self.config.rgbRate
                        elif thisType == "pvr" or thisType == "pvr.ccz":
                            params += " --opt " + thisType2
                        
                        outputName = _file.split(".")[0]
                        outputName = re.split(" |_", outputName)[0]

                        midPath = rt[len(srcPath): ]
                        #folderName = os.path.dirname(midPath)
                        folderName = os.path.basename(midPath)
                        folderName = re.split(" |_", folderName)[0]

                        tempDest = destPath + os.sep + folderName + os.sep + outputName + "." + thisType
                        tempPlistDest = destPath + os.sep + folderName + os.sep + outputName + ".plist"
                        #print("tempDest: {}\ntempPlistDest: {}".format(tempDest, tempPlistDest))

                        params += " --sheet " + "\"" + tempDest + "\""
                        params += " --data " + "\"" + tempPlistDest + "\""

                        params += " \"" + rt + os.sep + _file + "\""

                        self.callTP(params)

                    #self.replacePlistFrameNameSingle(destPath, tempPlistDest, _file)
                    frameFileName = ""
                    frameName = _file.split(".")[0]
                    frameName = re.split(" |_", frameName)[0]
                    if (self.config.pathAddition.Length > 0):
                        frameFileName = "0000"
                    else:
                        frameFileName = frameName
                    newFrameName = "<key>" + srcPath + "/" + frameName + "/" + frameFileName + ".tga" + "</key>"
                    oldFrameName = "<key>" + _file + "</key>"
                    self.replacePlistName(tempPlistDest, oldFrameName, newFrameName)


    def packMultiple(self, srcPath, destPath, texturePackerPath):
        # 遍历目录下的文件
        for rt, dirs, files in os.walk(srcPath):
            # 只处理没有子目录的目录
            if files and not dirs:
                #print(rt, dirs, files)
                midPath = rt[len(srcPath): ] # 取中间路径，包含 /
                #print("1: {}".format(midPath))
                # 目标位置
                folderName = os.path.basename(rt)
                
                outputName = re.split(" |_", folderName)[0] # 以空格或下划线分割
                
                midPath = os.path.dirname(midPath) # 上层目录
                #print("2: {}".format(midPath))
                outputFolder = os.path.basename(midPath)
                
                outputFolder = re.split(" |_", outputFolder)[0]
                #print("outputFolder: {}".format(outputFolder))
                tempDest = destPath + os.sep + outputFolder + os.sep + outputName
                tempPlistDest = destPath + os.sep + outputFolder + os.sep + outputName + ".plist"

                textureFilePath = ""

                paramBase = texturePackerPath
                paramBase += " --format cocos2d-x"
                paramBase += " --allow-free-size"
                #paramBase += " --dither-fs-alpha"
                paramBase += " --pack-mode Best"
                paramBase += " --padding 0"
                paramBase += " --scale " + self.config.scale
                paramBase += " --alpha-handling KeepTransparentPixels"

                if self.config._type == "pkm" or self.config._type == "jpg":
                    params = paramBase
                    
                    params += " --size-constraints " + self.config.sizeConstraints
                    params += " --max-size " + self.config.maxSize

                    if self.config.forceSquared:
                        params += " --force-squared"
                    
                    params += " --trim-mode " + "Trim" if self.config.trimmode == "" else self.config.trimmode
                    params += " --border-padding " + self.config.boderPadding
                    params += " --shape-padding " + self.config.shapePadding
                    
                    texturePath = tempDest + ".png"
                    params += " --sheet " + "\"" + texturePath + "\"" # 路径有空格，需要加引号
                    params += " --data " + "\"" + tempPlistDest + "\""
                    params += " \"" + rt + "\""
                    self.callTP(params)

                    # alpha texture
                    alphaParams = paramBase
                    alphaParams += " --size-constraints AnySize"
                    alphaParams += " --border-padding 0"
                    alphaParams += " --shape-padding 0"
                    alphaParams += " --opt ALPHA"
                    alphaParams += " --trim-mode None"

                    alphaTexturePath = tempDest + "alpha.png"
                    alphaParams += " --sheet " + alphaTexturePath
                    alphaParams += " \"" + texturePath + "\""
                    self.callTP(alphaParams)

                    plistConfig = plistlib.readPlist(tempPlistDest)
                    if "TextureWidth" in plistConfig:
                        imgWidth = plistConfig["TextureWidth"]
                    else:
                        print("---TextureWidth dosen't exist!")
                    if "TextureHeight" in plistConfig:
                        imgHeight = plistConfig["TextureHeight"]
                    else:
                        print("---TextureHeight dosen't exist!")
                    finalTexturePath = ""
                    canJoinTexture = False
                    if self.config.joinPkm:
                        if imgWidth > 0 and imgWidth <= 1024 and imgHeight > 0 and imgHeight <= 1024:
                            canJoinTexture = True
                    
                    if canJoinTexture:
                        rempJoinTexturePath = tempDest + "-jointemp.png"
                        rempJoinParam = paramBase
                        rempJoinParam += " --size-constraints AnySize"
                        rempJoinParam += " --border-padding 0"
                        rempJoinParam += " --shape-padding 0"
                        rempJoinParam += " --disable-rotation"
                        rempJoinParam += " --trim-mode None"
                        rempJoinParam += " --width " + imgWidth
                        rempJoinParam += " --sheet " + rempJoinTexturePath
                        rempJoinParam += " \"" + texturePath + "\" \"" + alphaTexturePath + "\""
                        self.callTP(rempJoinParam)

                        rgbPkmTexturePath = tempDest + "-a." + self.config._type
                        rgbPkmParam = paramBase

                        if self.config._type == "jpg":
                            rgbPkmParam += " --jpg-quality " + self.config.rgbRate
                        
                        rgbPkmParam += " --size-constraints AnySize"
                        rgbPkmParam += " --border-padding 0"
                        rgbPkmParam += " --shape-padding 0"
                        rgbPkmParam += " --trim-mode None"
                        rgbPkmParam += " --sheet " + rgbPkmTexturePath
                        rgbPkmParam += " " + rempJoinTexturePath
                        self.callTP(rgbPkmParam)
                        
                        if self.config.combinPkm:
                            scaleValue = float(self.config.scale) * 10000
                            #self.packPkm(rgbPkmTexturePath, "JOIN", scaleValue, 0)

                            finalTexturePath = rgbPkmTexturePath.replace("-a." + self.config._type, ".ab")
                        else:
                            finalTexturePath = rgbPkmTexturePath
                    else:
                        rgbPkmTexturePath = tempDest + "-a." + self.config._type
                        rgbPkmParam = paramBase
                        if self.config._type == "jpg":
                            rgbPkmParam += " --jpg-quality " + self.config.rgbRate
                        rgbPkmParam += " --size-constraints AnySize"
                        rgbPkmParam += " --border-padding 0"
                        rgbPkmParam += " --shape-padding 0"
                        rgbPkmParam += " --trim-mode None"
                        rgbPkmParam += " --sheet " + rgbPkmTexturePath
                        rgbPkmParam += " " + texturePath
                        self.callTP(rgbPkmParam)
                        
                        alphaPkmTexturePath = tempDest + "alpha." + self.config._type
                        alphaPkmParam = paramBase
                        if self.config._type == "jpg":
                            alphaPkmParam += " --jpg-quality " + self.config.rgbRate
                        alphaPkmParam += " --size-constraints AnySize"
                        alphaPkmParam += " --border-padding 0"
                        alphaPkmParam += " --shape-padding 0"
                        alphaPkmParam += " --trim-mode None"
                        alphaPkmParam += " --sheet " + alphaPkmTexturePath
                        alphaPkmParam += " " + alphaTexturePath
                        self.callTP(alphaPkmParam)

                        if self.config.combinPkm:
                            scaleValue = float(self.config.scale) * 10000
                            self.packPkm(rgbPkmTexturePath, alphaPkmTexturePath, scaleValue, 0)

                            finalTexturePath = rgbPkmTexturePath.Replace("-a." + self.config._type, ".ab")
                        else:
                            finalTexturePath = rgbPkmTexturePath

                    newTextureFileName = os.path.basename(finalTexturePath)
                    newTextureFileName = newTextureFileName.split(" ")[0]
                    newTextureName = "<string>" + newTextureFileName + "</string>"

                    oldTextureFileName = os.path.basename(texturePath)
                    oldTextureFileName = oldTextureFileName.split(" ")[0]
                    oldTextureName = "<string>" + oldTextureFileName + "</string>"

                    self.replacePlistName(tempPlistDest, oldTextureName, newTextureName)

                    textureFilePath = newTextureFileName

                else:
                    params = paramBase
                    if self.config.forceSquared:
                        params += " --force-squared"
                    
                    params += " --border-padding " + self.config.boderPadding
                    params += " --shape-padding " + self.config.shapePadding
                    params += " --size-constraints " + self.config.sizeConstraints
                    params += " --max-size " + self.config.maxSize
                    params += " --trim-mode " + "Trim" if self.config.trimmode == "" else self.config.trimmode

                    if self.config._type == "pvr" or self.config._type == "pvr.ccz":
                        params += " --opt " + self.config._type2

                    tempDest += "." + self.config._type
                    params += " --sheet " + "\"" + tempDest + "\"" # 路径有空格，需要加引号
                    params += " --data " + "\"" + tempPlistDest + "\""
                    params += " \"" + rt + "\""

                    #print(params)
                    self.callTP(params)

                self.replacePlistFrameName(rt, destPath, tempPlistDest, files)
                # have join image?
                # split plist

    def replacePlistName(self, plistPath, oldContent, newContent):
        plist = plistlib.readPlist(plistPath)
        plist = plistlib.writePlistToString(plist) # 从plist读为string
        plist = plist.replace(oldContent, newContent) # 替换
        plist = plistlib.readPlistFromString(plist) # 从string读为plist
        plistlib.writePlist(plist, plistPath) # 写入

    def replacePlistFrameNameSingle(self, destPath, plistPath, tgaFile):
        plist = plistlib.readPlist(plistPath)
        plist = plistlib.writePlistToString(plist)

        plistName = os.path.basename(plistPath)
        plistName = plistName.split(".")[0]
        plistDir = os.path.dirname(plistPath)
        destPath = os.path.dirname(destPath)
        plistDir = plistDir[len(destPath) + 1: ]
        newName = plistDir + os.sep + plistName + os.sep + plistName + ".tga"
        plist = plist.replace(tgaFile, newName)

        plist = plistlib.readPlistFromString(plist)
        plistlib.writePlist(plist, plistPath)

    def replacePlistFrameName(self, filePath, destPath, plistPath, srcFiles):
        plist = plistlib.readPlist(plistPath)
        basePath = os.path.dirname(plistPath)
        destPath = os.path.dirname(destPath)
        folderName = os.path.basename(filePath)
        folderName = re.split(" |_", folderName)[0]

        plist = plistlib.writePlistToString(plist)
        for _file in srcFiles:
            l = re.split(" |_", _file)
            fileId = l[len(l) - 1]
            newName = basePath + os.sep + folderName + os.sep + fileId
            newName = newName[len(destPath) + 1: ]
            #newName = newName.replace("\\", os.sep)
            plist = plist.replace(_file, newName)
        plist = plistlib.readPlistFromString(plist)
        plistlib.writePlist(plist, plistPath)

        """
        nameDict = plist["frames"]
        basePath = os.path.dirname(plistPath)
        destPath = os.path.dirname(destPath)
        folderName = os.path.basename(filePath)
        folderName = re.split(" |_", folderName)[0]
        i = 0
        for k, _ in nameDict.items():
            l = re.split(" |_", srcFiles[i])
            i += 1
            newName = l[len(l) - 1]
            newKey = basePath + os.sep + folderName + os.sep + newName
            newKey = newKey[len(destPath) + 1: ]
            newKey = newKey.replace("\\", os.sep)
            nameDict[newKey] = nameDict.pop(k)
        plist["frames"] = nameDict
        plistlib.writePlist(plist, plistPath)
        """

    def callTP(self, param):
        try:
            if platform.system() == "Windows":
                subprocess.call(param)
            elif platform.system() == "Darwin":
                os.popen(param)
            else:
                print("OS not supported")
        except:
            print("Failed to run TexturePacker")

    def printDirContent(self, path):
        for rt, dirs, files in os.walk(path):
            path = rt.split(os.sep)
            print((len(path) - 1) * '--' + os.path.basename(rt))
            for file in files:
                print(len(path) * '--' + file)
        print("")

    def packPkm(self, rgbFullPath, combinType, scale, rgbOpt):
        pass

    def splitPlist(self):
        pass
#params = r"D:\\Projects\\tools\\test src\\src\\folder with space" # + " --sheet " + r"D:\\Projects\\tools\\out.png"
#texturePackerPath = "D:\\Program Files\\CodeAndWeb\\TexturePacker\\bin\\TexturePacker.exe"
#subprocess.call([texturePackerPath, params, "--sheet", "D:\\Projects\\output\\out.png"])