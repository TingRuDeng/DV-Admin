###部署说明
1、yum 安装依赖

    yum -y install git python-pip mysql-devel rpm-build gcc automake autoconf python-devel vim sshpass lrzsz \
    readline-devel openldap-devel gcc-c++ unixODBC-devel.x86_64 xorg-x11-server-Xvfb wkhtmltopdf libattr-devel gpgme-devel libcurl-devel \
    pyliblzma  xz-devel xz

2、pip 安装依赖

    pip3.6 install -r install/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

3、安装mysql

    3.1 centos 7以上系统
        yum -y install mariadb-server mariadb-devel
        systemctl enable mariadb.service
        systemctl start mariadb.service

    3.2 centos 7以下系统
        yum -y install mysql-server
        service mysqld start
        chkconfig mysqld on

4、安装redis（可选）

    yum install redis redis-server
    redis-server /etc/redis.conf

2、修改项目目录Asset下的配置文件webserver.conf（视实际情况修改）

    [db]
    engine = mysql
    database = db_name
    host = 127.0.0.1
    user = db_user
    password = db_passwd
    port = 3306

2、在项目目录Asset下依次执行下面命令

    find ./ -type d -name "migrations" |xargs rm -rf
    python3.6 manage.py makemigrations juser webserver jlog jperm
    python3.6 manage.py migrate

3、导入初始化数据（数据库用户名密码及库名视实际修改）

    python3.6 manage.py loaddata install/init.json

4、开发环境启动（BD-System项目根目录下执行）

    python3.6 manage.py runserver 0.0.0.0:8000
    celery -A webserver worker --loglevel=debug -B -s celery-schedue.db -Q celery -n celery

5、登录

    http://ip:8000
    默认用户名：admin
    密码：9ol.0p;/
