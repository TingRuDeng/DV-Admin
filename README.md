###公司资产管理及员工管理（准OA系统）

1.员工及部门管理  
2.资产管理  
3.角色权限管理

###功能列表

1.首页展示资产及人员统计图表  
2.组织管理（admin用户及组管理员权限）  
    
    2.1. 部门管理  
        
        a. 部门信息录入及修改  
    
    2.2. 员工管理
        
        a. 人员信息录入及修改（人员状态统一为“未激活”，状态的变更只能由后期流程变动）
        
        b. AD域账号脚步批量生成及下载
3、资产管理
    
    3.1 资产列表（仅查看登录账户自身信息）
        a.增加分页
        b.支持类型筛选
        c.支持模糊搜索
        d.点击使用者的名字，跳转到个人资产详细页
        e.资产详情页-设备信息详情
            设备维修和升级记录
            设备历史使用轨迹
	3.2 资产类型管理（admin用户权限）
        a.资产类型录入及修改
        b.资产类别列表展示（包括单个资产类型采购总数）
	3.3 资产管理（admin用户权限）
        a.资产录入及修改
        b.资产配发：配发给员工后，记录日志，并变更员工状态为在职
        c.资产维修及报废，记录日志
        d.资产详细单打印（自动填充表单相关字段）
        e.点击资产财务ID，跳转资产详情页，展示资产详细详细、所有者配发详细、资产配发历史记录
4、权限管理
    
    4.1 角色管理
        a.角色创建
        b.角色修改
	4.2 角色分配
	    a.员工角色分配
5、用户登录退出（集成AD认证）


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
    database = huli_oa
    host = 127.0.0.1
    user = cmdb_test
    password = 123456
    port = 3306
    
2、在项目目录Asset下依次执行下面命令
    
    find ./ -type d -name "migrations" |xargs rm -rf
    python2.7 manage.py makemigrations juser webserver jlog jperm
    python2.7 manage.py migrate

3、导入初始化数据（数据库用户名密码及库名视实际修改）
    
    create database huli_oa

    mysql -uroot -p huli_oa < oa_init_v2.sql
    
4、创建超级管理员（自行填写相关详细）
    
    python manage.py createsuperuser 
    mysql -uroot -p -c "use huli_oa;update juser_user set role_id=2;"
    
5、开发环境启动
    
    python manage.py runserver 0.0.0.0:8000
    
6、登录
    
    http://ip:8000
    默认用户名：admin
    密码：9ol.0p;/

7、接口说明

    1、批量上传员工自有信息接口
        url地址：/juser/userprivate/upload/
        请求方式：post
        请求参数：
            birthday： 生日日期导入文件
            workday:  工作日期导入文件
    2、年假生成接口
        url地址：/juser/userprivate/work_age/
        请求方式：post
        请求参数：
            now_time：截止时间，不加则默认为当前时间
        生成文件地址：/opt/Assets/static/files/excels/work_age.csv    
    3、员工团建费批量导出
        文件生成地址：/opt/Assets/static/files/excels/jact_*.csv    
    