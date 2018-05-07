#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import smtplib
import socket
import getpass
from email.mime.text import MIMEText
import subprocess
import clangformat
import statistics
import xcodetemplate
import base64

def decodestr(s):
    return base64.decodestring(s)
    pass


# mail_to_list=[decodestr('aW9zLXRlYW1ANTZxcS5jb20=')]
# mail_to_list=[decodestr('aW9zLXRlYW1ANTZxcS5jb20=')]
to_cc = [decodestr('c2h1YWlwZW5nLndhbmdANTZxcS5jb20=')]

mail_host=decodestr("bWFpbC5odW9jaGViYW5nLmNvbQ==")
mail_sender_name=decodestr("Z2l0aG9va3MuaW9zQGh1b2NoZWJhbmcuY29t")
mail_sender_pwd=decodestr("Y2h1dGgtNz83dmVwaGFKZXJl")

# mail_host="smtp.163.com"
# mail_sender_name="wsp810@163.com"
# mail_sender_pwd="abc666888"


def send_mail_for_content(content=""):
        
    to_self = check_out_put("git config --global jira.user", False, None)
    if not to_self:
        print "未检测到JIRA用户名,邮件列表中无法包含自己"
        to_self = decodestr('c2h1YWlwZW5nLndhbmdANTZxcS5jb20=')
        pass
    to_list = list(set([to_self,decodestr('c2h1YWlwZW5nLndhbmdANTZxcS5jb20=')]))
    
    content = content+config_content()+statistics.data_collect()
    mail_title = user_name()+" (githooks脚本更新成功)"
    mail_content = user_name()+":"+content
    success = send_mail(to_list,mail_title,mail_content)
    return success
    pass

#失败次数告警
def send_mail_for_fail(count="0",fail_type="",traceback=""):
        
    to_self = check_out_put("git config --global jira.user", False, None)
    if not to_self:
        print "未检测到JIRA用户名,邮件列表中无法包含自己"
        to_self = decodestr('c2h1YWlwZW5nLndhbmdANTZxcS5jb20=')
        pass
    to_list = list(set([to_self,decodestr('c2h1YWlwZW5nLndhbmdANTZxcS5jb20=')]))

    content = fail_type+"("+"当前失败次数为第"+count+"次)\n"+"最后一次失败回溯:\n"+traceback
    mail_title = user_name()+" (githooks脚本更新失败)"
    version = "当前版本:"+current_version()+"\n"
    global_version = "模板版本:"+current_global_version()+"\n"
    mail_content = version+user_name()+":"+content
    success = send_mail(to_list,mail_title,mail_content)
    return success
    pass

#填充jira失败的邮件
def send_mail_for_fail_jira(traceback):
    if not traceback:
        return
        pass
    
    to_self = check_out_put("git config --global jira.user", False, None)
    if not to_self:
        print "未检测到JIRA用户名,邮件列表中无法包含自己"
        to_self = decodestr('c2h1YWlwZW5nLndhbmdANTZxcS5jb20=')
        pass
    to_list = list(set([to_self,decodestr('c2h1YWlwZW5nLndhbmdANTZxcS5jb20=')]))
    mail_title = "githooks填充JIRA失败,请手动填充JIRA注释"
    success = send_mail(to_list,mail_title,traceback)
    return success
    pass

def send_mail(to_list,title,content,cc_list=to_cc):

    me = "githooks-service"+"<"+mail_sender_name+">"
    msg = MIMEText(content,'plain', 'utf-8')
    msg['Subject'] = title
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    msg['Cc'] = ';'.join(cc_list)
    print "正在发送通知邮件"
    # print me,to_list,msg.as_string()
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_sender_name,mail_sender_pwd)    
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        print "通知邮件已经发送成功。"
        return True
    except Exception, e:
        print "通知邮件发送失败。"
        print e
        return False

def config_content():
    
    project = "\n\n"+"仓库路径: "+os.getcwd()+"\n\n"

    xcode_template = "1.xcode统一模板:"+xcode_template_state()+"\n"
    sameimg = "2.iOS项目检查同名图片: "+sameimg_state()+"\n"
    checkmsg = "3.commitMsg规范性检查: "+checkmsg_state()+"\n"
    premsg = "4.拼接版本号/分支到提交信息: "+premsg_state()+"\n"
    autoversion = "5.自动递增版本号: "+autoversion_state()+"\n"
    notejira = "6.填充注释到JIRA: "+notejira_state()+"\n"
    clangformat = "7.代码格式化: "+clang_format()+"\n"
    xcodetemplatev = "8."+xcode_template_version()

    return project+xcode_template+sameimg+checkmsg+premsg+autoversion+notejira+clangformat+xcodetemplatev

    pass

def xcode_template_version():
    return xcodetemplate.version_text()
    pass

def xcode_template_state():
    return check_out_put('git config  githooks.xcodetemplate', False, "YES")
    pass

def sameimg_state():
    return check_out_put('git config  githooks.sameimg', False, "YES")
    pass

def checkmsg_state():
    return check_out_put('git config  githooks.checkmsg', False, "YES")
    pass

def premsg_state():
    return check_out_put('git config  githooks.premsg', False, "YES")
    pass

def autoversion_state():
    return check_out_put('git config githooks.autoversion', False, "NO")
    pass

def notejira_state():
    return check_out_put('git config githooks.notejira', False, "YES")
    pass

def clang_format():
    return check_out_put('git config githooks.clangformat', False, "YES")
    pass

def current_version():
    return check_out_put('git config githooks.version', False, "0")
    pass

def current_global_version():
    return check_out_put('git config --global githooks.globalversion', False, "0")
    pass

def user_name():
    name = check_out_put('git config user.name', False, "")
    if not len(name):
        name = check_out_put('git config --global user.name', False, "未知名字")
        pass
    return name
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
    # send_mail_for_fail()
    send_mail_for_fail("测试")
    pass


if __name__ == '__main__':
    main()
    pass