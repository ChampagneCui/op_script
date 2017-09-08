#!/opt/venv/bin/python2.7
#_*_coding:utf-8_*_
from __future__ import print_function
from jenkinsapi.jenkins import Jenkins
import os
import tornado.template
import time
import datetime


url='http://x.x.x.x/jenkins/'
username='xxxxx'
token='xxxxxxxxxxxxxxxxxxxxxxx'
url2='http://y.y.y.y/jenkins/'
username2='yyyyy'
token2='yyyyyyyyyyyyyyyyyyyyyyyyyy'
project_file='job.txt'
result='result.txt'

def get_revision(url,username,token,job_name):
	jenkins = Jenkins(url,username,token)
	try:
		job = jenkins[job_name]
		try:
			lgb = job.get_last_good_build()
			return(lgb.get_revision())
		except:
			return('None')
	except:
		return('None')

def get_time(url,username,token,job_name):
        jenkins = Jenkins(url,username,token)
	try:
        	job = jenkins[job_name]
		try:
        		lgb = job.get_last_good_build()
			return(lgb.get_timestamp())
		except:
			return('None')
	except:
                return('None')
	

def clean():
	if os.path.exists(result):
		file1 = open(result,'w+')
		file1.truncate()

def SH_timezone(date):
	if date=='None':
		return('None')
	else:
		try:
			new_date_st=time.mktime(time.strptime(date,'%Y-%m-%d %H:%M:%S'))
		except:
			new_date_st=time.mktime(time.strptime(date,'%Y-%m-%d %H:%M'))
		new_date_st=int(new_date_st)+28800
		new_date=datetime.datetime.fromtimestamp(new_date_st)
		return(new_date)

def generate(file):
	clean()
	for job in open(file):
		job=job.strip('\n')
		print(job)
		qa='qa-'+job
		pp='jq-'+job
		prd='prd-'+job
		qa_re=get_revision(url,username,token,qa)	
		qa_tm=str(get_time(url,username,token,qa)).strip('+00:00')
		qa_tm=str(SH_timezone(qa_tm))
		pp_re=get_revision(url2,username2,token2,pp)
		pp_tm=str(get_time(url2,username2,token2,pp)).strip('+00:00')
		pp_tm=str(SH_timezone(pp_tm))
		prd_re=get_revision(url2,username2,token2,prd)	
		prd_tm=str(get_time(url2,username2,token2,prd)).strip('+00:00')
		prd_tm=str(SH_timezone(prd_tm))
		#time=str(get_time(job)).strip('+00:00')
		with open(result,'a') as f:
			a=job+'\t'+prd_re+'\t'+prd_tm+'\t'+pp_re+'\t'+pp_tm+'\t'+qa_re+'\t'+qa_tm
			f.write(a)
			f.write("\n")


if __name__=='__main__':
	generate(project_file)

	out = open('result.html', 'wb')
	items = []
	with open('result.txt', 'rb') as f:
  		for line in f:
    			fields = line.strip().split('\t')
    			items.append((fields[0], fields[1], fields[2],fields[3],fields[4], fields[5],fields[6]))
	loader = tornado.template.Loader("./template")
	out.write(loader.load("table.html").generate(items=items).decode('utf8').encode('gbk'))
	out.flush()
	out.close()
