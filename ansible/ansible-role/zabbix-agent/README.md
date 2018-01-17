Zabbix-agent Role for Zabbix 3.2
=================

Supported OSes
--------------
- Debian 7 and 8
- Ubuntu 14 and 16
- RHEL / CentOS 6 and 7

for windows, please visit: https://www.zabbix.com/documentation/3.2/manual/appendix/install/windows_agent  

Role Variables
--------------

The variables that can be passed to this role and a brief description about them are as follows.

	# Zabbix server to connect to
	zabbix_agent_server: localhost
	# Zabbix port in the server to connect to
	zabbix_agent_server_port: 10051
	# HostMetadata value in the agent config
	zabbix_agent_metadata: system.uname
	# Prefix to be added to the Hostname value in the agent config
	zabbix_agent_hostname_prefix: ""

How to Install
--------------

```
cd /etc/ansible/roles
git clone git@github.com:irLinja/ansible-zabbix-3.2-agent.git zabbix-agent 
```

Example Playbook
----------------

```
---
- hosts: zabbix-clients
  roles:
       - zabbix-agent
```

How to run
----------

``` 
ansible-playbook zabbix-agent.yml --limit zabbix-clients 
```
