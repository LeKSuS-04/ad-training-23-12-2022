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

echo -n "Enter wish id: "
read -r wish_id

query_result=$($psql -t <<EOF
SELECT owner_id,content,password FROM wishes WHERE id='${wish_id}' AND is_taken=false;
EOF
)

owner_id=$(echo "$query_result" | cut -d "|" -f 1 | sed -e 's/^[ \t]*//')
wish_content=$(echo "$query_result" | cut -d "|" -f 2 | sed -e 's/^[ \t]*//')
wish_password=$(echo "$query_result" | cut -d "|" -f 3 | sed -e 's/^[ \t]*//') 

if [ -z "$wish_content" ]; then
    echo "Wish not found"
    exit
fi

echo "Are you sure that you want to take wish ${wish_id}?"
echo "You'll have to fulfill it!"
echo -n "(y/n) > "
read -r choice

if [[ "$choice" != "y" ]]; then
    echo "Aborting..."
    exit
fi

echo -n "Prove that you're a real Santa... Enter wish password: "
read -r password
if [[ "$wish_password" != "$password" ]]; then
    echo "Wrong password!"
    exit
fi

owner_username=$($psql -t <<EOF
SELECT username FROM elfs WHERE id=${owner_id};
EOF
)
$psql -t <<EOF
UPDATE wishes SET is_taken=true WHERE id='${wish_id}';
EOF

echo "You're a real one!"
echo "*** \"${wish_content}\""
echo "- by ${owner_username}"
echo "Make sure it happens!"
