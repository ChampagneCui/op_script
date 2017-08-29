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
def project_list():
    url = GITLAB_URL + '/projects?private_token=' + GITLAB_PRIVATE_TOKEN + '&per_page=2000'
    r = requests.get(url)
    data = r.json()
    for i in data:
        id = i[u'id']
        name = i[u'name']
        dict[name]=id
    return dict

def project_query(project_name):
    url = GITLAB_URL + 'projects/search/' + project_name
    headers = {'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN}
    r = requests.get(url,headers = headers)
    data = r.json()
    for i in data:
        id = i[u'id']
        name = i[u'name']
	if name == project_name:
		break
    return id

def protect_branch(project_id,branch_name):
    url = GITLAB_URL + 'projects/' + project_id + '/repository/branches/' + branch_name + '/protect'
    print(url)
    headers = {'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN}
    r = requests.put(url,headers = headers)
    print(r.text)

def unprotect_branch(project_id,branch_name):
    url = GITLAB_URL + 'projects/' + project_id + '/repository/branches/' + branch_name + '/unprotect'
    headers = {'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN}
    r = requests.put(url,headers = headers)
    print(r.text)


def create_branch(project_id,newbranch_name,from_branch):
    url = GITLAB_URL + 'projects/' + project_id + '/repository/branches?branch_name=' + newbranch_name + '&ref=' + from_branch
    headers = {'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN}
    r = requests.post(url,headers = headers)
    print(r.text)

def delete_branch(project_id,newbranch_name):
    url = GITLAB_URL + 'projects/' + project_id + '/repository/branches/' + newbranch_name 
    print url
    headers = {'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN}
    r = requests.delete(url,headers = headers)
    print(r.text)


def usage():
    print '\033[1;32;40m'
    print '*' * 50
    print '*COMMAND:\t', 'python gitlab.py args'
    print '*HELP:\t', 'python gitlab.py --help'
    print '*VERSION:\t', 'V0.0.1'
    print '*' * 50
    print '\033[0m'
    print '\n' \
          'eg: python gitlab.py -t project_list \n' \
          'eg: python gitlab.py -t create_branch -p <project_name> -b <newbranch_name> -f <from_branch> \n' \
          'eg: python gitlab.py -t create_branch -p <project_name> -b <newbranch_name> \n' \
          'eg: python gitlab.py -t protect_branch -p <project_name> -f <branch_name> \n' \
          'eg: python gitlab.py -t unprotect_branch -p <project_name> -f <branch_name> \n' \
          '\n' \
          ' -t command type\n' \
          ' -p gitlab project id\n' \
          ' -b create new branch name\n' \
          ' -f new branch from branch\n' \
          ''

def main():
    command_type = ''
    project_name = ''
    newbranch_name = ''
    from_branch = ''

    if len(sys.argv) < 2:
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:t:p:b:f:", ["help", "type=","project_id=","branch=","from="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for name, value in opts:
        if name in ('-h','--help'):
            usage()
        elif name in ("-t", "--type"):
            command_type = value
        elif name in ("-p", "--project_name"):
            project_name = value
    	    #project_id=str(dict[project_name])
        elif name in ("-b", "--branch_name"):
            newbranch_name = value
        elif name in ("-f", "--from_branch"):
            from_branch = value
        else:
            assert False, "unhandled option"

    dict=project_list()
    try:
    	#project_id=str(dict[project_name])
    	project_id=str(project_query(project_name))
    except:
	pass
 

    if command_type == "project_list":
        print(dict)
    elif command_type == "create_branch":
        if project_id != "" and newbranch_name != "" and from_branch != "":
	    print(project_id,newbranch_name,from_branch)
            create_branch(project_id,newbranch_name,from_branch)
        else:
            print "please input -p project_name -b newbranch_name -f from_branch"
    elif command_type == "delete_branch":
	if project_id != "" and newbranch_name != "":
	    delete_branch(project_id,newbranch_name)
	else:
            print "please input -p project_name -b newbranch_name"
    elif command_type == "protect_branch":
        if project_id != "" and from_branch != "":
            protect_branch(project_id,from_branch)
        else:
            print "please input -p project_name -f branch_name"
    elif command_type == "unprotect_branch":
        if project_id != "" and from_branch != "":
            unprotect_branch(project_id,from_branch)
        else:
            print "please input -p unproject_name -f branch_name"

if __name__ == "__main__":
    main()
