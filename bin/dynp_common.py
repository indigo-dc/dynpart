#!/usr/bin/env python

import os,sys,time

def now():
    return time.ctime(time.time())

def mlog(f,m,dbg=True):
    if dbg:
        f.write("%s: "%now()+m+'\n')
        f.flush()
