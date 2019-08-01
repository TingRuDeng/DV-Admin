insert into `jperm_menu` ( `code`, `id`, `icon`, `parent_id`, `url`, `name`) values ( 'juser', '1', 'fa-group', null, 'user_admin', '组织管理');
insert into `jperm_menu` ( `code`, `id`, `icon`, `parent_id`, `url`, `name`) values ( 'jperm', '6', 'fa-gears', null, 'role_admin', '系统管理');
insert into `jperm_menu` ( `code`, `id`, `icon`, `parent_id`, `url`, `name`) values ( 'department', '101', null, '1', 'user_group_list', '部门管理');
insert into `jperm_menu` ( `code`, `id`, `icon`, `parent_id`, `url`, `name`) values ( 'employees', '102', null, '1', 'user_list', '员工管理');
insert into `jperm_menu` ( `code`, `id`, `icon`, `parent_id`, `url`, `name`) values ( 'mydetail', '106', null, '1', 'user_detail', '个人信息');
insert into `jperm_menu` ( `code`, `id`, `icon`, `parent_id`, `url`, `name`) values ( 'role', '602', '', '6', 'role_list', '角色管理');
insert into `jperm_menu` ( `code`, `id`, `icon`, `parent_id`, `url`, `name`) values ( 'passwd', '603', null, '6', 'user_passwd_list', '密码管理');

insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '1', '6', '2', '2018-01-25 10:56:53');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '3', '602', '2', '2018-01-25 11:29:17');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '19', '1', '1', '2018-01-28 15:57:50');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '20', '106', '1', '2018-01-28 15:57:50');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '21', '603', '2', '2018-01-30 16:34:58');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '27', '1', '2', '2018-01-31 14:31:00');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '28', '106', '2', '2018-01-31 14:31:00');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '29', '101', '2', '2018-01-31 14:31:00');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '30', '102', '2', '2018-01-31 14:31:37');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '40', '1', '3', '2019-03-05 17:17:43');
insert into `jperm_menu_permission` ( `id`, `menu_id`, `role_id`, `update_time`) values ( '41', '106', '3', '2019-03-05 17:17:43');

insert into `juser_user` ( `wechat`, `group_id`, `coin_addr`, `sex`, `departure_time`, `is_staff`, `uuid`, `parent_id`, `last_login`, `last_name`, `name`, `job`, `id`, `is_active`, `date_joined`, `email`, `mobile`, `portrait_address`, `update_time`, `password`, `first_name`, `is_superuser`, `role_id`, `username`) values ( '', null, null, '', null, '1', null, null, '2019-03-05 17:08:30', '', '', null, '1', '1', '2019-03-05 17:00:42', '', '', null, '2019-03-05 17:00:42', 'pbkdf2_sha256$20000$c3KZMNyWXseg$xxXTVEtqp95DxKGiVhQjOmfffkvWYloix2M36yZNHEQ=', '', '1', '2', 'admin');