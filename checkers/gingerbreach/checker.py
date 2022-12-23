#!/usr/bin/env python

import sys
import random

from checklib import *
from gingerbreach_lib import CheckMachine


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 10
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.chm = CheckMachine(self)

    def check(self):
        username = rnd_username(10)
        password = rnd_password()

        assert_eq(self.chm.me(), None, 'Got user without logging in O_O')

        self.chm.create(username, password)
        self.chm.login(username, password)
        assert_eq(self.chm.me().get('username'), username, 'Unable to log in')

        tangerine_count = random.randint(1, 20)
        for _ in range(tangerine_count):
            self.chm.eat_tangerine()
        assert_eq(self.chm.me().get('tangerinesEaten'), tangerine_count, "Tangerine count doesn't match")
        
        post_text = rnd_string(64)
        pub_post = self.chm.create_post(post_text, False)
        priv_post = self.chm.create_post(post_text, True)
        assert_neq(pub_post, None, 'Unable to create post')
        assert_neq(priv_post, None, 'Unable to create post')

        pub_post_resp = self.chm.get_post(pub_post.get('id'))
        priv_post_resp = self.chm.get_post(priv_post.get('id'))
        assert_eq(post_text, pub_post_resp.get('text'), 'Public post was corrupted')
        assert_eq(post_text, priv_post_resp.get('text'), 'Public post was corrupted')
        
        user_posts = self.chm.get_user_posts(username)
        assert_in(pub_post_resp.get('id'), user_posts, "Unable to find public post in user posts")
        assert_nin(priv_post_resp.get('id'), user_posts, "Found private post in user posts")

        tangerine_posts = self.chm.search_posts({'tangerines_eaten': tangerine_count})
        assert_in(pub_post_resp.get('id'), tangerine_posts, 'Unable to find post by tangerine count')

        self.cquit(Status.OK)


    def put(self, flag_id: str, flag: str, vuln: str):
        username = rnd_username(10)
        password = rnd_password()
        self.chm.create(username, password)
        self.chm.login(username, password)
        
        tangerine_count = random.randint(1, 20)
        for _ in range(tangerine_count):
            self.chm.eat_tangerine()
        
        post = self.chm.create_post(flag, True)
        self.cquit(Status.OK, username, f'{username}:{password}:{post.get("id")}')

    def get(self, flag_id: str, flag: str, vuln: str):
        username, password, post_id = flag_id.split(':')
        self.chm.login(username, password)
        post = self.chm.get_post(post_id, Status.CORRUPT)
        assert_eq(post.get('text'), flag, "Post text corrupted", Status.CORRUPT)
        self.cquit(Status.OK)


if __name__ == '__main__':
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
