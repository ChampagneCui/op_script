#!/usr/bin/env python
#coding:utf-8
#用来监控网络，如果有连续两个点高于前一个点30%，则钉钉告警
from __future__ import division
import json
import urllib2
from urllib2 import URLError
import sys
zabbix_addresses=['http://YourZabbixUrl,YourZabbixUsername,YourZabbixPassword']
#increase_point=1
#decrease_point=0.5
point=0.3 #涨跌幅阀值
history_limit=10 #取过去history几个
host_dict={'10001':{'hostname':'H00140','itemid':'140232'},
	   '10002':{'hostname':'H00141','itemid':'140337'},	
	   '10003':{'hostname':'H00134','itemid':'140172'},
	   '10004':{'hostname':'H00135','itemid':'140302'},
	   '10005':{'hostname':'H00325','itemid':'132811'},
	   '10006':{'hostname':'H00326','itemid':'134195'},
	   '10007':{'hostname':'H00327','itemid':'136685'},
	   '10008':{'hostname':'H00328','itemid':'133143'},
}
dingding_base_url='https://oapi.dingtalk.com/robot/send?'
dingding_token='access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
dingding_url=dingding_base_url+dingding_token


class ZabbixTools:
    def __init__(self,address,username,password):
                                                                       
        self.address = address
        self.username = username
        self.password = password
                                                                       
        self.url = '%s/api_jsonrpc.php' % self.address
        self.header = {"Content-Type":"application/json"}
                                                                       
                                                                       
                                                                       
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
            #print response['result']
            self.authID = response['result']
            return self.authID
                                                                           
    def history_get(self,hostid):
        data = json.dumps({
                           "jsonrpc":"2.0",
                           "method":"history.get",
                           "params": {
					"output": "extend",
					"history": 3,
					"hostids": hostid,
					"itemids": host_dict[hostid]['itemid'],
        				"sortfield": "clock",
        				"sortorder": "DESC",
        				"limit": history_limit
                                    },
                           "auth": self.user_login(),
                           "id":1 
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
	    return issues


def if_warning(content,hostid):
	last=int(content[0]["value"])
	sub=int(content[1]["value"])
	old=int(content[2]["value"])
	check_point=int(content[3]["value"])
	if (abs(old-check_point)/old) > point:
		exit()

	print(old,sub,last)
	if (abs(old-sub)/old) > point:
		if (abs(old-last)/old) > point:
			dd("There is a 'Flow surge' or 'Flow reduction' on %s!" %(host_dict[hostid]['hostname']))
	print(abs(old-sub)/old)
	print(abs(old-last)/old)
	

def dd(context):
    con={"msgtype":"text","text":{"content":context}}
    jd=json.dumps(con)
    req=urllib2.Request(dingding_url,jd)
    req.add_header('Content-Type', 'application/json')
    response=urllib2.urlopen(req)
    print(response.read())

                                                                           
if __name__ == "__main__":
    for zabbix_addres in zabbix_addresses:
        address,username,password = zabbix_addres.split(',')
        z = ZabbixTools(address=address, username=username, password=password)
	for hostid in host_dict.keys():
        	content = z.history_get(hostid)
		if_warning(content,hostid)
	
		
    print "Done!"
