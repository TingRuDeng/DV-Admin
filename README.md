###Django项目模板系统

1.员工及部门管理  
2.角色权限管理

###功能列表

1.首页展示资产及人员统计图表  
2.组织管理（admin用户及组管理员权限）  
    
    2.1. 部门管理  
        
        a. 部门信息录入及修改  
    
    2.2. 员工管理
        
        a. 人员信息录入及修改（人员状态统一为“未激活”，状态的变更只能由后期流程变动）
        
        b. AD域账号脚步批量生成及下载

2、权限管理
    
    4.1 角色管理
        a.角色创建
        b.角色修改
	4.2 角色分配
	    a.员工角色分配
3、用户登录退出（集成AD认证）


###部署说明    
1、yum 安装依赖

    yum -y install git python-pip mysql-devel rpm-build gcc automake autoconf python-devel vim sshpass lrzsz \
    readline-devel openldap-devel gcc-c++ unixODBC-devel.x86_64 xorg-x11-server-Xvfb wkhtmltopdf libattr-devel gpgme-devel libcurl-devel \
    pyliblzma  xz-devel xz

2、pip 安装依赖    
    
    pip install -r install/requirements.txt

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
    python manage.py makemigrations juser webserver jlog jperm
    python manage.py loaddata install/init.json

3、导入初始化数据（数据库用户名密码及库名视实际修改）
    
    create database db_name

    mysql -uroot -p huli_oa < oa_init_v2.sql

4、开发环境启动
    
    python manage.py runserver 0.0.0.0:8000
    
5、登录
    
    http://ip:8000
    默认用户名：admin
    密码：9ol.0p;/
