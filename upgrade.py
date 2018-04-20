#!/usr/bin/env python
# coding=utf-8


import os
import sys
import re
import subprocess
import autoupdate
import hookshelp


GLOBAL_version = ""


#公开
def deal_argv(argv):

    for i in range(1, len(argv)):

        if i==1 and (argv[i] == "-h" or argv[i] == "--help"):
            hookshelp.log_help(False)
            exit(0)

        if i==1 and (argv[i] == "-v" or argv[i] == "--version"):
            print check_out_put("git config githooks.version", True, "未发现版本号")
            exit(0)
            pass

        if argv[i] == "-d":
            hookshelp.clear_current_repo_config()
            pass

        if argv[i] == "-a":
            hookshelp.clear_all_config()
            pass

        if  argv[i].find("-v=")==0:
            check_argv_version(argv[i][3:])            
            pass

        if  argv[i].find("--version=")==0:
            check_argv_version(argv[i][10:])
            pass
        pass
    pass

def check_argv_version(version_str):
    
    if not len(version_str):
        print "未输入版本号"
        return
        pass
        
    global GLOBAL_version
    GLOBAL_version = version_str
    pass

def main():
    print "执行强制更新,清空上次更新的时间"
    check_out_put("git config githooks.updateTime \"0\"", False, "")
    autoupdate.update_to_define_version(GLOBAL_version)
    print "强制更新执行完毕"
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

if __name__ == '__main__':

    deal_argv(sys.argv)
    
    main()

    pass


