#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import division
import os
import subprocess


#statistics

#公开
def data_collect():
    commits = int(all_commit_count())
    if not commits:
        return ""
        pass

    reviews = int(review_count())
    jiras = int(jira_count())
    review_jira = int(review_jira_count())

    review_percent = "{:.2f}{}".format(reviews/commits*100,"%")
    jira_percent = "{:.2f}{}".format(jiras/commits*100,"%")
    review_jira_percent = "{:.2f}{}".format(review_jira/commits*100,"%")
    
    title = "\n\n数据统计(本统计用来看下使用习惯,并无其他用途)"
    commit_count_str = "距离上次更新后,本周期本仓库总提交数量:"+str(commits)
    review_count_str = "使用自动review功能的数量:"+str(reviews)+"(占比:"+review_percent+")"
    jira_count_str = "使用填充jira功能的数量:"+str(jiras)+"(占比:"+jira_percent+")"
    review_jira_count_str = "同时使用jira和review功能的数量:"+str(review_jira)+"(占比:"+review_jira_percent+")"
    
    text = "\n".join([title,commit_count_str,review_count_str,jira_count_str,review_jira_count_str])
    clear_all_counts()

    return text
    pass

def add_all_commit_count():
    commits = int(all_commit_count())
    result = str(commits+1)
    check_out_put("git config githooks.commitnum "+result, False, "")
    pass

def add_review_count():
    reviews = int(review_count())
    result = str(reviews+1)
    check_out_put("git config githooks.reviewnum "+result, False, "")
    pass

def add_jira_count():
    jiras = int(jira_count())
    result = str(jiras+1)
    check_out_put("git config githooks.jiranum "+result, False, "")
    pass

def add_review_jira_count():
    review_jira = int(review_jira_count())
    result = str(review_jira+1)
    check_out_put("git config githooks.reviewjiranum "+result, False, "")

    pass

def clear_all_counts():
    check_out_put("git config --unset githooks.commitnum", False, "0")
    check_out_put("git config --unset githooks.reviewnum", False, "0")
    check_out_put("git config --unset githooks.jiranum", False, "0")
    check_out_put("git config --unset githooks.reviewjiranum", False, "0")
    pass

#私有
def all_commit_count():
    return check_out_put("git config githooks.commitnum", False, "0")
    pass

def review_count():
    return check_out_put("git config githooks.reviewnum", False, "0")
    pass

def jira_count():
    return check_out_put("git config githooks.jiranum", False, "0")
    pass

def review_jira_count():
    return check_out_put("git config githooks.reviewjiranum", False, "0")
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
