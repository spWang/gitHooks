#!/usr/bin/env python
# coding=utf-8

import subprocess
import os
import shutil
import filecmp

TEMPLATE_VERSION = 2

new_default_file_path = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/Library/Xcode/Templates/File Templates/Source"
new_file_category_path = "/Applications/Xcode.app/Contents/Developer/Library/Xcode/Templates/File Templates/Source/Objective-C File.xctemplate"
template_file = os.path.expanduser('~')+"/.git_template/hooks/xcodetemplate"
template_version_cammand = "git config --global githooks.templateversion"

def move_template_if_need():

    if not template_version_can_move():
        remove_template_dir()
        return
        pass

    default_name = "/Cocoa Touch Class.xctemplate"
    old_default_path = template_file+default_name
    new_default_path = new_default_file_path+default_name
    deal_file_access_if_need(path=new_default_file_path)
    move_template(old_file_path=old_default_path,new_file_path=new_default_path,write_version=False)

    category_name = "/CategoryNSObject"
    old_category_path = template_file+category_name
    new_category_path = new_file_category_path+category_name
    deal_file_access_if_need(path=new_file_category_path)
    move_template(old_file_path=old_category_path,new_file_path=new_category_path,write_version=True)

    remove_template_dir()
    pass

def version_text():
    template_version = check_out_put(template_version_cammand, False, "无")
    xcode_exist = "NO"
    xcode_app = "/Applications/Xcode.app"
    if os.path.exists(xcode_app):
        xcode_exist = "YES"
        pass
    return "check xcode exist:"+xcode_exist+"  template version:"+template_version
    pass

def move_template(old_file_path,new_file_path,write_version):
    if not os.path.exists(old_file_path) or not os.path.exists(new_file_path):
        return
        pass

    if os.access(new_file_path,os.R_OK | os.W_OK | os.X_OK):
        # print "已经有权限,准备开始复制模板"
        shutil.rmtree(new_file_path)
        shutil.copytree(old_file_path,new_file_path)
        if write_version:
            write_template_version()
            pass
    else:
        print "💎💎💎提交被中断,原因是:xcode模板路径无写权限,无法复制xcode模板"
        print "请打开终端,并cd到当前仓库下,然后执行下边命令\ngit commit -m \"test\"\n此命令会在终端模式下执行脚本,复制写入xcode模板,执行完毕后再尝试你的提交💎💎💎"
        exit(-1)
        pass      
    pass

def remove_template_dir():
    path = savePath()+"xcodetemplate"
    if os.path.exists(path):
        shutil.rmtree(path)
        pass

    pass

def template_version_can_move():
    #开启此功能,才移动
    if check_out_put("git config githooks.xcodetemplate", False, "YES") == "NO":
        print "未开启统一xcode模板功能,如需开启请执行git config githooks.xcodetemplate \"YES\""
        return False
        pass
    print "已开启统一xcode模板功能"

    #1.文件不同,需要复制过去
    file = "/Cocoa Touch Class.xctemplate/NSObjectObjective-C/___FILEBASENAME___.h"
    xcode_file = new_default_file_path+file
    xcode_template_file = template_file+file
    
    #1.1模板没有,不复制
    if not os.path.exists(xcode_template_file):
        print "脚本未提供xcode模板文件,无需复制xcode模板"
        return False
        pass
    
    #1.2未安装xcode,不复制
    xcode_app = "/Applications/Xcode.app"
    if not os.path.exists(xcode_app):
        print "未安装xcode,不需要复制xcode模板"
        return False
        pass

    #1.3xcode文件没有,复制
    if not os.path.exists(xcode_file):
        print "你的xcode没有模板文件,正在帮你复制模板..."
        return True
        pass
        
    #2.内容不同,复制
    equale = filecmp.cmp(xcode_file,xcode_template_file)
    if not equale:
        print "你的xcode的模板和提供的模板不一致,正在帮你复制模板..."
        return True        
        pass

    #3.内容相同,看标记版本
    template_version = check_out_put(template_version_cammand, False, None)
    if not template_version or int(template_version)<TEMPLATE_VERSION:
        print "xcode模板已更新,正在帮你复制模板..."
        return True
        pass
    print "xcode模板一致,不需要复制模板"
    return False
    pass
def write_template_version():
    cammand = template_version_cammand+ ' ' +str(TEMPLATE_VERSION)
    check_out_put(cammand, True, "")
    print "xcode模板复制成功"
    pass

#项目/.git/hooks/
def savePath():
    currentPath = os.path.realpath(__file__);
    fileName = os.path.basename(__file__);
    hooksPath = currentPath.replace(fileName,"");
    return hooksPath
    pass

def deal_file_access_if_need(path):
    path = path.replace(' ','\ ')
    if not os.access(path, os.R_OK | os.W_OK | os.X_OK):
        # print "XCode模板路径无可写权限,需要临时使用root权限"
        cammand = "sudo chown -R $(whoami) "+path
        check_out_put(cammand, False, None)
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


def main():
    pass


if __name__ == '__main__':
    main()
    pass