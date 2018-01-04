#!/usr/bin/env python
# coding:utf-8
# 标准的zabbix监控报警
import json
import urllib2
from urllib2 import URLError
import sys

zabbix_addresses = ['http://x.x.x.x/zabbix/,username,password']
dingding_base_url = 'https://oapi.dingtalk.com/robot/send?'
dingding_token = 'access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
dingding_url = dingding_base_url + dingding_token
block_key = []  # 关键字过滤
priority_level = -1  # 从几级开始告警

class ZabbixTools:
	def __init__(self, address, username, password):

		self.address = address
		self.username = username
		self.password = password

		self.url = '%s/api_jsonrpc.php' % self.address
		self.header = {"Content-Type": "application/json"}

	def user_login(self):
		data = json.dumps({
			"jsonrpc": "2.0",
			"method": "user.login",
			"params": {
				"user": self.username,
				"password": self.password
			},
			"id": 0
		})

		request = urllib2.Request(self.url, data)
		for key in self.header:
			request.add_header(key, self.header[key])

		try:
			result = urllib2.urlopen(request)
		except URLError as e:
			print "Auth Failed, please Check your name and password:", e.code
		else:
			response = json.loads(result.read())
			result.close()
			# print response['result']
			self.authID = response['result']
			return self.authID

	def trigger_get(self):
		data = json.dumps({
			"jsonrpc": "2.0",
			"method": "trigger.get",
			"params": {
				"output": [
					"triggerid",
					"description",
					"priority",
				],
				"filter": {
					"value": 1
				},
				"active": 0,
				"withUnacknowledgedEvents":0,
				"expandData": "hostname",
				"sortfield": "priority",
				"sortorder": "DESC"
			},
			"auth": self.user_login(),
			"id": 1
		})

		request = urllib2.Request(self.url, data)
		for key in self.header:
			request.add_header(key, self.header[key])

		try:
			result = urllib2.urlopen(request)
		except URLError as e:
			print "Error as ", e
		else:
			response = json.loads(result.read())
			result.close()
			issues = response['result']
			content = ''
			if issues:
				for line in issues:
					priority = line['priority']
					if (int(priority) <= priority_level):  # 设置什么级别以上才告警
						continue
					triggerid = line['triggerid']
					host = self.host_get(triggerid)
					for i in block_key:
						if i in line['description']:
							break
					else:
						content = content + "%s:%s\r\n" % (host, line['description'])
			return content

	def host_get(self, triggerid):
		data = json.dumps({
			"jsonrpc": "2.0",
			"method": "host.get",
			"params": {
				"triggerids": triggerid
			},
			"auth": self.user_login(),
			"id": 1
		})

		request = urllib2.Request(self.url, data)
		for key in self.header:
			request.add_header(key, self.header[key])

		try:
			result = urllib2.urlopen(request)
		except URLError as e:
			print "Error as ", e
		else:
			response = json.loads(result.read())
			result.close()
			issues = response['result']
			host = issues[0]['host']
			hostid = issues[0]['hostid']
			ip=self.host_ip_get(hostid)
			host=host+"("+ip+")"
			description = issues[0]['description']
			#print(description)
			return host

	def host_ip_get(self, hostid):
		data = json.dumps({
			"jsonrpc": "2.0",
			"method": "hostinterface.get",
			"params": {
				"output": "extend",
				"hostids": hostid
			},
			"auth": self.user_login(),
			"id": 1
		})

		request = urllib2.Request(self.url, data)
		for key in self.header:
			request.add_header(key, self.header[key])

		try:
			result = urllib2.urlopen(request)
		except URLError as e:
			print "Error as ", e
		else:
			response = json.loads(result.read())
			result.close()
			issues = response['result']
			ip = issues[0]['ip']
			return ip

	def host_description_updtae(self, hostname, description):
		hostid = self.host_search(hostname)
		data = json.dumps({
			"jsonrpc": "2.0",
			"method": "host.update",
			"params": {
				"hostid": hostid,
				"description": description
			},
			"auth": self.user_login(),
			"id": 1
		})

		request = urllib2.Request(self.url, data)
		for key in self.header:
			request.add_header(key, self.header[key])

		try:
			result = urllib2.urlopen(request)
		except URLError as e:
			print "Error as ", e
		else:
			result.close()


	def host_search(self,hostname):
		data = json.dumps({
			"jsonrpc": "2.0",
			"method": "host.get",
			"params": {
				"filter": {
					"host": [
						hostname,
					]
				}
			},
			"auth": self.user_login(),
			"id": 1
		})

		request = urllib2.Request(self.url, data)
		for key in self.header:
			request.add_header(key, self.header[key])

		try:
			result = urllib2.urlopen(request)
		except URLError as e:
			print "Error as ", e
		else:
			response = json.loads(result.read())
			result.close()
			issues = response['result']
			hostid = issues[0]['hostid']
			host_des = issues[0]['description']
			print(host_des)
			return hostid



def dd(context):
	con = {"msgtype": "text", "text": {"content": context}}
	jd = json.dumps(con)
	req = urllib2.Request(dingding_url, jd)
	req.add_header('Content-Type', 'application/json')
	response = urllib2.urlopen(req)
	print(response.read())

def main():
	for zabbix_addres in zabbix_addresses:
		address, username, password = zabbix_addres.split(',')
		z = ZabbixTools(address=address, username=username, password=password)
		content = z.trigger_get()
		# print(content)
		if content != '':
			print(content)
		print "Done!"


if __name__ == "__main__":
	main()
	# for zabbix_addres in zabbix_addresses:
	# 	address, username, password = zabbix_addres.split(',')
	# 	z = ZabbixTools(address=address, username=username, password=password)
	# des = z.host_search('xxxxxx')
	# print(des)


