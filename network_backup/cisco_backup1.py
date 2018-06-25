#!/usr/bin/env python
# coding:utf-8

import sys, time

reload(sys)
sys.setdefaultencoding('utf8')
import configparser
import paramiko
import threading
import telnetlib
from datetime import date, timedelta, datetime

day = 1
brand_cmd = {'cisco': ['terminal length 0', 'show running-config'], 'fortinet': ['show full-configuration'],
             'huawei': ['screen-length 0 temporary', 'display current-configuration']}

file_path = './iplist.txt'
config = configparser.ConfigParser()

dt = datetime.now()
time1 = dt.strftime('%Y-%m-%d-%H-%M-%S')
time2 = (date.today() - timedelta(day)).strftime('%Y-%m-%d')


def telnet(ip, username, password, hostname, port, cmd_list,enable,en_pwd):
	finish = '>'
	# 连接Telnet服务器
	tn = telnetlib.Telnet(ip, port=int(port), timeout=3)
	# 输入登录用户名
	tn.read_until(b'Username:')
	tn.write(username.encode('ascii') + '\n')
	# 输入登录密码
	tn.read_until(b'Password: ')
	tn.write(password.encode('ascii') + '\n')
	# 登录完毕后执行命令
	tn.read_until(finish)
	if enable == 'yes':
		tn.write('enable'.encode('ascii')+'\n')
		time.sleep(.1)
		tn.write(en_pwd.encode('ascii') + '\n')
		time.sleep(.1)
	for command in cmd_list:
		tn.write('%s\n' % command.encode('ascii'))
	# 执行完毕后，终止Telnet连接（或输入exit退出）
	#tn.read_until(finish)
	time.sleep(8)
	result = tn.read_very_eager()
	tn.close()  # tn.write('exit\n')
	print('done',result)
	filename = hostname + '-' + time1 + '.' + 'conf'
	with open(filename, 'w') as ff:
		ff.write(result)


def ssh2(ip, username, passwd, hostname, port, cmd_list, enable, en_pwd):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(ip, int(port), username, passwd)
		ssh_shell = ssh.invoke_shell()
		if enable == 'yes':
			ssh_shell.send('enable\n')
			time.sleep(1)
			ssh_shell.send(en_pwd + '\n')
			time.sleep(1)
		for cmd in cmd_list:
			ssh_shell.send(cmd + '\n')
			time.sleep(1)
		result = ssh_shell.recv(65535)
		print('%s\tok\n' % (ip))
		ssh.close()
		filename = hostname + '-' + time1 + '.' + 'conf'
		with open(filename, 'w') as ff:
			ff.write(result)
	except (IOError, ZeroDivisionError) as e:
		print('%s\tError\n:%s' % (ip, e))


if __name__ == "__main__":
	threads = []
	config.read(file_path)
	print('Begin ...')
	for item in config.sections():
		hostname = config.get(item, 'name')
		ip = config.get(item, 'ip')
		port = config.get(item, 'port')
		username = config.get(item, 'user')
		passwd = config.get(item, 'password')
		brand = config.get(item, 'brand')
		protocol = config.get(item, 'protocol')
		cmd_list = brand_cmd[brand]
		enable = config.get(item, 'enable')
		if enable == 'yes':
			en_pwd = config.get(item, 'en_pwd')
		else:
			en_pwd = ''

		if protocol == 'ssh2':
			job = threading.Thread(target=ssh2, args=(ip,username,passwd, hostname, port,cmd_list,enable, en_pwd))
		else:
			job = threading.Thread(target=telnet, args=(ip, username, passwd, hostname, port, cmd_list,enable, en_pwd))
			job.start()
