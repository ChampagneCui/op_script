cd /home/admin/gitlab  
python gitlab.py -t unprotect_branch -p $project -f $branch  
python gitlab.py -t delete_branch -p $project -b $branch  
python gitlab.py -t create_branch -p $project -b $branch -f $from  
python gitlab.py -t protect_branch -p $project -f $branch  
也是结合jenkins，传参数使用，集成了分支解保护、删分支、拷贝分支、分支重新保护功能  
gitlab是靠项目id来识别项目的 ，所以先要把项目名查询到id  
  
ps:其实脚本可以合并为一个的，懒。。。  
