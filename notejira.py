#!/usr/bin/env python
# coding=utf-8

import re
import os
import sys
import subprocess
import addpremsg
import statistics
import send
from jira import JIRA
from jira import JIRAError
from CommitMsgStyle import CheckMsgStyle
from util.colorlog import *
import base64

JIRA_SERVER_URL = 'aHR0cDovL2ppcmEuNTZxcS5jbi8='

GOLBAL_JIRA_ID = ""
GOLBAL_COMMIT_MSG = ""


'''公开方法'''
def note_jira_if_need(review_url):
    
  jira_state = check_out_put("git config githooks.notejira", False, "YES")
  if jira_state == "NO":
    print "未开启填充注释到jira的功能,如需开启请执行git config githooks.notejira \"YES\""
    return
    pass
  print "已开启填充注释到jira的功能"

  if not can_note_jira():
    return
    pass

  note_jira(review_url)

  pass

#重置状态
def reset_jira_state():

  if check_out_put('git config githooks.notejira', False ,"YES") == "NO":
      check_out_put('git config githooks.notejira \"YES\"', False, "")
      pass
  pass

'''私有方法'''
def can_note_jira():

  #1.检查最后一笔提交是不是本人
  local_user = check_out_put("git config user.name",False,"")
  global_local_user = check_out_put("git config --global user.name",False,"")
  last_commit_user = check_out_put("git log --format=%an -n 1",False,"None")
  if last_commit_user != global_local_user and last_commit_user != local_user:
    print "最后一笔提交不是你的,无法填充打jira注释"
    return False
    pass
  
  #2.检查是不是在没有commit的情况下执行了push
  result = check_out_put("git status",True,"")
  need_push = "use \"git push\" to publish your local commits"
  need_pull = "use \"git pull\" to merge the remote branch into yours"
  if not need_push in result and not need_pull in result:
    print "你当前没有什么可以push的东西,因此也不需要去填充jira"
    return False
    pass

  #3.填充过了就不需要填充jira了

  #4.未检查到jira号,不填充
  commit_message = check_out_put("git log --format=%B -n 1", False, "")
    
  left_bracket_location = commit_message.find("(")
  right_bracket_location = commit_message.find("):")

  if left_bracket_location == -1 or right_bracket_location == -1:
    print "未检测到关键字():"
    print "表示没有填写jira号,不填充jira注释"
    return False
    pass

  #5.从提交信息第一个字符到冒号之间,检查header类型是否匹配,以防止匹配到了后边的提交信息,导致JIRA号匹配错误
  add_text = addpremsg.get_add_text()
  header = commit_message[0:left_bracket_location].replace(add_text,"")
  issue_id = commit_message[left_bracket_location+1:right_bracket_location]
    
  if not header in CheckMsgStyle.headerTypesList():
    print "检测到的header是"+header
    print "header类型不在可选列表中,无法做JIRA号的匹配,不填充jira注释"
    return False
    pass

  #6.检查JIRA号是否存在
  if len(issue_id) == 0:
    print "你的jira_id为空,无法填充jira注释"
    return False
    pass

  #7.检查jira用户名
  if len(jira_user_name()) == 0 or len(jira_user_pwd()) == 0:
    print "你没有为JIRA配置用户名或密码,请按照如下命令格式分别配置用户名和密码"
    print "git config --global jira.user \"xxx@xx.com\""
    print "git config --global jira.pwd \"xxxpwd\""
    exit(-1)
    pass

  global GOLBAL_JIRA_ID;
  global GOLBAL_COMMIT_MSG;

  GOLBAL_JIRA_ID = issue_id
  GOLBAL_COMMIT_MSG = commit_message
  statistics.add_jira_count()
  return True
  pass

def update_jira_comment(issue_id, commit_message):
  jira_user = jira_user_name()
  jira_password = jira_user_pwd()

  try:
    authed_jira = JIRA(server=(base64.decodestring(JIRA_SERVER_URL)), basic_auth=(jira_user, jira_password))
    issue = authed_jira.issue(issue_id)
    authed_jira.add_comment(issue, commit_message)
    return True
    pass
  except JIRAError as je:
    str1 = "提交信息注释到JIRA失败,请手动复制以下提交信息去填充jira的注释\n\n"
    str2 = "需要填充的JIRA号为:"+issue_id+"\n\n"
    str3 = "提交信息为:\n\n"+commit_message+"\n\n\n\n"
    str4 = "异常信息:\n"+je.__str__().encode('utf-8')
    send.send_mail_for_fail_jira(str1+str2+str3+str4)
    return False

  pass

def note_jira(review_url):
    if not review_url:
      review_url = ""
      pass
      
    if GOLBAL_JIRA_ID == "":
      print "获取JIRA号异常,JIRA号为空,无法填充jira注释"
      return
      pass

    if GOLBAL_COMMIT_MSG == "":
      print "读取commit msg异常,无法填充jira注释"
      return
      pass
    if len(review_url)>0:
      statistics.add_review_jira_count()
      pass

    print "你填写的jira号是:"+GOLBAL_JIRA_ID
    print "正在把msg填充到jira...请稍候"
    commit_message = GOLBAL_COMMIT_MSG + review_url
    success = update_jira_comment(GOLBAL_JIRA_ID,commit_message)
    if success:
      print "填充完成,提交中...请稍候"
    else:
      print "填充失败,需要手动填充;提交中...请稍候"
      pass
    
    pass

def jira_user_name():
  return check_out_put("git config jira.user", False, "")
  pass

def jira_user_pwd():
  return check_out_put("git config jira.pwd", False, "")
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


