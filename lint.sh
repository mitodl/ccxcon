#!/bin/bash
RETVAL=0

function incr_err() {
    RETVAL=`expr $RETVAL + 1`
}

# check that mock.patch calls use autospec
OUTPUT=`git grep -e "mock\\.patch(" --or -e "\spatch(" | grep -v "autospec"`
if [ "$OUTPUT" = "" ]; then
    echo "Autospec check.. DONE"
else
    echo "All mock.patch calls must use autospec=True"
    echo $OUTPUT
    incr_err
fi

# Ensure auto-generated migrations are renamed.
OUTPUT=`find .  | grep -v tox | grep -E "migrations/.*auto.*py$"`
if [ "$OUTPUT" = "" ]; then
    echo "Migration naming check.. DONE"
else
    echo "You must rename auto migrations to something sensible."
    echo $OUTPUT
    incr_err
fi

exit $RETVAL
