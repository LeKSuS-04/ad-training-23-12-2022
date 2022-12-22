#!/usr/bin/env python

import re
import os
import sys
from typing import Union
argv = [c for c in sys.argv]        # https://docs.pwntools.com/en/stable/args.html :)))))))))))
os.environ['PWNLIB_NOTERM'] = '1'   # https://stackoverflow.com/a/67183309/15078906 :)))))))))))

from pwn import remote, PwnlibException, context
from checklib import *

