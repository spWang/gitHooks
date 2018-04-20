#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import subprocess

def open_execute_limit():
    check_file_access("pre-applypatch")
    check_file_access("applypatch-msg")

    check_file_access("pre-commit")
    check_file_access("prepare-commit-msg")
    check_file_access("commit-msg")
    check_file_access("post-commit")

    check_file_access("pre-push")
    check_file_access("update")
    check_file_access("post-update")

    check_file_access("pre-rebase")
    check_file_access("pre-receive")

    pass

def check_file_access(file_name):
    file_path = hooks_path()+file_name
    file_access = os.access(file_path,os.X_OK)
    
    if os.path.exists(file_path) and file_access == False:
        cammand = "chmod +x "+file_name
        subprocess.Popen(cammand,shell=True,cwd=hooks_path())
        print  file_name+"可执行权限未开启,已重新开启"
    pass
    pass

def hooks_path():
    currentPath = os.path.realpath(__file__);
    fileName = os.path.basename(__file__);
    return currentPath.replace(fileName,"");
    pass
