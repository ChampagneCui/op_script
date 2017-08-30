#!/bin/bash

project=$1
branch=$2
Commit_Id=$3
ip='x.x.x.x'
port=29418

##cherry-pick
git clone  -b $branch ssh://jenkins-build@${ip}:${port}/Cloud/$project
cd $project
gitdir=$(git rev-parse --git-dir); scp -p -P $port jenkins-build@${ip}:hooks/commit-msg ${gitdir}/hooks/
git cherry-pick $Commit_Id
git push origin HEAD:refs/for/$branch

#查找新commit号
new_commit=`git rev-parse HEAD`

###review
ssh -p $port admin@$ip gerrit review --verified +1 --code-review +2 --submit --project Cloud/$project  $new_commit
