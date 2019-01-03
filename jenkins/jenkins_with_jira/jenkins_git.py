#!/usr/bin/env python
# coding: utf-8
# author: Champagne Cui


import sys
import requests
import re
import xmltodict
import threading
import gitlab
import redis
import random
import string
import time
import json
from jira.client import JIRA

from jenkins import Jenkins

jenkins_url = 'http://ci.xxxx.com'
username = 'jira_auto'
token_dict = 'xxxxxxxxxxxxxxxxxx'
jira_url = "http://jira.dop.xxxx.com"
jira_user = "jira_auto"
jira_passwd = "xxxxxxxxxx"
jira_id = sys.argv[2]  # 获取JiraId 例jira_id = 'VERPOOL-1939'
#jira_id = 'OPS-9'
git_url = 'https://git.xxxx.com'
git_token = 'xxxxxxxxxxxxxxxxxxxxxxx'
redis_server = 'redis.xxxx.qa'
redis_password = 'xxxxxxxxxxxxxxxxxxx'
keyname = 'merge_'+jira_id +':'+ ''.join(random.sample(string.ascii_letters + string.digits, 16))


class myjenkins:
	def __init__(self):
		self.server = Jenkins(jenkins_url,
		                      username=username,
		                      password=token_dict)

	def getjobconfig(self, job_name):
		job_info = self.server.get_job_config(job_name)
		return job_info

	# 根据给来的app id查询job的完整name，目前只看'0-Site'和'1-API'两个view下的，如果有需要可以加，需要保证这两个view下的所有job在view下都是唯一的
	def search_job_name(self, job_id):
		site = self.server.get_jobs(view_name='0-Site')
		web = self.server.get_jobs(view_name='1-API')
		b = site + web
		job_name = ''
		for i in b:
			w = re.findall(job_id, i['name'])
			if w != []:
				job_name = i['name']
		return job_name

	# 根据job的配置文件，找到他的git仓库地址，用于判断用户传入的分支名是否存在
	def get_git_url(self, job_name):
		info = self.getjobconfig(job_name)
		convertedDict = xmltodict.parse(info)
		git_repo_url = convertedDict['project']['scm']['userRemoteConfigs']['hudson.plugins.git.UserRemoteConfig'][
			'url']
		return git_repo_url


def get_git_repo_brach(job_id,job_url):
	job_name = job_url.split('/')[-1].strip('.git')
	gl = gitlab.Gitlab(git_url, git_token)
	project_list = gl.projects.list(search=job_name)
	if len(project_list) == 1:
		branches = project_list[0].branches.list()
		branch_list = []
		for i in branches:
			branch_name = 'origin/' + i.name
			branch_list.append(branch_name)
		return branch_list
	elif len(project_list)>1:
		for item in project_list:
			if item.attributes['http_url_to_repo']==job_url:
				#print(project_list[0].attributes['http_url_to_repo'])
				branches = project_list[0].branches.list()
				branch_list = []
				for i in branches:
					branch_name = 'origin/' + i.name
					branch_list.append(branch_name)
				return branch_list
		err_msg = 'FAILURE! Find job %s in git failed!' % (job_name)
		word(job_id, err_msg)
		exit(err_msg)
	else:
		err_msg = 'FAILURE! Find job %s in git failed!' % (job_name)
		word(job_id, err_msg)
		exit(err_msg)

class redis_op:
	def __init__(self, redis_server, password):
		self.r = redis.Redis(host=redis_server, port=6379, password=password,db=7, decode_responses=True)

	def store2redis(self, name, value):
		self.r.rpush(name, value)

	def get_redis(self, name):
		return self.r.lrange(name, 0, -1)

	def len_key(self, name):
		return self.r.llen(name)

def check_merge(mr,job_id,source_branch, target_branch):
	changes = (mr.changes())['changes']
	if changes == []:
		mr.delete()
		result = 'FAILURE!' + 'No changes found!'
		word(job_id, result)
		exit(result)
	else:
		try:
			mr.merge()
			result = 'SUCCESS! Merge success from %s to %s!' % (source_branch, target_branch)
			return result
		except Exception as e:
			mr.delete()
			result = 'FAILURE!' + e.error_message
			word(job_id, result)
			exit(result)

def git_merge(git_repo_url, source_branch,target_branch, job_id):
	gl = gitlab.Gitlab(git_url, git_token)
	project_name = git_repo_url.split('/')[-1].strip('.git')
	source_branch = source_branch.replace('origin/','')

	project_list = gl.projects.list(search=project_name,all=True)
	if len(project_list) == 1:
		project=project_list[0]

		try:
			project.tags.create({'tag_name': source_branch, 'ref': source_branch}) #tag
		except Exception as e:
			result = 'FAILURE!'+e.error_message
			print(result)
		mr = project.mergerequests.create({'source_branch': source_branch,
		                                   'target_branch': target_branch,
		                                   'title': 'merge %s to %s by auto' % (source_branch,target_branch),
		                                   'remove_source_branch': True})
		check_merge(mr,job_id,source_branch, target_branch)
	elif len(project_list)>1:
		for item in project_list:
			if item.attributes['http_url_to_repo']==git_repo_url:
				project=item
				try:
					project.tags.create({'tag_name': source_branch, 'ref': source_branch})  # tag
				except Exception as e:
					result = 'FAILURE!' + e.error_message
					print(result)
				mr = project.mergerequests.create({'source_branch': source_branch,
				                                   'target_branch': target_branch,
				                                   'title': 'merge %s to %s by auto' % (source_branch, target_branch),
				                                   'remove_source_branch': True})
				check_merge(mr,job_id,source_branch, target_branch)
	else:
		err_msg = 'FAILURE! Find job %s in git failed!' % (job_id)
		word(job_id, err_msg)
		exit(err_msg)


def func(job_id, branch):
	a = myjenkins()
	##get job name
	if job_id != [] and job_id.isdigit():
		job_name = a.search_job_name(job_id)
	else:
		err_msg = 'FAILURE! job_id %s can not be found in "0-Site" or "1-API" view!' %(job_id)
		word(job_id, err_msg)
		exit(err_msg)

	if job_name == '':
		err_msg = 'FAILURE! 参数“%s”未找到对应的job' %(job_id)
		word(job_id, err_msg)
		exit(err_msg)
	else:
		git_repo_url = a.get_git_url(job_name)
		git_brach_list = get_git_repo_brach(job_id,git_repo_url)  # *****************
		if branch not in git_brach_list:
			err_msg = 'FAILURE! 未在%s任务中找到对应的分支 %s !' % (job_name, branch)
			word(job_id, err_msg)
			exit(err_msg)

	random_time = random.uniform(0, 1)
	time.sleep(random_time)
	result = git_merge(git_repo_url, branch, 'master' ,job_id)
	word(job_id, result)


def word(job_id='', result=''):
	a = redis_op(redis_server, redis_password)
	body = 'Job ID:%s merge %s' % (job_id, result)
	a.store2redis(keyname, body)


def check_and_commit(a, number, keyname):
	while a.len_key(keyname) <number:
		time.sleep(5)
		continue
	else:
		result = a.get_redis(keyname)
		S_num = 0
		F_Num = 0
		for i in result:
			c = re.findall('FAILURE', i)
			d = re.findall('SUCCESS', i)
			S_num += len(d)
			F_Num += len(c)
		b="统计：一键合并了：%s 个，成功：%s 个，失败：%s 个" %(number,S_num,F_Num) +'\n'
		for i in result:
			b = b + i + '\n'
		jira = JIRA(jira_url, basic_auth=(jira_user, jira_passwd))
		jira.add_comment(jira_id, str(b))


def main():
	job_list = sys.argv[1]
	#job_list = '80001:origin/test:dev'
	job_list=job_list.strip()
	a = redis_op(redis_server, redis_password)
	print(
		"NOTICE!!! The Result will be store in Redis Server(redis.xxxx.qa)db7 {keyname} key. If you have any problem,please check in redis!".format(
			keyname=keyname))
	if job_list[-1] == ',':
		job_list = job_list[:-1]
	number = len(job_list.split(','))
	for job in job_list.split(','):
		if len(job.split(':')) != 3:
			err_msg = 'FAILURE! jira参数数量错误！'
			word(job.split(':')[0], err_msg)
		else:
			job_id = job.split(':')[0].strip()
			branch = job.split(':')[1].strip()

		S = threading.Thread(target=func, args=(job_id, branch))
		S.start()
	check_and_commit(a, number, keyname)


if __name__ == '__main__':
	main()