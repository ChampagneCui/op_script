#!/usr/bin/env python
# coding: utf-8
# author: Champagne Cui

import jenkins
import sys
import threading
import time

url_dict={'qa':'http://x.x.x.x/jenkins/',
		  'prd':'http://y.y.y.y/jenkins'}

username_dict={'qa':'admin-qa','prd':'admin-prd'}

token_dict={'qa':'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
			'prd':'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'}
str = "-"
env2job_dict={'qa':"checkout_qa",'prd':"checkout_prd"}
help='''For example:
#不切分支
./jenkins_deploy.py rebuild qa-job1,qa-job2,qa-job3
#qa例行发布
./jenkins_deploy.py qa qa-job1,qa-job2,qa-job3,qa-job4
#生产发布
./jenkins_deploy.py prd prd-job1,prd-job2,prd-job3,prd-job4'''


class myjenkins:
	def __init__(self,env):
		self.server = jenkins.Jenkins(url_dict[env],
									  username=username_dict[env],
									  password=token_dict[env])

	def build_job(self,job_name,param_dict=''):
		next_build_num=self.server.get_job_info(job_name)['nextBuildNumber']
		if param_dict=='':
			self.server.build_job(job_name)
		else:
			self.server.build_job(job_name,parameters=param_dict)
		while 1:
			try:
				result=self.server.get_build_info(job_name,next_build_num)
				if (result['result'] != None) and (result['building'] == False):
					break
			except:
				continue
		print("%s(%s) build %s" %(job_name,result['displayName'],result['result']))
		return result['result']

	@staticmethod
	def usage():
		print(help)


def func(job_name,branch_do):
		job_name=job_name.strip()
		env = job_name.split('-')[0]
		project_name = job_name.split('-')[1:]
		project_name = str.join(project_name)

		a = myjenkins(env)
		if branch_do != 'rebuild':
			checkout_result = a.build_job(env2job_dict[branch_do], {'ProjectName': project_name})
		else:
			checkout_result = 'SUCCESS'

		if checkout_result == 'SUCCESS':
			a.build_job(job_name)
		else:
			print("Checkout % failed" % (job_name))


def main():
	branch_do=sys.argv[1]

	if branch_do == '--help':
		myjenkins.usage()
		exit()

	jobs = sys.argv[2]
	jobs=jobs.split(',')

	if jobs != []:
		for job_name in jobs:
			S=threading.Thread(target=func,args=(job_name,branch_do))
			S.start()
			time.sleep(15) #不sleep的话，切分支会抓到同一个next_build_num

if __name__ == '__main__':
	main()
