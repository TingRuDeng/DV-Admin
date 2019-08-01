###部署说明
1、yum 安装依赖

    yum -y install rpm-build gcc automake autoconf python-devel vim sshpass lrzsz \
    readline-devel openldap-devel gcc-c++ unixODBC-devel.x86_64 xorg-x11-server-Xvfb wkhtmltopdf libattr-devel gpgme-devel libcurl-devel \
    pyliblzma  xz-devel xz

2、pip 安装依赖    
    
    pip install -r install/requirements_vs.txt

3、安装mysql
    
    3.1 centos 7以上系统
        yum -y install mariadb-server mariadb-devel
        systemctl enable mariadb.service
        systemctl start mariadb.service
     
    3.2 centos 7以下系统
        yum -y install mysql-server
        service mysqld start
        chkconfig mysqld on
    
4、安装redis

    yum install redis redis-server
    redis-server /etc/redis.conf

2、修改项目目录Asset下的配置文件jumpserver.conf（视实际情况修改）
    
    [db]
    engine = mysql
    database = dev_test
    host = 127.0.0.1
    user = cmdb_test
    password = 123456
    port = 3306
    
2、在项目目录Asset下依次执行下面命令
    
    find ./ -type d -name "migrations" |xargs rm -rf
    python3 manage.py makemigrations
    python3 manage.py migrate

3、导入初始化数据（数据库用户名密码及库名视实际修改）

    create database coin_server
    mysql -uroot -p coin_server < init_v2.sql

4、开发环境启动
    
    python3 manage.py runserver 0.0.0.0:8000
    
5、登录
    
    http://ip:8000
    默认用户名：admin
    密码：Bb$4.b

    或者使用ldap账号登录