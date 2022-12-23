import re
import random

from pathlib import Path
from typing import Union
from checklib import *
from pwn import remote


class CheckMachine:
    def __init__(self, checker: BaseChecker):
        self.c = checker

    def create_elf(self, r: remote, username: str, password: str, fail_status: Status = Status.MUMBLE):
        r.recvuntil(b'*> ')
        r.sendline(b'1')
        r.recvuntil(b': ')
        r.sendline(username.encode())
        r.recvuntil(b': ')
        r.sendline(password.encode())
        response = r.recvuntil(b'\n\n')
        self.c.assert_in(b'Success', response, 'Unable to register elf' + username + password, fail_status)

    def create_santa(self, r: remote, username: str, password: str, fail_status: Status = Status.MUMBLE):
        r.recvuntil(b'*> ')
        r.sendline(b'2')
        r.recvuntil(b': ')
        r.sendline(username.encode())
        r.recvuntil(b': ')
        r.sendline(password.encode())
        response = r.recvuntil(b'\n\n')
        self.c.assert_in(b'Success', response, 'Unable to register santa', fail_status)

    def create_wish(self, r: remote, elf_username: str, elf_password: str, wish: str, password: str, fail_status: Status = Status.MUMBLE) -> str:
        r.recvuntil(b'*> ')
        r.sendline(b'3')
        r.recvuntil(b': ')
        r.sendline(elf_username.encode())
        r.recvuntil(b': ')
        r.sendline(elf_password.encode())
        response = r.recvuntil((b': ', b'\n\n'))
        self.c.assert_in(elf_username, response.decode(), 'Unable to log in as an elf', fail_status)
        r.sendline(wish.encode())
        r.recvuntil(b': ')
        r.sendline(password.encode())
        response = r.recvuntil(b'\n\n')
        self.c.assert_in(b'Success', response, 'Unable to create a wish', fail_status)
        wish_id = re.findall(r'Your wish id is ([a-zA-Z0-9]+)', response.decode())
        self.c.assert_neq(len(wish_id), 0, 'Unable to get wish id', fail_status)
        return wish_id[0]

    def list_wishes(self, r: remote, santa_username: str, santa_password: str, fail_status: Status = Status.MUMBLE) -> list[str]:
        r.recvuntil(b'> ')
        r.sendline(b'4')
        r.recvuntil(b': ')
        r.sendline(santa_username.encode())
        r.recvuntil(b': ')
        r.sendline(santa_password.encode())
        response = r.recvuntil((b': ', b'\n\n'))
        self.c.assert_in(santa_username, response.decode(), 'Unable to log in as a santa', fail_status)
        wishes = re.findall(r'->  ([a-zA-Z0-9]+)', response.decode())
        return wishes
    
    def take_wish(self, r: remote, santa_username: str, santa_password: str, wish_id: str, wish_password: str, fail_status: Status = Status.MUMBLE) -> tuple[str, str]:
        r.recvuntil(b'*> ')
        r.sendline(b'5')
        r.recvuntil(b': ')
        r.sendline(santa_username.encode())
        r.recvuntil(b': ')
        r.sendline(santa_password.encode())
        response = r.recvuntil((b': ', b'\n\n'))
        self.c.assert_in(santa_username, response.decode(), 'Unable to log in as a santa', fail_status)
        r.sendline(wish_id.encode())
        response = r.recvuntil((b'(y/n) > ', b'\n\n'))
        self.c.assert_in(f'Are you sure that you want to take wish {wish_id}?', response.decode(), 'Unable to configrm taking wish', fail_status)
        r.sendline(b'y')
        r.recvuntil(b': ')
        r.sendline(wish_password.encode())
        response = r.recvuntil(b'\n\n').decode()
        self.c.assert_in("You're a real one!", response, 'Unable to take a wish', fail_status)
        content = re.findall(r'\*\*\* \"([^\n]*)\"', response)
        author = re.findall(r'- by ([^\n]*)', response)
        self.c.assert_neq(len(content), 0, 'Unable to get content from taken wish', fail_status)
        self.c.assert_neq(len(author), 0, 'Unable to get author from taken wish', fail_status)
        return content[0].strip(), author[0].strip()
