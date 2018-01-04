#!/usr/bin/env python
# coding:utf-8

import paramiko
import threading
import datetime

time1=datetime.datetime.now()
time2=time1.strftime('%Y-%m-%d')
file_path='./iplist.txt'
port=22

def ssh2(ip,username,passwd,cmd):
	try:
		ssh=paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(ip,port,username,passwd,timeout=5)
		for m in cmd:
			stdin,stdout,stderr=ssh.exec_command(m)
			out=stdout.readlines()
			result=''
			for o in out:
				result+=o
		print('%s\tok\n' %(ip))
		ssh.close()
		filename=ip+'-'+time2+'.'+'conf'
		with open(filename, 'w') as ff:
			ff.write(result)
	except:
		print('%s\tError\n' %(ip))

if __name__=="__main__":
	threads=[]
	print('Begin ...')
	with open(file_path) as f:
		iplist=f.readlines()
		for line in iplist:
			x=line.strip('\n')
			y=x.split(' ')
			ip=y[0]
			username=y[1]
			passwd=y[2]
			cmd=['ls -al']
			a=threading.Thread(target=ssh2,args=(ip,username,passwd,cmd))
			a.start()
