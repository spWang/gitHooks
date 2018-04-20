#!/usr/bin/env python
# coding=utf-8

from biplist import *
import os
import subprocess
from util.colorlog import *

#货主PLIST_PATH="/Consignor4ios/Supporting Files/Consignor4ios-Info.plist"
#司机PLIST_PATH="/NewDriver4iOS/NewDriver4iOS/Info.plist"

VERSION_KEY = "CFBundleShortVersionString"
BUILD_VERSON_KEY = "CFBundleVersion"
HOOKS_PATH = ".git/hooks"
PROJECT_SUF = ".xcodeproj"
PLIST_SUF = ".plist"


#公开
def add_version_if_need():
    if open_fun() == "YES":
        print "已开启自动递增build版本号的功能"
        change_plist_verson(True)
        pass
    else:
        print_log("未开启自动递增build版本号的功能,如需开启请执行:git config githooks.autoversion \"YES\"")
    pass

def reduce_version_if_need():
    if open_fun() == "YES":
        change_plist_verson(False)
        pass
    pass

def read_current_project_version():

    #需要在仓库里配置.plist_path文件,并填好对应的plist文件便可以拼接版本号
    
    config_path = get_project_path()+os.path.sep+".plist_path"
    if not(os.path.exists(config_path) and os.path.isfile(config_path)):
        return ""
        pass

    with open(config_path, 'r+') as f:
        relative_path = f.read()
    pass

    plist_path = get_project_path()+os.path.sep+relative_path
    
    if not check_file_is_plsit(plist_path):
        print plist_path+"不是plist文件"
        return ""
        pass

    current_version = read_plist_for_key(plist_path, VERSION_KEY, False, "")
    if len(current_version)>0:
        return "["+current_version+"]"
        pass
    return ""
    
    pass


def write_version(current_version,plist_path,add):
    if current_version == None:
        return

    las_dot_index = current_version.rfind('.')

    pre_version_str = current_version[0:las_dot_index+1]

    last_version_str = current_version[las_dot_index+1:len(current_version)]

    version = str(int(last_version_str)+1) if add else str(int(last_version_str)-1)

    write_version_str = pre_version_str+version

    plist_dic = readPlist(plist_path)

    plist_dic[BUILD_VERSON_KEY] = write_version_str

    writePlist(plist_dic,plist_path)
    
    if add:
        loggreen("已成功将版本号"+current_version+"改成为"+write_version_str)
        pass
    else:
        logred("已成功将版本号"+current_version+"回滚至"+write_version_str)    
    pass

def print_log(log):
    print log
    pass

def read_version(plist_path, can_raise):
    if not os.path.exists(plist_path):
        
        log = "路径%s找不到plist文件" % plist_path
        
        raise(IOError(log)) if can_raise else print_log(log)

        return None
    pass

    try:
        plist = readPlist(plist_path)
        try:
            version = plist[BUILD_VERSON_KEY]
            return version
        except(KeyError, Exception),e:
            log = plist_path+"文件里没有这个key:"+BUILD_VERSON_KEY
            raise(IOError(log)) if can_raise else print_log(log)
            return None

    except (InvalidPlistException, NotBinaryPlistException), e:
        log = "路径%s不是plist文件" % plist_path
        raise(IOError(log)) if can_raise else print_log(log)
        return None
    pass

def get_project_path():
    current_path = os.getcwd()
    if current_path.find(HOOKS_PATH):
        return current_path.replace(HOOKS_PATH,'')
    else:
        raise Exception("路径不在.git/hooks,请检查")
    pass

def plist_father_path():
    preject_path = get_project_path()
    for file in os.listdir(preject_path):
        if PROJECT_SUF in file:
            preject_path = preject_path+'/'+file.replace(PROJECT_SUF,'')
            break
        pass
    return preject_path+"/Supporting Files/"
    pass

def plist_paths(plist_father_path):
    plists = []
    if not os.path.isdir(plist_father_path):
        return plists
        pass

    for file in os.listdir(plist_father_path):

        if PLIST_SUF in file:
            plists.append(plist_father_path+file)
            pass
        pass

    return plists
    pass

def change_plist_verson(add):
    plist_exist = True
    current_version = ""
    plist_path_arr = plist_paths(plist_father_path())
    
    if len(plist_path_arr) == 0:
        plist_exist = False
        pass

    #先尝试去默认路径读取
    for plist_path in plist_path_arr:
        current_version = read_version(plist_path,False)
        if  current_version == None:
            plist_exist = False
            break
            pass
        else:
            write_version(current_version, plist_path, add)
        pass
    pass

    #如果读取不到再到配置的路径读取
    if not plist_exist:
        config_plist_paths = ""
        try:
            config_plist_paths = subprocess.check_output('git config  githooks.plistpaths', shell=True).strip()
            pass
        except subprocess.CalledProcessError as e:
            log = "默认路径没有plist文件,请在%s路径下配置plist的相对路径,如果有多个," % get_project_path()
            example = "请以逗号隔开,示例:git config githooks.plistpaths \"xxx/info.plist,ooo/info2.plist\""
            ex = log+example
            raise IOError(ex)
                
        config_plist_path_arr = config_plist_paths.split(',')
        #遍历的是相对路径
        for config_relative_plist_path in config_plist_path_arr:
           #绝对路径
            config_plist_path = get_project_path()+config_relative_plist_path

            current_version = read_version(config_plist_path,True)
            
            write_version(current_version, config_plist_path, add)
            pass

        pass
#公开
def open_fun():
    return check_out_put("git config githooks.autoversion", False, "NO")
    pass

def reset_autoversion_state():
    if check_out_put('git config githooks.autoversion', False ,"NO") == "YES":
        check_out_put('git config githooks.autoversion \"NO\"', False, "")
        pass
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

# 基础方法
def check_file_is_plsit(plist_path):
    try:
        plist = readPlist(plist_path)
        return True
    except (InvalidPlistException, NotBinaryPlistException), e:
        return False
    pass

# 此方法必须先验证是plist文件
def read_plist_for_key(plist_path, key, can_raise, return_value):
    plist = readPlist(plist_path)
    try:
        return plist[key]
    except(KeyError, Exception),e:
        return return_value
    pass


