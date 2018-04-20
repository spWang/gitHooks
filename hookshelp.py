#!/usr/bin/env python
# coding=utf-8

import os
import sys
import subprocess

#公开
def clear_all_config():
    print "  抹掉全局githooks配置"
    check_out_put("git config --global githooks.testabc 1", False, "")
    print check_out_put("git config --global --remove-section githooks", False, "抹除全局githooks所有配置失败")
    pass

def clear_current_repo_config():
    print "  抹掉当前仓库的githooks配置("+os.getcwd()+")"
    check_out_put("git config githooks.testabc 1", False, "")
    print check_out_put("git config --remove-section githooks", False, "抹除本仓库githooks所有配置失败")
    pass

def log_help(is_setup):
    print "帮助文档:"
    if not is_setup:
        print "   不加任何参数,则执行强制检查是否有新版本"
        pass
    print "-h --help 输出帮助文档"
    if is_setup:
        print "-d 抹掉setup.plist配置下的仓库的githooks配置"
        pass
    else:
        print "-d 抹掉当前仓库的githooks配置"
        pass    
    print "-a 抹掉全局的githoks配置"
    print "-v --version 输出当前仓库githooks的版本"
    print "-v=xxx --version=xxx 升级至指定的版本号(若指定到1.5.1之前的版本,则无法再使用此功能)"
    pass

#私有
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




