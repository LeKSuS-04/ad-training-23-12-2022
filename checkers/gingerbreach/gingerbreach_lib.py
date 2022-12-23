from typing import Any
from checklib import *


PORT = 3000


class CheckMachine:
    @property
    def url(self):
        return f'http://{self.c.host}:{PORT}'

    def __init__(self, checker: BaseChecker):
        self.c = checker
        self.session = self.c.get_initialized_session()

    def login(self, username: str, password: str):
        self.session.headers['Authorization'] = f'Basic {username}:{password}'

    def logout(self):
        self.session.headers.pop('Authorization')

    def me(self, fail_status: Status = Status.MUMBLE) -> None | dict[str, Any]:
        r = self.session.get(f'{self.url}/auth/me')
        self.c.assert_eq(r.status_code, 200, 'Unable to get info about current user', fail_status)
        return r.json().get('user')

    def create(self, username: str, password: str, fail_status: Status = Status.MUMBLE):
        r = self.session.post(f'{self.url}/auth/create', json={
            'username': username,
            'password': password
        })
        self.c.assert_eq(r.status_code, 200, 'Unable to create new user', fail_status)

    def get_user(self, username: str, fail_status: Status = Status.MUMBLE) -> dict[str, Any]:
        r = self.session.get(f'{self.url}/get_user', json={
            'username': username
        })
        self.c.assert_eq(r.status_code, 200, 'Unable to get info about user', fail_status)
        return r.json().get('user')

    def eat_tangerine(self, fail_status: Status = Status.MUMBLE):
        r = self.session.post(f'{self.url}/eat_tangerine')
        self.c.assert_eq(r.status_code, 200, 'Unable to create new user', fail_status)

    def create_post(self, text: str, is_private: bool, fail_status: Status = Status.MUMBLE):
        r = self.session.post(f'{self.url}/create_post', json={
            'text': text,
            'isPrivate': is_private
        })
        self.c.assert_eq(r.status_code, 200, 'Unable to create post', fail_status)
        return r.json().get('post')

    def get_post(self, post_id: str, fail_status: Status = Status.MUMBLE):
        r = self.session.get(f'{self.url}/get_post', json={
            'id': post_id
        })
        self.c.assert_eq(r.status_code, 200, 'Unable to get post', fail_status)
        return r.json().get('post')

    def get_user_posts(self, username: str, fail_status: Status = Status.MUMBLE):
        r = self.session.get(f'{self.url}/get_user_posts', json={
            'username': username
        })
        self.c.assert_eq(r.status_code, 200, 'Unable to get user posts', fail_status)
        return r.json().get('posts')

    def search_posts(self, query: dict, fail_status: Status = Status.MUMBLE):
        r = self.session.get(f'{self.url}/search_posts', json=query)
        self.c.assert_eq(r.status_code, 200, 'Unable to search posts', fail_status)
        return r.json().get('posts')
