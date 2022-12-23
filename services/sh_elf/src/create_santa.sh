#!/bin/bash

echo -n "Enter username for santa account: "
read -r username
echo -n "Enter password for santa account: "
read -r password

output=$($psql -t <<EOF
INSERT INTO santas (username,password) VALUES('${username}','$password');
EOF
)

if [[ "$output" == "INSERT 0 1" ]]; then
    echo "Success!"
else
    echo "Something went wrong..."
fi
