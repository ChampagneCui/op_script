#!/usr/bin/python
# -*- coding: utf-8 -*-


import string
import random
import sys

#./generate_passwd.py 16
n=sys.argv[1]
pass_char = string.letters+string.digits
pass_word = random.sample(pass_char,int(n))
print ''.join(pass_word)
