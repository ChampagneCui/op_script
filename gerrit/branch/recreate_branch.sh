#!/bin/bash
user="xxxxx"
token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
url="http://Your gerrit url"

curl  --digest --user ${username}:${token} -X DELETE ${url}/a/projects/$1/branches/$3


sleep 5 
  
curl  --digest --user ${username}:${token}  $url/a/projects/$1/branches/$2 > $2.txt
  
sed -i '1d' $2.txt
sed -i '2d' $2.txt
sed -i '3d' $2.txt
sed -i 's/,//g' $2.txt
  
curl  --digest --user ${username}:${token} -X PUT -d@$2.txt --header "Content-Type: application/json;charset=UTF-8" $url/a/projects/$1/branches/$3
