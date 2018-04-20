#!/usr/bin/env python
# coding=utf-8

import sys
import os
import re
import subprocess
from util.colorlog import *

imgList = []

def open_fun():
    return check_out_put('git config githooks.sameimg', False ,"YES")
    pass

def reset_check_same_img_state():
    if check_out_put('git config githooks.sameimg', False ,"YES") == "NO":
        check_out_put('git config githooks.sameimg \"YES\"', False, "")
        pass
    pass

def check_out_put(cammand, can_raise, return_value):
    try:
        return subprocess.check_output(cammand, shell=True).strip()
        pass
    except subprocess.CalledProcessError as e:
        if can_raise:
            raise(e)
        else:
            return return_value
            pass
    pass

class CheckImgName(object):
    """检查相同图片名字"""


    #获取项目名字
    @classmethod
    def __getProjectName(self, projectPath):
    #列出目录下的所有文件和目录
        projectName = "a";

        #这是所有文件的名字
        files = os.listdir(projectPath)
        for fileName in files:

            workspace = ".xcworkspace";
            if workspace in fileName:
                #print "'%s'" % fileName;
                projectName = fileName.replace(workspace,"");
                break;
                pass

            xcodeproj = ".xcodeproj";
            if xcodeproj in fileName:
                #print "'%s'" % fileName;
                projectName = fileName.replace(xcodeproj,"");
                break;
                pass

        return projectName;
    @classmethod
    def __findImgFolder(self, pattern,directory):
        found =[]
        for (thisdir,subsHere,filesHere) in os.walk(directory):
            
            for file in filesHere + subsHere:
                if pattern in file:
                    found.append(os.path.join(thisdir,file))
                    break;
                    pass
                pass
            pass
        return found


    #是否有子文件
    @classmethod
    def __hasSubFolder(self, folderPath):
        files = os.listdir(folderPath)
        count = 0;
        for file in files:
            if file[0] != ".":
                count = count + 1;
                #print "%s" % file;
                pass
            pass
        pass
        if count == 0:
            return False;
        else: 
            return True;
            pass


    #检查是否有相同的图片
    @classmethod
    def __checkHasSameImg(self):
        listCount =  len(imgList);
        #print "项目里共有图片%d对" % listCount

        nameEqual = False;
        for i in range(listCount-1):
            for j in range(listCount-i-1):
                if imgList[i] == imgList[i+j+1]:
                    logstr = "你有相同名字的图片%s 请修改后再尝试提交" % imgList[i];
                    logred(logstr)
                    nameEqual = True;
                    pass
                pass
            pass
        pass
        return nameEqual;

    #把path下所有图片放入数组
    @classmethod
    def  __putImgInList(self, path):
        #print "Images.xcassets路经:%s\n" % path;
        #这是Images.xcassets内所有文件的名字
        files = os.listdir(path)
        
        for file in files:
            #跳过隐藏文件
            if file[0] == ".":
                continue;
                pass
            
            #文件的绝对路径
            filePath = path + "/" + file;
            
            #跳过文件
            if os.path.isfile(filePath):
                continue;
                pass

            #图片名字
            fileExtensionName = os.path.splitext(file)[1];
            if fileExtensionName == ".imageset":
                imgName = file.replace(".imageset","")
                imgList.append(imgName);
                pass
            
            #不是文件,递归
            if self.__hasSubFolder(filePath):
                self.__putImgInList(filePath);
                #print "有子文件夹 %s" % filePath;
                pass
            pass
    @classmethod
    def check_img_if_need(self):
        if open_fun() == "NO":
            print "未开启检查同名图片的功能,如需开启请执行git config githooks.sameimg \"YES\""
            return
            pass
        print "已开启检查同名图片的功能"

        #当前脚本所在的路径
        currentPath = os.path.realpath(__file__);

        #项目所在的路径
        currentFilePath = "/.git/hooks/" + os.path.basename(__file__);
        #print "当前文件相对路径:'%s'\n" % currentFilePath;

        projectPath = currentPath.replace(currentFilePath,"");

        projectPath = projectPath + "/"+ self.__getProjectName(projectPath)

        #print "您的项目路径:'%s'\n" % projectPath;

        #图片文件的路径
        fatherImgPath = projectPath
        foundList = self.__findImgFolder("Assets.xcassets",projectPath);

        if len(foundList) > 0:
            fatherImgPath = foundList[0]
            pass
        else:
            foundList = self.__findImgFolder("Images.xcassets",projectPath)
            if len(foundList) > 0:
                fatherImgPath = foundList[0]
                pass
        #判断图片路径文件夹是否存在
        if fatherImgPath == projectPath:
            # print "图片目录不存在,可提交";
            return
            pass

        else:
            self.__putImgInList(fatherImgPath);
            
            if self.__checkHasSameImg() == True:
                # print "有重名图片,不可提交"
                sys.exit(-1)
                pass
            else:
                # print "没有重复图片名字,可提交"
                return
            pass

        pass
        