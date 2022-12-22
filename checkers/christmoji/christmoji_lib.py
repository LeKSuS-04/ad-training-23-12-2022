import re
import random
import sys

from pathlib import Path
from typing import Union
from checklib import *
from pwn import remote

PORT = 1337

class CheckMachine:
    def __init__(self, checker: BaseChecker):
        self.c = checker
        with open(str(Path(__file__).parent / 'wishes.txt'), 'r') as f:
            self.wishes = f.read().split('\n')

    def force_create_tree(self, r: remote, password: str, fail_status: Status = Status.MUMBLE) -> str:
        r.recvuntil(b'> ')
        r.sendline(b'1')
        response = r.recvuntil((b': ', b'\n\n'))
        r.sendline(password.encode())
        response = r.recvuntil(b'\n\n').decode()
        ids = re.findall(r'Done! Your tree id is ([a-zA-Z0-9]+)!', response)
        self.c.assert_neq(len(ids), 0, 'Unable to create tree', fail_status)
        return ids[0]

    def add_decorations_to_tree(self, r: remote, tree_id: str, present: Union[str, None] = None, fail_status: Status = Status.MUMBLE):
        r.recvuntil(b'> ')
        r.sendline(b'2')
        r.recvuntil(b': ')
        r.sendline(tree_id.encode())
        response = r.recvuntil((b'\n\n', b'> '))
        self.c.assert_nin(b'Something went wrong', response, 'Unable to add decorations to tree', fail_status)
        r.sendline(f'{random.randint(1, 5)}'.encode())
        r.recvuntil(b': ')
        if present is None:
            r.sendline(b'no')
            return
        r.sendline(b'y')
        r.recvuntil(b': ')
        r.sendline(present.encode())

    def list_undecorated_trees(self, r: remote, fail_status: Status = Status.MUMBLE) -> list[str]:
        r.recvuntil(b'> ')
        r.sendline(b'3')
        response = r.recvuntil(b'\n\n').decode()
        tree_ids = list(map(str, re.findall(r'\- ([a-zA-Z0-9]+)', response)))
        return tree_ids

    def list_decorated_trees(self, r: remote, fail_status: Status = Status.MUMBLE) -> list[str]:
        r.recvuntil(b'> ')
        r.sendline(b'4')
        response = r.recvuntil(b'\n\n').decode()
        tree_ids = list(map(str, re.findall(r'\- ([a-zA-Z0-9]+)', response)))
        return tree_ids

    def view_tree(self, r: remote, tree_id: str, fail_status: Status = Status.MUMBLE) -> str:
        r.recvuntil(b'> ')
        r.sendline(b'5')
        r.recvuntil(b': ')
        r.sendline(tree_id.encode())
        response = r.recvuntil(b'\n\n').decode()
        self.c.assert_nin('Tree not found', response, 'Unable to view tree', fail_status)
        return response

    def view_presents(self, r: remote, tree_id: str, password: str, fail_status: Status = Status.MUMBLE) -> list[str]:
        r.recvuntil(b'> ')
        r.sendline(b'6')
        r.recvuntil(b': ')
        r.sendline(tree_id.encode())
        r.recvuntil(b': ')
        r.sendline(password.encode())
        response = r.recvuntil(b'\n\n').decode()
        presents = list(map(str, re.findall(r'\- \([^)]*\): ([^\n]+)', response)))
        if len(presents) == 0 and 'There are no present under your tree' not in response:
            self.c.cquit(fail_status, 'Unable to view presents under the tree', f'{tree_id}:{password}')
        return presents

    def generate_present(self) -> str:
        return random.choice(self.wishes)