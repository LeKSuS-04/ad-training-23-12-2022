#!/bin/bash

echo "You need to log in as an santa first"
echo -n "Enter username: "
read -r username
echo -n "Enter password: "
read -r password

santa_id=$($psql -t <<EOF
SELECT id FROM santas WHERE username='${username}' AND password='${password}';
EOF
)

if [ -z "$santa_id" ]; then
    echo "Santa not found"
    exit
fi

echo "Authenticated as santa $username"

wish_ids=$($psql -t <<EOF
SELECT id FROM wishes WHERE is_taken=false;
EOF
)

echo "Here is a list of wish ids that are yet to be taken:"
while IFS= read -r id; do
    if [ -n "$id" ]; then
        echo "-> $id"
    fi
done <<< "$wish_ids"
