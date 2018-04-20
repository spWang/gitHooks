#!/usr/bin/python
# -*- coding: UTF-8 -*-

import subprocess
import os
import reviewboard
from util.colorlog import *

def format_files():
    
    if check_out_put("git config githooks.clangformat", False, "YES") == "NO":
        print "你未开启自动代码格式的功能,如需开启请执行git config githooks.clangformat \"YES\""
        return
        pass
    
    print "\n"
    
    if not clang_format_file_exist():
        print "未检测到.clang-format文件,无需开启格式化代码功能"
        return
    
    if not file_path_exist("/usr/local/bin/clang-format"):
        logstr = "已配置.clang-format文件,表明需要开启代码格式化功能,但无依赖库clang-format,因此你需要执行下面的命令:"+ "\nbrew update & brew upgrade\nbrew install clang-format"+"\n然后可以执行brew list看是否clang-format"
        logred(logstr)
        print "如不想开启代码格式化功能,请执行git config githooks.clangformat \"NO\""
        exit(-1)
        pass

    file_path = "/usr/bin/clang-format"
    if not file_path_exist(file_path):
        reviewboard.log_operation_not_permitted(file_path, "自动代码格式化", "git config githooks.clangformat \"NO\"")
        exit(-1)
        pass
    output = check_out_put("git diff-index --cached --name-only HEAD",False, "")
    
    if not len(output):
        return
        pass
    
    print "正在检查可格式化代码的文件"
    for file in output.split("\n"):
        format_codefile(file)
        pass
    print "格式化代码功能执行完成"
    pass

def format_codefile(file):
    if len(file) == 0:
        return
        pass
    
    suf = file.split(".")[-1]

    # if suf == "h" or suf == "m" or suf == "mm" or suf == "c":
    if suf == "h" and check_file_state_ok(file):
        print "格式化:"+file
        check_out_put("clang-format -i -style=file "+file,True,"")
        add_cammand = "git add "+file
        check_out_put(add_cammand, True, "")
        pass

    pass

def check_file_state_ok(file_path):
    result = check_out_put("git status -s "+file_path, False, "异常")
    if not len(result):
        print "无法获取文件被改变的状态:"+file_path
        return False
        pass

    if result[0] == "M" or result[0] == "A":
        return True
        pass
    return False
    pass

#send.py也用到这里
def clang_format_file_exist():
    clang_format_file = os.getcwd()+"/.clang-format"
    return file_path_exist(clang_format_file)
    pass

def file_path_exist(file):
    return os.path.exists(file) and os.path.isfile(file)
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

def hooks_path():
    currentPath = os.path.realpath(__file__);
    fileName = os.path.basename(__file__);
    return currentPath.replace(fileName,"");
    pass
