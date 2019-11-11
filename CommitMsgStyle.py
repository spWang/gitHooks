#!/usr/bin/env python
# coding=utf-8

import sys
import re
import subprocess
import reviewboard

maxSubjectLen = 380
typesList = ['feat','fix','docs','style','refactor','test','chore']

MERGE_BRANCH_TEXT = "Merge branch"
CONFLICTS_TEXT = "# Conflicts:"

GLOBAL_BLUR_JIRA_ID = ""
GLOBAL_TRUE_JIRA_ID = ""


def open_fun():
    return check_out_put('git config githooks.checkmsg', False ,"YES")
    pass

def mark_did_blur_check():
    if check_out_put("git config githooks.blurcheck", False, None):
        check_out_put("git config --unset githooks.blurcheck", False, "")
        pass
    pass

def reset_check_msg_state():
    if check_out_put('git config githooks.checkmsg', False ,"YES") == "NO":
        check_out_put('git config githooks.checkmsg \"YES\"', False, "")
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
def check_contain_chinese(check_str):
    for ch in check_str.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False
    pass

#xm检查的类
class CheckMsgStyle(object):
    """检查提交信息规范的功能"""

    @classmethod
    def headerTypesList(self):
        return typesList
        pass

    @classmethod
    def check_msg_if_need(self):
        if  open_fun() == "NO":
            print "未开启检查提交信息规范的功能,如需开启请执行:git config githooks.checkmsg \"YES\""
            return
            pass
        print "已开启检查提交信息规范的功能"

        content = self.__commitMsg()

        self.__CheckMsg(content)        

    pass

    #检查提交信息是否正常
    @classmethod 
    def __CheckMsg(self, content):

        logContent = "你的提交信息如下:\n%s" % content
        
        #0.处理合并时有冲突的情况
        if MERGE_BRANCH_TEXT in content or CONFLICTS_TEXT in content:
            content = "feat:"+content
            pass
         #1.匹配空行
        changeLineRegex = re.compile(r".*\S\n\n.*\S", re.S)
        changeLineMachObject = changeLineRegex.match(content)
        if not changeLineMachObject:
            print logContent
            print "msg格式不对,必须包含一个空行以区分header和body,且空行前后内容不为空"
            reviewboard.reset_review_state()
            sys.exit(1)

        #2.匹配冒号
        headerContent = content.split('\n\n',1)[0]
        colonRegex = re.compile(r".*\S:.*\S", re.I)
        colonMachObject = colonRegex.match(content)
        if not colonMachObject:
            print logContent
            print "msg格式不对,header中必须有一个冒号(:)来区分type和subject,冒号前后内容不为空"
            reviewboard.reset_review_state()
            sys.exit(1)

        
        #3如果有(),校验jira
        typeJiraContent = headerContent.split(':',1)[0]
        typeContent = typeJiraContent
        
        #3.1校验小括号
        jiraRegex = re.compile(r".*\S\(.*\S\)", re.I)
        jiraMachObject = jiraRegex.match(typeJiraContent)
        if jiraMachObject:
            typeContent = typeJiraContent.split('(',1)[0]

        #4.匹配type
        if typeContent in typesList:
            pass
        else:
            print "你的type是:%s" % typeContent
            print "type类型不正确,必须为下面其中一个:%s" % typesList
            reviewboard.reset_review_state()
            sys.exit(1)  

        #4校验subject字数
        #冲突的时候,不校验subject字数
        if MERGE_BRANCH_TEXT in content or CONFLICTS_TEXT in content:
            return
            pass
        subjectContent = headerContent.split(':',1)[1]
        trimSpaceContent = subjectContent.replace(' ','')#去除掉空格再检查
        subjectLen = len(trimSpaceContent.decode('utf-8'))
        if subjectLen>maxSubjectLen:
            print "首行最多%s个字,你超出了%d个字" % (maxSubjectLen,subjectLen-maxSubjectLen)
            print "你的subject是:%s" % subjectContent
            reviewboard.reset_review_state()
            sys.exit(1)
        
        #5 JIRA模糊匹配     
        blur = self.__check_is_blur_JIRAID(content, typeContent)
        did_check_blur = check_out_put("git config githooks.blurcheck", False, "NO")
        if blur and (did_check_blur == "NO") and len(GLOBAL_TRUE_JIRA_ID)>0:
            print "\n检测到你可能想要提交到JIRA注释里,但是JIRA号填写的位置不对,应该在冒号前边,如果确实要将提交信息添加到JIRA里,请按以下信息重新修改后提交;如果不是,再次直接提交即可"
            print content.replace(GLOBAL_BLUR_JIRA_ID,GLOBAL_TRUE_JIRA_ID)
            check_out_put("git config githooks.blurcheck \"YES\"", False, True)
            exit(-1)
            pass

        print "提交中.."

    @classmethod
    def __check_is_blur_JIRAID(self, content, type_content):

        #初步检测包含:(
        if content.find(type_content+":(") != 0:
            return False
            pass

        #检测其后边含有)
        blur_content = content[len(type_content+":("):]
        if blur_content.find(")") == -1:
            return False
            pass

        #模糊匹配出的JIRAID,看最后的JIRAID)后是否还有内容
        blur_jira_ID = blur_content[0:blur_content.find(")")]        
        if blur_content.find("\n") == blur_content.find(")")+1:
            return False
            pass
        #匹配出的JIRAID为空
        if len(blur_jira_ID)==0:
            return False
            pass
        #匹配出的JIRAID有中文
        if check_contain_chinese(blur_jira_ID):
            return False
            pass

        global GLOBAL_BLUR_JIRA_ID
        global GLOBAL_TRUE_JIRA_ID
        GLOBAL_BLUR_JIRA_ID = ":("+blur_jira_ID+")"
        GLOBAL_TRUE_JIRA_ID = "("+blur_jira_ID+"):"

        return True
            
        pass

    #获取提交的内容
    @classmethod
    def __commitMsg(self):
        commit_msg_filepath = sys.argv[1]

        with open(commit_msg_filepath, 'r+') as f:
            content = f.read()
            return content
    pass

