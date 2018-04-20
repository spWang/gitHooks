#!/usr/bin/env python
# coding=utf-8

import re, os, sys

def logblack(msg):
    print "\033[1;30;1m%s\033[0m" % msg;
    pass

def logred(msg):
    print "\033[1;31;1m%s\033[0m" % msg;
    pass

def loggreen(msg):
    print "\033[1;32;1m%s\033[0m" % msg;
    pass

def logyellow(msg):
    print "\033[1;33;1m%s\033[0m" % msg;
    pass

def logblue(msg):
    print "\033[1;34;1m%s\033[0m" % msg;
    pass

def logpurple(msg):
    print "\033[1;35;1m%s\033[0m" % msg;
    pass

def logbule_green(msg):
    print "\033[1;36;1m%s\033[0m" % msg;
    pass

def loggray(msg):
    print "\033[1;37;1m%s\033[0m" % msg;
    pass