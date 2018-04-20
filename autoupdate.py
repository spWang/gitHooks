#!/usr/bin/env python
# coding=utf-8

import re  
import os
import sys
import json
import urllib
import subprocess
import time
import socket
import urllib2
import traceback
import zipfile
import shutil
import executelimit
import send
from util.colorlog import *

UPDATEDURATION_HOUR = 24 #每隔多少小时更新一次
TIMEOUT = 30
GITHOOKSURL = "https://api.github.com/repos/spWang/gitHooks/tags"
MAX_FALI_COUNT = 0 #检查和更新脚本失败时抛异常的最大次数,0不抛异常
MIN_ALARM_COUNT = 1 #失败报警的最小次数
MAX_CHECK_FAIL_ONE_DAY = 2 #检查失败时,每天最大次数,超过后当天不在检查
VERSIONNAMEKEY = "name"
ZIPBALLKEY = "zipball_url"
GITHOOK_ZIP_NAME = "gitHooks.zip"
CHANGE_LOG_NAME = "changelog.md"

GOLBAL_DOWNLOAD_URL = ""
GOLBAL_REMOTE_VERSION = ""
GOLBAL_LOCAL_VERSION = ""

GOLBAL_DEFINE_VERSION = ""


#更新至指定版本
def update_to_define_version(verson_str):
    global GOLBAL_DEFINE_VERSION
    GOLBAL_DEFINE_VERSION = verson_str
    
    if len(verson_str)>0:
        print "你指定了升级的版本为"+GOLBAL_DEFINE_VERSION
        logred("谨慎:指定版本功能仅从1.5.1之后开始支持,若切回之前版本,则无法再使用切换版本的功能,需要手动再初始化一次")
        pass

    update_if_need(force_update=True)
    
    pass

def update_if_need(force_update=False):
    
    #是否需要检查更新
    if not need_check_update(force_update):
        return
        pass
    
    #是否有新的代码
    if not have_new_code_for_check():
        return
        pass  

    #新代码是否下载成功
    if not download_new_code():
        return
        pass

    #解压和复制新代码文件到hooks文件夹下
    update_success = False
    if unzip_files():
        move_code_files()
        deal_success_events()
        update_success = True
        pass

    #检查并开启可执行权限
    executelimit.open_execute_limit()

    if update_success:
        #放于后边的原因是要复制已经获的可执行权限的文件
        copy_code_files_to_template()
        show_change_log()
        pass
    
    pass

#处理后事
def deal_success_events():
    if os.path.exists(unzip_path()):
        shutil.rmtree(unzip_path())
        pass
    
    update_check_update_time()
    update_version()
    send_mail()

    pass

def send_mail():
    content = "脚本更新成功(版本:" + GOLBAL_LOCAL_VERSION + "-->" + GOLBAL_REMOTE_VERSION +")"
    send.send_mail_for_content(content)
    pass

#将代码拷贝到模板路径
def copy_code_files_to_template():
    template_path = os.environ['HOME']+"/.git_template/"
    template_hooks_path = template_path+"hooks"
    
    if os.path.exists(template_hooks_path):
        shutil.rmtree(template_hooks_path)
        pass

    shutil.copytree(hooks_path(),template_hooks_path)

    pass

def unzip_path():
    return hooks_path().replace('.git/hooks/','.git/temp_hooks/')
    pass

def unzip_files():
    zipfile_path = hooks_path()+GITHOOK_ZIP_NAME

    isZipfile = zipfile.is_zipfile(zipfile_path)
    if isZipfile == False:
        print "文件不存在或者不是zip类型,无法解压"
        return False

    fz = zipfile.ZipFile(zipfile_path, 'r')
    
    unZipPath = unzip_path()
    if not os.path.exists(unZipPath):
        os.mkdir(unZipPath)
        pass
    
    for file in fz.namelist():
        fz.extract(file, unZipPath)    
    fz.close()
    return True

    pass

def move_code_files():
    unzip_fils_path = ""
    for file in os.listdir(unzip_path()):
        if "spWang" in file:
            unzip_fils_path = unzip_path()+file
            break
            pass
        pass
    
    down_hooks_path = unzip_path()+"hooks"
    os.rename(unzip_fils_path,down_hooks_path)
    new_hooks_path = hooks_path()
    if os.path.exists(new_hooks_path):
        shutil.rmtree(new_hooks_path)
        pass
    shutil.copytree(down_hooks_path,new_hooks_path)
    
    pass

def download_new_code():
    if not "http" in GOLBAL_DOWNLOAD_URL:
        return False
        pass

    print "代码下载中,请稍候..."
    zipfile_path = hooks_path()+GITHOOK_ZIP_NAME
    socket.setdefaulttimeout(TIMEOUT)
    # send_headers = {
    # 'Host' : 'codeload.github.com',
    # 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
    # 'Accept' : 'text/html,application/xhtml+xm…plication/xml;q=0.9,*/*;q=0.8',
    # 'Connection': 'keep-alive',
    # }

    try:
        #下载完的zip包有问题,不用这个
        # response = requests.get(GOLBAL_DOWNLOAD_URL,headers=send_headers)
        # with open(zipfile_path, 'wb') as f:
        #     f.write(response.content)
        #     f.flush()
        urllib.urlretrieve(GOLBAL_DOWNLOAD_URL, zipfile_path, download_progress)
        check_out_put("git config --unset githooks.downFailCount", False , None)
        print "下载完毕。"
        return True
        pass
    except Exception, e:
        fail_count = check_out_put('git config githooks.downFailCount', False, 0)
        current_fail_count = str(int(fail_count)+1)

        print "代码下载失败时,前%s次会中断提交并抛出异常,如有疑问,请联系脚本开发者" % MAX_FALI_COUNT
        print "这是第%s次下载失败。在下次commit时会重新检查并下载,以下是异常信息:" % current_fail_count

        fail_count_cammand = "git config githooks.downFailCount "+ current_fail_count
        check_out_put(fail_count_cammand, False , 1)
        traceback_str = traceback.format_exc()
        if int(current_fail_count) >= MIN_ALARM_COUNT:
            send.send_mail_for_fail(current_fail_count,"下载脚本失败",traceback_str)
            pass

        if int(fail_count) < MAX_FALI_COUNT:
            raise e
            pass

        print traceback_str
        return False

    pass

def download_progress(a,b,c):
    per = 100.0 * a * b / c
    if per < 0:
        return

    if per > 100 :
        per = 100.00
    print '%.2f%%' % per
    pass

def have_new_code_for_check():
    print "如果你开启了蓝灯,而发现迟迟不能更新脚本,请暂时关闭蓝灯,蓝灯可能和github冲突,在脚本更新完毕后再开启它"
    
    if len(GOLBAL_DEFINE_VERSION)>0:
        print "正在获取脚本所有版本信息,请稍后..."
    else:
        print "正在检查脚本是否有新版本,请稍候..."
        pass
    
    socket.setdefaulttimeout(TIMEOUT)
    send_headers = {
    'Host' : 'api.github.com',
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Connection': 'keep-alive',
    }

    req = urllib2.Request(GITHOOKSURL)

    try:
        response = urllib2.urlopen(req)
        have_new_code = deal_check_result(response)
        clear_check_fail_count()
        clear_last_check_fail_date()
        return have_new_code
        pass
    except Exception, e:
        fail_count = check_out_put('git config githooks.checkFailCount', False, 0)
        current_fail_count = str(int(fail_count)+1)

        print "检查更新失败时,前%s次会中断提交并抛出异常,如有疑问,请联系脚本开发者" % MAX_FALI_COUNT
        print "这是今天第%s次检查失败。在下次commit时会重新检查,以下是异常信息:" % current_fail_count

        fail_count_cammand = "git config githooks.checkFailCount "+ current_fail_count
        check_out_put(fail_count_cammand, False , 1)

        currentDate = time.strftime('%Y%m%d',time.localtime(time.time()))
        fail_date_cammand = "git config githooks.lastCheckFailDate "+currentDate
        check_out_put(fail_date_cammand, False , 1)

        traceback_str = traceback.format_exc()
        if int(current_fail_count) >= MIN_ALARM_COUNT:
            send.send_mail_for_fail(current_fail_count,"检查更新失败",traceback_str)
            pass
        

        if int(fail_count) < MAX_FALI_COUNT:
            raise e
            pass

        print traceback_str
        return False
    pass

def deal_check_result(response):
    gitHooksStr = response.read()
    hooksList = json.loads(gitHooksStr)
   
    if len(hooksList)<=0:
        print "未检查到远端脚本,无法更新"
        return False
        pass

    global GOLBAL_DOWNLOAD_URL
    global GOLBAL_REMOTE_VERSION
    global GOLBAL_LOCAL_VERSION
    
    GOLBAL_LOCAL_VERSION = check_out_put("git config githooks.version", False, "0")
    GOLBAL_REMOTE_VERSION = hooksList[0][VERSIONNAMEKEY].encode('unicode-escape')
    GOLBAL_DOWNLOAD_URL = hooksList[0][ZIPBALLKEY]

    #优先处理指定版本的升级
    if len(GOLBAL_DEFINE_VERSION)>0:
        return deal_define_version(hooksList)
        pass

    if GOLBAL_LOCAL_VERSION == "0":
        print "本地未检测到版本信息,需要更新脚本"
        return True
        pass

    if GOLBAL_LOCAL_VERSION != GOLBAL_REMOTE_VERSION:
        print "当前版本号为%s,最新版本为%s" % (GOLBAL_LOCAL_VERSION,GOLBAL_REMOTE_VERSION)
        print "版本不一致,需要更新脚本"
        return True
        pass

    print "本地和远端版本号一致,无脚本更新"
    update_check_update_time()
    return False
    pass

def deal_define_version(hooks_list):

    in_list = False    
    for index, hooks_info in enumerate(hooks_list):
        
        remote_version = hooks_info[VERSIONNAMEKEY].encode('unicode-escape')
        if remote_version == GOLBAL_DEFINE_VERSION:
            in_list = True
            GOLBAL_REMOTE_VERSION = hooks_list[index][VERSIONNAMEKEY].encode('unicode-escape')
            GOLBAL_DOWNLOAD_URL = hooks_list[index][ZIPBALLKEY]
            break

            pass
        pass

    if not in_list:
        print "远端版本号列表未发现你指定的版本!!!"
        print "请检查后重新输入"
        exit(-1)
        pass

    print "正在切换至版本"+GOLBAL_REMOTE_VERSION
    return True
    pass


#根据上次检查时间看是否需要检查更新
def need_check_update(force_update=False):

    last_update_time = check_out_put('git config githooks.updateTime', False, 0)
    if last_update_time == 0:
        print "未检测到上次脚本更新的时间,需要检查是否有新版本"
        return True
        pass
    currentTime = time.time()
    if not force_update:
        currentDate = time.strftime('%Y%m%d',time.localtime(currentTime))
        lastCheckFailDate = check_out_put('git config githooks.lastCheckFailDate', False, "19700101")

        #清空上次失败的次数
        if currentDate !=lastCheckFailDate:
            clear_check_fail_count()
            pass
        checkFailCount = int(check_out_put('git config githooks.checkFailCount', False, 0))
        if checkFailCount >= MAX_CHECK_FAIL_ONE_DAY and (currentDate ==lastCheckFailDate):
            print "今日失败次数:"+str(checkFailCount)
            print "当前已经达到当天最大检查失败的次数,今日不再检查更新;若需要强制检查,执行命令python .git/hooks/upgrade.py"
            return False
            pass
        pass


    currentHour = int(time.strftime('%H',time.localtime(currentTime)))

    if (currentHour<10 or currentHour>20) and not force_update:
        print "脚本仅在上午10点-晚上20点期间检查是否有新版本;若需要强制检查,执行命令python .git/hooks/upgrade.py"
        return  False
        pass

    duration = currentTime -float(last_update_time)
    if duration>UPDATEDURATION_HOUR*60*60:
        print "距离上次检查是否有新版本的时间已经大于%s小时,需要检查更新是否有新版本" % UPDATEDURATION_HOUR
        return True
    
    duration_diff = calculate_canupdate_duration(last_update_time,currentTime)
    print "脚本每隔%s小时检查更新一次,还差%s检查是否有新版本;若需要强制检查,执行命令python .git/hooks/upgrade.py" % (UPDATEDURATION_HOUR, duration_diff)
    return  False

    pass

def update_version():
    command = 'git config githooks.version ' + GOLBAL_REMOTE_VERSION
    check_out_put(command,False,None)
    print "当前版本%s已更新录入本地" % GOLBAL_REMOTE_VERSION
    pass

#清空上次检查失败的日期
def clear_last_check_fail_date():
    check_out_put("git config --unset githooks.lastCheckFailDate", False , None)
    pass
def clear_check_fail_count():
    check_out_put("git config --unset githooks.checkFailCount", False , None)
    pass

#更新检测时间
def update_check_update_time():
    currentTime = time.time()
    command = 'git config githooks.updateTime ' + str(currentTime)
    check_out_put(command,False,None)
    print "本次检测的时间已更新录入本地"
    pass

#打开更新说明
def show_change_log():
    if updatelog().find(GOLBAL_LOCAL_VERSION) != -1:
        print "┏"+"┳"*50+"┓\n"
        print updatelog()
        print "┗"+"┻"*50+"┛"
        pass
    print "更新完毕✅✅✅"
    pass

def updatelog():
    updateFile = hooks_path()+CHANGE_LOG_NAME
    
    if os.path.exists(updateFile) == False:
        return ""
    all_changelog = open(updateFile, 'r').read()
        
    if all_changelog.find(GOLBAL_LOCAL_VERSION) == -1:
        return ""
        pass

    change_log = all_changelog.split(GOLBAL_LOCAL_VERSION, 1)[0]
    if len(change_log)>0:
        return change_log
        pass

    return ""
    pass

#计算还差多久要更新
def calculate_canupdate_duration(last_update_time, currentTime):
    diff = float(last_update_time)+float(UPDATEDURATION_HOUR)*60*60 - currentTime
    if diff<=0:
        return "0秒"
        pass
    m, s = divmod(diff, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    duration_diff = ("%01d天%01d小时%01d分钟%01d秒" % (d, h, m, s))
    if d == 0:
        duration_diff = ("%01d小时%01d分钟%01d秒" % (h, m, s))
        pass
    if d == 0 and h == 0:
        duration_diff = ("%01d分钟%01d秒" % (m, s))
        pass

    if d == 0 and h == 0 and m == 0:
        duration_diff = ("%01d秒" % s)
        pass

    return duration_diff
    pass

#基础支撑方法
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

#项目/.git/hooks/
def hooks_path():
    currentPath = os.path.realpath(__file__);
    fileName = os.path.basename(__file__);
    hooksPath = currentPath.replace(fileName,"");
    return hooksPath
    pass

#项目/.git/
def dot_git_path():
    return hooks_path().replace("hooks/","")
    pass

def main():
    # ok = need_check_update(force_update=True)
    # if not ok:
    #     print "不检查更新"
    #     return
    #     pass
    # print "在检查更新,模拟失败"
    # fail_count = check_out_put('git config githooks.checkFailCount', False, 0)
    # current_fail_count = str(int(fail_count)+1)

    # print "检查更新失败时,前%s次会中断提交并抛出异常,如有疑问,请联系脚本开发者" % MAX_FALI_COUNT
    # print "这是今天第%s次检查失败。在下次commit时会重新检查,以下是异常信息:" % current_fail_count

    # fail_count_cammand = "git config githooks.checkFailCount "+ current_fail_count
    # check_out_put(fail_count_cammand, False , 1)

    # currentDate = time.strftime('%Y%m%d',time.localtime(time.time()))
    # fail_date_cammand = "git config githooks.lastCheckFailDate "+currentDate
    # check_out_put(fail_date_cammand, False , 1)
    pass
if __name__ == '__main__':
    main()

