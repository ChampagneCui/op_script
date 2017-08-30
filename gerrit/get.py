#!/opt/bin/env python

import MySQLdb
import os
import sys
import time
import datetime
from requests.auth import HTTPDigestAuth
from pygerrit2.rest import GerritRestAPI

branch=sys.argv[2]
com_branch=sys.argv[3]
project=sys.argv[1]



class gerrit():
	def __init__(self,user,passwd,url):
		self.user=user
		self.passwd=passwd
		self.url=url
		self.rest=self.conn()

	def conn(self):
		auth = HTTPDigestAuth(self.user,self.passwd)
		rest = GerritRestAPI(url=self.url, auth=auth)
		return rest
		
	def get_commit(self,project,branch):
		res=self.rest.get('/projects/Cloud%2F{0}/branches/{1}/'.format(project,branch))
		#print(res)
		return res['revision']

	def get_commit_time(self,commit):
		res=self.rest.get('/changes/?q=commit:{0}'.format(commit))
		if res==[]:
			'''local time'''
			#res=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			'''utc time'''
			res=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
			return res
		else:
			return res[0]['created']




if __name__=='__main__':
	a=gerrit('Your Username Here','Your token Here','http://Your Gerrit Url Here')
	commit=a.get_commit(project,branch)
	com_commit=a.get_commit(project,com_branch)
	
	#print(commit)
	if commit==com_commit:
		exit
	else:
		os.system('sh show.sh {0} {1} {2}'.format(project,commit,com_commit))
