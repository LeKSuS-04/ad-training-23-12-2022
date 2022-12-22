#!/usr/bin/env python

import re
import os
import sys
from typing import Union

argv = [c for c in sys.argv]            # https://docs.pwntools.com/en/stable/args.html :)))))))))))
os.environ['PWNLIB_NOTERM'] = '1'       # https://stackoverflow.com/a/67183309/15078906 :)))))))))))

from pwn import remote, PwnlibException, context
from checklib import *
from christmoji_lib import CheckMachine


PORT = 1337
context.log_level = 'critical'


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 10
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

        password = rnd_password()
        tree_id = self.chm.force_create_tree(r, password)
        
        assert_in(tree_id, self.chm.list_undecorated_trees(r), "Unable to see created tree in undecorated trees")
        
        present = self.chm.generate_present()
        self.chm.add_decorations_to_tree(r, tree_id, present)

        assert_in(present, self.chm.view_presents(r, tree_id, password), "Unable to see present in list of presents")
        self.chm.view_tree(r, tree_id)

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        r = self.get_session()
        password = rnd_password()
        tree_id = self.chm.force_create_tree(r, password)
        self.chm.add_decorations_to_tree(r, tree_id, present=flag)
        self.cquit(Status.OK, tree_id, f'{tree_id}:{password}')

    def get(self, flag_id: str, flag: str, vuln: str):
        r = self.get_session()
        tree_id, password = flag_id.split(':')
        presents = self.chm.view_presents(r, tree_id, password, Status.CORRUPT)
        self.assert_in(flag, presents, 'Unable to get flag', Status.CORRUPT)
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
