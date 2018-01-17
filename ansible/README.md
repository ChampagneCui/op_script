1.dynamic-host.py 可以为ansible提供动态hosts，当然这只是一个测试，脚本可以k写的很复杂，来源可以是csv或者你的cmdb系统  
2.playbook下的init.yml是初始化服务器的脚本（centos6、7全兼容），目前完成的功能如下：  
  a.修改root密码  
  b.贴上管理服务器的ssh公钥  
  c.关闭selinux  
  d.添加来自于管理服务器的入向策略全允许  
  e.zabbix agent部署并且自动改完zabbix server地址（需把role下的zabbix-agent拷贝到/etc/ansible/role下）    
用法：ansible-playbook init.yml --extra-vars "host=Your host group"  
