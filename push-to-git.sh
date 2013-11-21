
#!/bin/bash

if [ "$1" == "" ]
then
    echo Please include a comment.
    exit
fi

git add *
git commit -m "$1"
git push -u origin master
