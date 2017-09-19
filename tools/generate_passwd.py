#!/usr/bin/python
# -*- coding: utf-8 -*-


import string
import random
import sys

#./generate_passwd.py 16
n=sys.argv[1]
letter = string.letters+string.digits
password = random.sample(pass_char,int(n))
print ''.join(password)
