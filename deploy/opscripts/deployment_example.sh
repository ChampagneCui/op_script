#!/bin/bash

JOB_NAME=$2
PORT=$4

source /etc/profile
file=$3
TOMCAT_HOME="/app/tomcat-$PORT"
RETRY_COUNT=3
RETRY_TIME=30
DEPLOY_HOME='/opt/deploy/install'
WORK_HOME="/app/tomcat-$PORT/webapps/"
TOMCAT_USER="tomcat"
TOMCAT_PASS="tomcat"


if [ ! $WORK_HOME ];then
        echo "WORK_HOME is null!"
        exit 1
fi


#check&clean_backup_part
function clean_backup
{
        cd $DEPLOY_HOME;
        ls -lt|grep $JOB_NAME| awk '{if(NR>5){print "rm " $9}}'|sh
}

#start_part
function start
{
        start_tomcat
        for ((i=1; i<=$RETRY_COUNT; i++));
        do
                start_check
                if [ $? -eq 0 ]
                then
                        echo "start check success"
                        break
                else
                        if [ $i -eq $RETRY_COUNT ]
                        then
                                echo "start check failed"
                                exit 1
                                #exit 0
                        else
                                sleep $RETRY_TIME
                                continue
                        fi
                fi
        done
}

function start_tomcat
{
        cd $TOMCAT_HOME;
        nohup bin/startup.sh
}

#stop part
function stop
{
        for ((i=1; i<=$RETRY_COUNT; i++))
        do
                stop_tomcat
                stop_check
                if [ $? -eq 0 ]
                then
                        echo "stop check success"
                        break
                else
                        if [ $i -eq $RETRY_COUNT ]
                        then
                                echo "stop check failed"
                                exit 1
                        else
                                sleep $RETRY_TIME
                                continue
                        fi
                fi
        done
}

function stop_tomcat
{
        cd $TOMCAT_HOME;
        bin/shutdown.sh -force;
}

#clean old files
function clean
{
        cd $WORK_HOME;
        ls |grep -v manager |xargs rm -rf
        #rm -fr $WORK_HOME/*
}

#check part
function check
{
        start_check
        if [ $? -eq 0 ]
        then
                echo "start check success"
        else
                echo "start check failed"
                #return 1
                exit 1
        fi
}

function start_check
{
        project_status=`tomcat-manager --user=$TOMCAT_USER --password=$TOMCAT_PASS http://127.0.0.1:${PORT}/manager/text list |grep $JOB_NAME|awk '{print $2}'`

        if [ "$project_status" == "running" ]
        then
                return 0
        else
                return 1
        fi

}


function stop_check
{
	tomcat_count=`netstat -tln|grep -w "$PORT"|wc -l`

        if [ "$tomcat_count" == "0" ]
        then
                return 0
        else
                return 1
        fi
}


#sync part
function sync
{
        rsync -avzP $DEPLOY_HOME/$file $WORK_HOME/${JOB_NAME}.war
}


case $1 in
        start)
                start
        ;;
        stop)
                stop
        ;;
        check)
                check
        ;;
        sync)
                sync
        ;;
        restart)
                stop
                start
        ;;
        all)
                clean_backup
                stop
                clean
                sync
                start
        ;;
        *)
                echo "invalid param" ; echo -e "Usage: sh $0 start|stop|sync|check|all|restart"
                exit 1
        ;;
esac

exit 0
