#!/usr/bin/env python
# coding=utf-8

import subprocess
import os
import statistics
from util.colorlog import *

'''公开函数'''
def key_words():
    return ["re-", "re_", "review-", "review_", "rbt-","rbt_"]
    pass

def log_operation_not_permitted(file_path, func_desc, cammand):
    print "\n"
    log_str = "sudo bash " + hooks_path()+"bridge.sh"
    print file_path+"文件不存在,无法在非命令行中使用"+func_desc+"的功能,你需要做下面的事情:"
    print "  1. 复制下个命令创建软链接后再尝试提交代码"+log_str
    print "  2. 如果执行上边命令时遇到Operation not permitted(权限不允许),说明你的mac SIP权限没有禁用,无法向/usr/bin里边写入文件去创建软链接,解决办法看此网址http://blog.csdn.net/u012165769/article/details/50477410"
    print "  3. 当你关闭了SIP权限后,需要重新再执行此命令"+log_str+"执行完毕再push"
    print "\n"
    print cammand
    pass

def post_review_if_need():
    review_state = check_out_put("git config githooks.review", False, "NO")
    if review_state == "NO":
        return ""
        pass
    
    advice = " 如果你遇到自动发送review的问题,请先将问题反馈脚本开发者,然后执行此命令(git config githooks.review \"NO\")临时关闭一次此功能,最后重新push。\n"
    logblue(advice)
        
    check_cammand_can_execute()

    print "正在发送reviewboard请求..."
    cammand = "rbt post -g -p"
    father_branch = check_out_put("git config githooks.rbtbranch", False, "")
    
    if len(father_branch)>0:
        print "你指定了review的父分支,它是:"+father_branch
        cammand = cammand+" --parent="+father_branch
        pass
    print "本次review命令是:"+cammand

    result = check_out_put(cammand,False, "")
    reset_review_state()
    statistics.add_review_count()

    print "发送reviewboard请求完毕;结果:\n"+result

    if not "\n" in result:
        return result
        pass

    return result[result.index("\n")+1:]
    pass


#根据提交信息检测是否需要标记review,并返回提交信息
def mark_if_need_review(commit_msg):
    for keyword in key_words():
        if commit_msg.find(keyword) == 0:
            check_out_put("git config githooks.review \"YES\"", True, "")

            content = commit_msg[commit_msg.index(keyword)+len(keyword):]
            
            truple = sep_rbt_branch_commitmsg(content)

            father_branch = truple[0]
            msg = truple[1]

            mark_review_parent_branch(father_branch)
            return msg
            pass
        pass
    return commit_msg
    pass

#重置review的状态
def reset_review_state():
    check_out_put("git config --unset githooks.review", False, "")
    reset_review_parent_branch()
    pass

#记录一下指定的父分支
def mark_review_parent_branch(parent_branch):
    if not len(parent_branch):
        return
        pass
    check_out_put("git config githooks.rbtbranch "+parent_branch, False, "")
    pass

#删除记录的父分支
def reset_review_parent_branch():
    check_out_put("git config --unset githooks.rbtbranch", False, "")
    pass

'''私有函数'''
def sep_rbt_branch_commitmsg(content):

    match_obj = re.match(r"\[.*\S\]", content, re.S)
    if match_obj:
        return match_obj.group()[1:-1],content[match_obj.end():]
        pass

    return "",content
    pass

def file_path_exist(file):
    return os.path.exists(file) and os.path.isfile(file)
    pass

def check_cammand_can_execute():
    file_path = "/usr/bin/rbt"
    if not file_path_exist(file_path):
        log_operation_not_permitted(file_path, "自动发送review", "git config githooks.review \"NO\"")
        exit(-1)
        pass
    pass


'''基础方法'''
def hooks_path():
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