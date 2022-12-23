#!/usr/bin/env python

import os
import sys
from typing import Union

argv = [c for c in sys.argv]            # https://docs.pwntools.com/en/stable/args.html :)))))))))))
os.environ['PWNLIB_NOTERM'] = '1'       # https://stackoverflow.com/a/67183309/15078906 :)))))))))))

from pwn import remote, PwnlibException, context
from checklib import *
from sh_elf_lib import CheckMachine


PORT = 5555
context.log_level = 'critical'


class Checker(BaseChecker):
    vulns: int = 4
    timeout: int = 30
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self._pwn_sessions: list[remote] = []
        self.chm = CheckMachine(self)

    def get_session(self) -> remote:
        try:
            r = remote(self.host, PORT)
            r.timeout = Checker.timeout
        except PwnlibException as e:
            cquit(Status.DOWN, "Can't connect", str(e))
        self._pwn_sessions.append(r)
        return r

    def check(self):
        r = self.get_session()

        elf_username = rnd_username(10)
        elf_password = rnd_password()
        self.chm.create_elf(r, elf_username, elf_password)

        santa_username = rnd_username(10)
        santa_password = rnd_password()
        self.chm.create_santa(r, santa_username, santa_password)

        wish = rnd_string(32)
        wish_passwd = rnd_password()
        wish_id = self.chm.create_wish(r, elf_username, elf_password, wish, wish_passwd)

        wish_ids = self.chm.list_wishes(r, santa_username, santa_password)
        self.assert_in(wish_id, wish_ids, 'Unable to see created wish in list of wishes')

        content, author = self.chm.take_wish(r, santa_username, santa_password, wish_id, wish_passwd)
        self.assert_eq(content, wish, 'Wish content is corrupted')
        self.assert_eq(author, elf_username, 'Wish author is corrupted')

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        r = self.get_session()
        
        if vuln in ['1', '2', '3']:
            elf_username = rnd_username(10)
            elf_password = rnd_password()
            wish = rnd_string(32)
            wish_password = rnd_password()
            if vuln == '1':
                wish = flag
            elif vuln == '2':
                elf_username = flag
            elif vuln == '3':
                elf_password = flag
            self.chm.create_elf(r, elf_username, elf_password)
            wish_id = self.chm.create_wish(r, elf_username, elf_password, wish, wish_password)
            self.cquit(Status.OK, wish_id, f'{wish_id}:{wish_password}')
        elif vuln == '4':
            santa_username = rnd_username(10)
            santa_passsword = flag
            self.chm.create_santa(r, santa_username, santa_passsword)
            self.cquit(Status.OK, 'ho-ho-ho!', f'{santa_username}')

    def get(self, flag_id: str, flag: str, vuln: str):
        r = self.get_session()
        
        if vuln in ['1', '2', '3']:
            santa_username = rnd_username(10)
            santa_password = rnd_password()
            self.chm.create_santa(r, santa_username, santa_password)
            wish_id, wish_password = flag_id.split(':')
            content, owner = self.chm.take_wish(r, santa_username, santa_password, wish_id, wish_password, Status.MUMBLE)
            if vuln == '1':
                self.assert_eq(content, flag, 'Corrupted wish content', Status.MUMBLE)
            if vuln == '2':
                self.assert_eq(owner, flag, 'Corrupted wish author', Status.MUMBLE)
            if vuln == '3':
                check_wish = rnd_string(32)
                check_wish_password = rnd_password()
                self.chm.create_wish(r, owner, flag, check_wish, check_wish_password, Status.MUMBLE)
        elif vuln == '4':
            santa_username = flag_id
            santa_password = flag
            self.chm.list_wishes(r, santa_username, santa_password, Status.MUMBLE)

        self.cquit(Status.OK)

    def cquit(self, status: Status, public: str = '', private: Union[str, None] = None):
        for sess in self._pwn_sessions:
            sess.close()
        self._pwn_sessions = []

        super().cquit(status, public, private)


if __name__ == '__main__':
    c = Checker(argv[2])

    try:
        c.action(argv[1], *argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
