#!/bin/sh
BP_FILE="xfilip46-thesis-01-chapters.tex"
LAST_MODIFIED=$(stat -c %Y $BP_FILE)

while true
do
    sleep 1;
    if [ "$(stat -c %Y $BP_FILE)" -ne "$LAST_MODIFIED" ]
    then
        LAST_MODIFIED=$(stat -c %Y $BP_FILE);
        make;
        if [ "$?" -eq "0" ]
        then
            echo "Success";
        else
            echo "Failed";
        fi
    fi
done
