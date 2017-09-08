在web页面点jenkins切分支再点发布太累，命令行解决。支持异步  

#不切分支  
./jenkins_deploy.py rebuild qa-job1,qa-job2,qa-job3  
#qa例行发布  
./jenkins_deploy.py qa qa-job1,qa-job2,qa-job3,qa-job4  
#生产发布  
./jenkins_deploy.py prd prd-job1,prd-job2,prd-job3,prd-job4  

ps:  
我的生产和QA不是同一台jenkins，如果是一台的可以擦除这部分  
