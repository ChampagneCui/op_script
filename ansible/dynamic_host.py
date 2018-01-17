#!/usr/bin/env python
import json
 
hostlist = {"db": {"hosts": ["172.11.1.1"]}}
 
print json.dumps(hostlist)
