#!/bin/bash -x
RETVAL=0

function incr_err() {
    RETVAL=`expr $RETVAL + 1`
}

OUTPUT=`git grep "patch(" | grep -v "autospec"`
if [ $(echo -n $OUTPUT| wc -l) -eq 0 ]; then
    echo "Autospec check.. DONE"
else
    echo "All mock.patch calls must use autospec=True"
    echo $OUTPUT
    incr_err
fi


exit $RETVAL
