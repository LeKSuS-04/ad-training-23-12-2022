#!/bin/bash

PROMPT=$(cat <<-EOF

<*-?-*> What do you desire to do? <*-?-*>
1. Create new elf
2. Create new santa
3. Create a wish as elf
4. List wishes as santa
5. Take a wish as santa
6. Exit
*> 
EOF
)

export psql="psql $POSTGRES"

echo "Hello :D"

echo -n "$PROMPT"
read -r choice
until [[ "$choice" == 6 ]]; do
    case "$choice" in
        "1") ./create_elf.sh;;
        "2") ./create_santa.sh;;
        "3") ./create_wish.sh;;
        "4") ./list_wishes.sh;;
        "5") ./take_wish.sh;;
        *) echo "Uhh... I don't understand you..."
    esac
    echo -n "$PROMPT"
    read -r choice
done

echo "Bye :D"
