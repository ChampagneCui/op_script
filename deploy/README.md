此脚本可以结合jenkins发布：
Project="YourProjectHere"
Port="808x" #8080,8081....
old_war="$Project*.war"
path=`find ./ -name $old_war`
md5=`md5sum $path|awk '{print $1}'`
new_war="$Project-${md5}.war"
mv $path target/$new_war
ansible $env-$Project  -m copy -a "src=target/$new_war dest=/opt/deploy/install/"
ansible $env-$Project  -m script -a "/opt/deploy/opscripts/deployment_example.sh all $new_war $Project $Port"
配合上jenkins可以做到编译、分发、替换、重启、检测、回滚一体，且新项目添加时只需更改project、port变量，再改下ansible hosts
