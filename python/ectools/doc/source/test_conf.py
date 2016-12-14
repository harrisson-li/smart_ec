import os
import sys

print "current: " + os.path.abspath(os.path.curdir)
sys.path.insert(0, os.path.abspath('../../.'))

from ectools import config

print(config.config.env)
assert config.config.partner == 'Cool'
