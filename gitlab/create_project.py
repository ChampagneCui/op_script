#!/usr/bin/env python
#coding:utf-8
import sys,getopt
import requests
import time
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

dict={}

GITLAB_URL = 'http://Your Gitlab Url Here/api/v3/'
GITLAB_PRIVATE_TOKEN = 'Your token here!'
NOW=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def create_project():
    project_name=raw_input('Please enter a new project name:')
    url = GITLAB_URL + 'projects/?name=' + project_name
    headers = {'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN}
    r = requests.post(url,headers = headers)
    print(r.text)


create_project()
