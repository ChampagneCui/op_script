#!/bin/bash

project=$1
commit=$2
com_commit=$3

date=`date "+%Y-%m-%d" `


function download
{
        cd temp/$project
        git checkout rls  >/dev/null 2>&1
        git pull  >/dev/null 2>&1
}

function compare
{
        i=1
        echo ,,,,${project}
        git log --pretty=oneline --pretty="%H,,%ci,,%s" $commit^..$com_commit|grep -v $commit
        while [ $? != 0  ]
        do
                commit=`git log --pretty=oneline --pretty="%P" -n 1 $commit`
                commit=`echo $commit|awk -F ',,' {print $1}`
                git log --pretty=oneline --pretty="%H,,%ci,,%s" $commit^..$com_commit|grep -v $commit
        done
}


download
compare
