#!/usr/bin/env python
# coding=utf-8

import os
import re
import sys
import subprocess
import shutil
import executelimit
import hookshelp
from util.colorlog import *
from biplist import *

reload(sys)  
sys.setdefaultencoding('utf8')


TEMPLATE_FILE = ".git_template"+os.path.sep
CONFIG_FILE = "setup.plist"
GIT_FILE = ".git"
PRE_COMMIT_FILE = "pre-commit"

GLOBAL_clear_repo_config = False
GLOBAL_all_repo_paths = []

def main():
    
    #检查依赖库是否安装及自动安装
    check_dependent_balls()

    #检查用户名和密码
    check_require_config()

    #创建模板文件夹
    template_path = create_template_dir()
    
    #开启当前文件夹下文件的可执行权限
    executelimit.open_execute_limit()

    #拷贝当前文件夹下所有文件到模板文件夹
    copy_code_files_to_template(template_path)

    #配置全局的git模板文件路径
    config_global_git()

    #获取桌面上所有的仓库路径
    get_all_repo_paths()

    #所有仓库执行命令
    setup_all_projects(GLOBAL_all_repo_paths)

    pass

def check_dependent_balls():
    print "  正在检查依赖库是否安装"
    pip_list = check_out_put("pip list --format=legacy", False, None)
    
    #异常情况则不检查
    if len(pip_list)>0 and ("pip" not in pip_list):
        return
        pass

    if not pip_list:
        logred("  未安装pip,请参考gitHub页面里常见问题一栏pip的安装方案来安装pip")
        exit(-1)
        pass
    if not "jira" in pip_list:
        print "  正在安装jira..."
        check_out_put("pip install jira --user", False, None)
        pass
    
    #安装后重新检测一次
    pip_list = check_out_put("pip list --format=legacy", False, None)
    result = True

    if not "jira" in pip_list:
        print "  请手动安装jira"
        result = False
        pass

    if not result:
        exit(-1)
        pass
    pass

def check_require_config():
    print "  正在检查必要的配置项"
    config_path = current_path()+CONFIG_FILE
    
    if not (os.path.exists(config_path) and os.path.isfile(config_path)):
        log = "  未知原因导致配置文件"+config_path+"不存在,请联系开发者"
        logred(log)
        exit(-1)
        pass

    if not check_file_is_plsit(config_path):
        log = "  未知原因导致配置文件"+config_path+"不是plist文件,无法读取,请联系开发者"
        logred(log)
        exit(-1)
        pass

    result = True
    jira_name = read_plist_for_key(config_path, "jira_name", False, "")
    if not len(jira_name):
        jira_name = check_out_put("git config --global jira.user", False, "")
        print "  检测到已配置JIRA用户名"+jira_name
        pass
    if not len(jira_name):
        logred("  未配置JIRA用户名")
        result = False
        pass

    jira_pwd = read_plist_for_key(config_path, "jira_pwd", False, "")
    if not len(jira_pwd):
        jira_pwd = check_out_put("git config --global jira.pwd", False, "")
        print "  检测到已配置JIRA密码"+jira_pwd
        pass
    if not len(jira_name):
        logred("  未配置JIRA密码")
        result = False
        pass

    check_out_put("git config --global jira.user "+jira_name, False, None)
    check_out_put("git config --global jira.pwd "+jira_pwd, False, None)

    if not result:
        logred("请在当前目录下找到"+CONFIG_FILE+"完善上述配置项后重新执行当前命令")
        exit(-1)
        pass
    pass

def create_template_dir():
    rootdir = os.environ['HOME']
    template_path = rootdir+os.path.sep+TEMPLATE_FILE
    
    if os.path.exists(template_path):
        print "  发现旧的模板路径存在,正在删除旧目录"
        deal_file_access(template_path)
        shutil.rmtree(template_path)
        pass

    if not os.path.exists(template_path):
        print "  正在初始化模板目录"
        os.makedirs(template_path)
        pass
    
    return template_path

    pass

def copy_code_files_to_template(template_path):
    print "  正在复制代码到模板目录"
    new_path = template_path+"hooks"+os.path.sep
    shutil.copytree(current_path(),new_path)
    pass

def config_global_git():
    print "  正在配置全局的git初始化模板"
    check_out_put("git config --global init.templatedir ~/.git_template", True, "")
    pass

def get_all_repo_paths():
    print "  正在获取当前用户所有可配置的仓库路径,可能耗时较长,请耐心等待.."
    user_path = os.path.expanduser('~')
    global GLOBAL_all_repo_paths
    search_repo_path(user_path)
    print "  所有仓库路径获取完毕"
    pass

def search_repo_path(path):
    #不存在
    if not os.path.exists(path):
        return
        pass
    #不是文件夹
    if not os.path.isdir(path):
        return
        pass
    #没有可读可写权限
    if not os.access(path, os.R_OK | os.W_OK | os.X_OK):
        return
        pass
    file_name = os.path.basename(path)
    #隐藏文件夹
    if  file_name.startswith('.'):
        return
        pass
    #特殊文件名
    if  file_name.startswith('com.'):
        return
        pass
    #特殊目录
    especial_files = [
    'Library/Application Scripts',
    'Library/Application Support', 
    'Library/Assistant',
    'Library/Assistants',
    'Library/Audio',
    'Library/Caches',
    'Library/Calendars',
    'Library/CallServices',
    'Library/Colors',
    'Library/Containers',
    'Library/Cookies',
    'Library/Developer',
    'Library/Dictionaries',
    'Library/CoreData',
    'Library/GameKit',
    'Library/Gas Mask',
    'Library/Group Containers',
    'Library/iMovie',
    'Library/iTunes',
    'Library/Keychains',
    'Library/LanguageModeling',
    'Library/Logs',
    'Library/LanguageModeling',
    'Library/Mail',
    'Library/Maps',
    'Library/Messages',
    'Library/Metadata',
    'Library/MobileDevice',
    'Library/openvpn',
    'Library/Passes',
    'Library/Personas',
    'Library/Preferences',
    'Library/PubSub',
    'Library/Python',
    'Library/Safari',
    'Library/SafariSafeBrowsing',
    'Library/sapi',
    'Library/Saved Application State',
    'Library/Suggestions',
    'Library/WebKit',
    'Library/WechatPrivate',
    ]
    for especial_file in especial_files:
        especial_path = os.path.join(os.path.expanduser("~"), especial_file)
        if path == especial_path:
            return
            pass
        pass
    
    #目录下有.git目录即认为找到了目标
    project_git_path = path+os.path.sep+GIT_FILE
    if os.path.exists(project_git_path) and os.path.isdir(project_git_path):
        print "  检索到仓库:"+path
        GLOBAL_all_repo_paths.append(path)
        pass

    for file in os.listdir(path): 
        file_path = os.path.join(path, file)
        if os.path.exists(file_path) and os.path.isdir(file_path):
            search_repo_path(file_path)
            pass
        pass
        
    pass

def check_project_can_setup(project_path):
    result = True
    if not(os.path.exists(project_path) and os.path.isdir(project_path)):
        logred("  "+project_path+" ->初始化失败,原因:路径不存在或者不是文件夹")
        result = False
        pass
    else:
        project_git_path = project_path+os.path.sep+GIT_FILE
        if not(os.path.exists(project_git_path) and os.path.isdir(project_git_path)):
            logred("  " + project_path + " ->初始化失败,原因:路径下必须为.git的上级目录")
            result = False
            pass
    return result
    pass

def setup_all_projects(project_paths):
    print "  正在初始化仓库,请稍候..."
    for project_path in project_paths:
        if not len(project_path):
            continue
            pass

        if not check_project_can_setup(project_path):
            continue
            pass
        
        hooks_path = project_path+os.path.sep+GIT_FILE+os.path.sep+"hooks"
        if os.path.exists(hooks_path):
            # print "  发现旧hooks存在,正在删除旧目录"
            deal_file_access(hooks_path)
            shutil.rmtree(hooks_path)
            pass
        
        os.chdir(project_path)
        setup = "git init"
        check_out_put(setup, True, None)
        if GLOBAL_clear_repo_config:
            hookshelp.clear_current_repo_config()
            pass

        success = check_setup_success(hooks_path)
        if success:
            loggreen("  "+project_path+" ->初始化完成")
            pass
        else:
            logred("  "+project_path+" ->初始化失败")
        pass
    pass

def check_setup_success(hooks_path):
    pre_commit = hooks_path+os.path.sep+PRE_COMMIT_FILE
    if os.path.exists(pre_commit) and os.path.isfile(pre_commit):
        if os.access(pre_commit,os.X_OK):
            return True
            pass
        pass

    return False
    pass

#处理参数
def deal_argv(argv):
    for i in range(1, len(argv)):
        
        if argv[i] == "-d":
            global GLOBAL_clear_repo_config
            GLOBAL_clear_repo_config = True
            pass

        if argv[i] == "-a":
            hookshelp.clear_all_config()
            pass

        if i==1 and (argv[i] == "-h" or argv[i] == "--help"):
            hookshelp.log_help(True)
            exit(0)
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

def current_path():
    currentPath = os.path.realpath(__file__);
    fileName = os.path.basename(__file__);
    return currentPath.replace(fileName,"");
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
def deal_file_access(path):
    if not os.access(path, os.R_OK | os.W_OK):
        cammand = "sudo chown -R $(whoami) "+path
        check_out_put(cammand, False, None)
        pass
    pass

#入口
if __name__ == '__main__':
    deal_argv(sys.argv)

    logblue("开始初始化配置...")
    
    main()
    
    logblue("所有步骤执行完毕, 如有遗留问题,请根据日志输出检查;")
    
    pass