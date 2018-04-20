#!/usr/bin/env python
# coding=utf-8

import sys
import re
import subprocess
import reviewboard
import AutoVersion


'''公开函数'''
#添加subject
def add_subject_if_need():
    commit_msg_filepath = sys.argv[1]
    
    with open(commit_msg_filepath, 'r+') as f:
        msg = f.read()
    pass
    
    if text_contain_blankrow(msg):
        with open(commit_msg_filepath, 'w') as f:
            result = reviewboard.mark_if_need_review(msg)
            f.write(result)
        return
        pass

    with open(commit_msg_filepath, 'w') as f:
        result = reviewboard.mark_if_need_review(msg)
        if ":" in result:
            result = result+"\n"+"1."+result[result.index(":")+1:] 
            pass
        f.write(result)
    pass
    pass

#添加版本号/分支名字
def add_premsg_if_need():
    if add_msg_state() == "NO":
        print "未开启添加版本号/分支的功能,如需开启请执行git config githooks.premsg \"YES\""
        return
        pass
    print "已开启提交信息前添加分支/版本号功能"

    pre_text = get_add_text()
    commit_msg_filepath = sys.argv[1]
    
    with open(commit_msg_filepath, 'r+') as f:
        commti_msg = f.read()
        pass

    with open(commit_msg_filepath, 'w') as f:
        result = pre_text+commti_msg
        f.write(result)
        pass
    pass

#获取当前拼接的内容
def get_add_text():
    
    version = AutoVersion.read_current_project_version()
    if len(version)>0:
        return version
        pass

    #拼接分支
    return "["+current_branch()+"]"

    pass

def reset_add_premsg_state():
    if check_out_put('git config githooks.premsg', False ,"YES") == "NO":
        check_out_put('git config githooks.premsg \"YES\"', False, "")
        pass
    pass

def add_msg_state():
    return check_out_put('git config githooks.premsg', False, "YES")
    pass

'''私有函数'''
def current_branch():
    branch = check_out_put("git symbolic-ref --short -q HEAD", False, "HEAD")
        
    if len(branch) == 0:
        branch = "HEAD"
        return branch
        pass
        
    #分割分支的全路径
    lists = branch.split('/')
    now_branch = lists[len(lists)-1]
        
    #当前分支不包含父文件夹名字,则给拼上
    if len(lists)>2:
        father_dir = lists[len(lists)-2]
        if now_branch.find(father_dir) == -1:
            now_branch = father_dir+"/"+now_branch
            pass
        pass
    
    return now_branch
    pass

#文本是否包含空行
def text_contain_blankrow(content):
    changeLineRegex = re.compile(r".*\S\n\n.*\S", re.S)
    changeLineMachObject = changeLineRegex.match(content)
    if changeLineMachObject:
        return True
        pass

    return False
    pass

#基础方法
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