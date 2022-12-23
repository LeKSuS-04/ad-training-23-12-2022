#!/bin/bash

echo "You need to log in as an elf first"
echo -n "Enter username: "
read -r username
echo -n "Enter password: "
read -r password

elf_id=$($psql -t <<EOF
SELECT id FROM elfs WHERE username='${username}' AND password='${password}';
EOF
)

if [ -z "$elf_id" ]; then
    echo "Elf not found"
    exit
fi

echo "Authenticated as elf $username"

echo -n "Make a wish: "
read -r content
echo -n "Enter password for your wish: "
read -r password

random_id=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 32 ; echo '')
output=$($psql -t <<EOF
INSERT INTO wishes (id,owner_id,content,password,is_taken)
     VALUES ('${random_id}',${elf_id},'${content}','${password}',false);
EOF
)

if [[ "$output" == "INSERT 0 1" ]]; then
    echo "Success! Your wish id is ${random_id}"
else
    echo "Something went wrong..."
fi
