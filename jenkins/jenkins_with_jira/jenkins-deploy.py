# !/usr/bin/env python
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
from jira.client import JIRA

from jenkins import Jenkins

jenkins_url = 'http://ci.ixxxx.com'
username = 'jira_auto'
token_dict = 'xxxxxxxxxxxx'
jira_url = "http://jira.dop.xxxx.com"
jira_user = "jira_auto"
jira_passwd = "xxxxxxxxxxxxxxxxxxxxx"
jira_id=sys.argv[2] #获取JiraId 例jira_id = 'VERPOOL-1939'
#jira_id = 'OPS-9'
git_url = 'https://git.ixxxx.com'
git_token = 'xxxxxxxxxxxxxxxxxxxxxx'
redis_server = 'redis.xxxx.qa'
redis_password = 'xxxxxxxxxxxxxxxxxxxxxx'
keyname = jira_id +':'+ ''.join(random.sample(string.ascii_letters + string.digits, 16))


# 替换掉Jenkins类中的build_job函数（不然貌似有点问题），其他的函数都继承下来，接下来就用jenkins2这个类了
class jenkins2(Jenkins):
	def build_job(self, name, parameters=None, token=None):
		response = self.jenkins_request(requests.Request(
			'POST', self.build_job_url(name, parameters, token)))
		location = response.headers['Location']
		# location is a queue item, eg. "http://jenkins/queue/item/25/"
		if location.endswith('/'):
			location = location[:-1]
		parts = location.split('/')
		number = int(parts[-1])
		return number


class myjenkins:
	def __init__(self):
		self.server = jenkins2(jenkins_url,
		                       username=username,
		                       password=token_dict)

	def build_job(self, job_name, param_dict=''):
		if param_dict == '':  # 判断该脚本是否有参数传入
			queue_id = self.server.build_job(job_name)
		else:
			queue_id = self.server.build_job(job_name, parameters=param_dict)
		return queue_id

	def buildinfo(self, job_name, num):
		self.server.get_build_info(job_name, num)

	def getjobconfig(self, job_name):
		job_info = self.server.get_job_config(job_name)
		return job_info

	# 根据给来的app id查询job的完整name，目前只看'0-Site'和'1-API'两个view下的，如果有需要可以加，需要保证这两个view下的所有job在view下都是唯一的
	def search_job_name(self, job_id):
		job_name_list=[]
		site = self.server.get_jobs(view_name='0-Site')
		web = self.server.get_jobs(view_name='1-API')
		b = site + web
		for i in b:
			w = re.findall(job_id, i['name'])
			if w != []:
				job_name_list.append(i['name'])
		if len(job_name_list)>1:
			err_msg='FAILURE! %s 找到多个job，故未执行' %(job_id)
			word(job_id,err_msg)
			exit(err_msg)
		else:
			return job_name_list[0]

	# 因为传参还是要传ip，而用户传过来时是环境，所以我需要爬一下对应job的配置文件，自己建立一份ip与环境关系的字典
	def get_ip_dict(self, job_name,job_id):
		info = self.getjobconfig(job_name)
		convertedDict = xmltodict.parse(info)
		obj = \
			convertedDict['project']['properties']['hudson.model.ParametersDefinitionProperty']['parameterDefinitions'][
				'com.cwctravel.hudson.plugins.extended__choice__parameter.ExtendedChoiceParameterDefinition']
		iplist = obj['value'].split(',')
		ipdes = obj['descriptionPropertyValue'].split(',')
		ipdict = {}
		if len(iplist) != len(ipdes):
			err_msg = 'FAILURE! 参数ip与description数量不一一对等'
			word(job_id, err_msg)
			exit(err_msg)
		else:
			i = 0
			while i < len(iplist):
				ipdict[ipdes[i]] = iplist[i]
				i += 1
		return ipdict

	# 根据job的配置文件，找到他的git仓库地址，用于判断用户传入的分支名是否存在
	def get_git_url(self, job_name):
		info = self.getjobconfig(job_name)
		convertedDict = xmltodict.parse(info)
		git_repo_url = convertedDict['project']['scm']['userRemoteConfigs']['hudson.plugins.git.UserRemoteConfig'][
			'url']
		return git_repo_url

	# 通过queue id查询job task id，这里需要备注：每次执行job时不是立刻执行的，而是先进入队列，此时只有队列id，而没有该job的task id，此id需等真正执行的时候才有
	def get_queue_info(self, number):
		info = ''
		while info == '':
			if 'executable' in self.server.get_queue_item(number):
				if 'number' in self.server.get_queue_item(number)['executable']:
					info = int(self.server.get_queue_item(number)['executable']['number'])
				else:
					continue
			else:
				continue
		return info

	# 拿着task id等待着结果，拿到结果将结果反馈
	def get_job_result(self, job_name, job_task_id):
		while 1:
			try:
				result = self.server.get_build_info(job_name, job_task_id)
				if (result['result'] != None) and (result['building'] == False):
					break
			except:
				continue
		url = 'http://ci.ixxxx.com/job/%s/%s/' % (job_name, job_task_id)
		result = result['result'] + '!' + ' URL:' + url
		return result


class redis_op:
	def __init__(self, redis_server, password):
		self.r = redis.Redis(host=redis_server, port=6379, password=password,db=8, decode_responses=True)

	def store2redis(self, name, value):
		self.r.rpush(name, value)

	def get_redis(self, name):
		return self.r.lrange(name, 0, -1)

	def len_key(self, name):
		return self.r.llen(name)

def get_git_repo_brach(job_id,job_url):
	job_name = job_url.split('/')[-1].strip('.git')
	print(job_name)
	gl = gitlab.Gitlab(git_url, git_token)
	project_list = gl.projects.list(search=job_name,all=True)
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

def check_merge(mr,job_id,source_branch, target_branch):
	changes = (mr.changes())['changes']
	if changes == []:
		mr.delete()
		result = 'FAILURE!' + 'No changes found!'
		print(job_id,result)
	else:
		try:
			mr.merge()
			result = 'SUCCESS! Merge success from %s to %s!' % (source_branch, target_branch)
			print(result)
		except Exception as e:
			mr.delete()
			result = 'FAILURE!' + e.error_message
			word(job_id, result)
			exit(result)

def merge_from_master(git_repo_url, source_branch,target_branch, job_id):
	gl = gitlab.Gitlab(git_url, git_token)
	project_name = git_repo_url.split('/')[-1].strip('.git')
	source_branch = source_branch.replace('origin/','')

	project_list = gl.projects.list(search=project_name,all=True)
	if len(project_list) == 1:
		project=project_list[0]

		mr = project.mergerequests.create({'source_branch': source_branch,
		                                   'target_branch': target_branch,
		                                   'title': 'merge %s to %s by auto' % (source_branch,target_branch)})
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
				                                   'title': 'merge %s to %s by auto' % (source_branch, target_branch)})
				check_merge(mr,job_id,source_branch, target_branch)
	else:
		err_msg = 'FAILURE! Find job %s in git failed!' % (job_id)
		word(job_id, err_msg)
		exit(err_msg)

def func(a, job_id, branch, env):
	print(job_id)
	a = myjenkins()
	##get job name
	if job_id != [] and job_id.isdigit():
		job_name = a.search_job_name(job_id)
	else:
		err_msg = 'FAILURE! job_id %s can not be found in "0-Site" or "1-API" view!' %(job_id)
		word(job_id, err_msg)
		exit(err_msg)

	# get job config for ip
	if job_name == '':
		err_msg = 'FAILURE! 参数“%s”未找到对应的job' %(job_id)
		word(job_id, err_msg)
		exit(err_msg)
	else:
		ipdict = a.get_ip_dict(job_name,job_id)
		git_repo_url = a.get_git_url(job_name)
		git_brach_list = get_git_repo_brach(job_id,git_repo_url)  # *****************
		if branch not in git_brach_list:
			err_msg = 'FAILURE! 未在%s任务中找到对应的分支 %s !' % (job_name, branch)
			word(job_id, err_msg)
			exit(err_msg)
		if env not in ipdict.keys():
			err_msg = 'FAILURE! 未在%s任务中找到对应的env %s !' % (job_name, env)
			word(job_id, err_msg)
			exit(err_msg)

	merge_from_master(git_repo_url, 'master',branch ,job_id) ###merge first
	queue_id = a.build_job(job_name,
	                       {'TARGETBRANCH': branch, 'ServerIP': ipdict[env], 'env': env,
	                        'ServiceIP': ipdict[env]})  # 这里因为有的项目里叫ServerIP，有的叫ServiceIP，反正参数传多了也没事
	job_task_id = a.get_queue_info(queue_id)
	result = a.get_job_result(job_name, job_task_id)
	word(job_id, result)
	# comment2jira(jira_id, job_id, result)


def word(job_id='', result=''):
	a = redis_op(redis_server, redis_password)
	body = 'Job ID:%s has been deployed and the result was %s' % (job_id, result)
	a.store2redis(keyname, body)


def check_and_commit(a, number, keyname):
	while a.len_key(keyname) <number:
		time.sleep(10)
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
		b="统计：发布了：%s 个，成功：%s 个，失败：%s 个" %(number,S_num,F_Num) +'\n'
		for i in result:
			b = b + i + '\n'
		jira = JIRA(jira_url, basic_auth=(jira_user, jira_passwd))
		jira.add_comment(jira_id, str(b))


def main():
	job_list=sys.argv[1]
	#job_list='39004:origin/feature/user_alpha_v1:qa3'
	# jira_issue_id = 'VERPOOL-1939'
	a = redis_op(redis_server, redis_password)
	print("NOTICE!!! The Result will be store in Redis Server(redis.xxxx.qa)db8 {keyname} key. If you have any problem,please check in redis!".format(keyname=keyname))
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
			env = job.split(':')[2].strip()
		if len(sys.argv) > 3:
			env = sys.argv[3]

		S = threading.Thread(target=func, args=(a, job_id, branch, env))
		S.start()
	check_and_commit(a, number, keyname)


if __name__ == '__main__':
	main()