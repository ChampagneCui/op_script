#!/bin/env python

import os
import sys
from pyhdfs import HdfsClient

env=sys.argv[1]
env_dir={'dev':'10.x.x.1:50070,10.x.x.2:50070','qa':'20.x.x.1:50070,20.x.x.2:50070'}
directory='/app'
src='/home/jenkins/.jenkins/jobs/%s-jar/workspace/target/' %(env)


def check_appjars(client):
        try:
                a=client.listdir(directory)
                print(a)
        except:
                client.mkdirs(directory)
		print('mkdir %s' %(directory))

def hdfs_put(client):
	for f in os.listdir(src):
		if(os.path.isfile("%s/%s" %(src,f))):
			try:
				client.delete("%s/%s" %(directory,f))
			finally:
				client.copy_from_local("%s/%s" %(src,f),'%s/%s' %(directory,f))	
				print('Copy success!')


if __name__ == '__main__':
	client = HdfsClient(hosts=env_dir[env],user_name='root')
	check_appjars(client)
	hdfs_put(client)

	#document: http://pyhdfs.readthedocs.io/en/latest/pyhdfs.html
