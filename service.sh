#!/bin/bash

webserver_dir=

base_dir=$(dirname $0)
webserver_dir=${webserver_dir:-$base_dir}
export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

if [ -f ${webserver_dir}/install/functions ];then
    . ${webserver_dir}/install/functions
elif [ -f /etc/init.d/functions ];then
    . /etc/init.d/functions
else
    echo "No functions script found in [./functions, ./install/functions, /etc/init.d/functions]"
    exit 1
fi

PROC_NAME="webserver"
lockfile=/var/lock/subsys/${PROC_NAME}

start() {
        if [ $(whoami) != 'root' ];then
            echo "Sorry, JMS must be run as root"
            exit 1
        fi
    
        jump_start=$"Starting ${PROC_NAME} service:"
        if [ -f $lockfile ];then
             echo -n "webserver is running..."
             success "$jump_start"
             echo
        else
            daemon python $webserver_dir/manage.py crontab add &>> /var/log/webserver.log 2>&1
#            daemon python $webserver_dir/run_server.py &> /dev/null 2>&1 &
            daemon python $webserver_dir/run_server.py &>> /opt/Assets/logs/huli_oa.log 2>&1 &
            sleep 1
            echo -n "$jump_start"
            ps axu | grep 'run_server' | grep -v 'grep' &> /dev/null
            if [ $? == '0' ];then
                success "$jump_start"
                if [ ! -e $lockfile ]; then
                    lockfile_dir=`dirname $lockfile`
                    mkdir -pv $lockfile_dir
                fi
                touch "$lockfile"
                echo
            else
                failure "$jump_start"
                echo
            fi
        fi
}


stop() {
    echo -n $"Stopping ${PROC_NAME} service:"
    daemon python $webserver_dir/manage.py crontab remove &>> /var/log/webserver.log 2>&1
    ps aux | grep -E 'run_server.py' | grep -v grep | awk '{print $2}' | xargs kill -9 &> /dev/null
    ret=$?
    if [ $ret -eq 0 ]; then
        echo_success
        echo
        rm -f "$lockfile"
    else
        echo_failure
        echo
        rm -f "$lockfile"
    fi

}

status(){
    ps axu | grep 'run_server' | grep -v 'grep' &> /dev/null
    if [ $? == '0' ];then
        echo -n "webserver is running..."
        success
        touch "$lockfile"
        echo
    else
        echo -n "webserver is not running."
        failure
        echo
    fi
}



restart(){
    stop
    start
}

# See how we were called.
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;

  restart)
        restart
        ;;

  status)
        status
        ;;
  *)
        echo $"Usage: $0 {start|stop|restart|status}"
        exit 2
esac
