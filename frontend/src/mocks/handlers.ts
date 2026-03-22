import { http, HttpResponse } from 'msw'

export const handlers = [
  // OAuth 登录
  http.post('/api/v1/oauth/login/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        expiresIn: 7200,
      },
    })
  }),

  // 登出
  http.post('/api/v1/oauth/logout/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
    })
  }),

  // 获取用户信息
  http.get('/api/v1/oauth/info/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        id: 1,
        username: 'admin',
        name: '管理员',
        avatar: '',
        email: 'admin@example.com',
        phone: '',
        roles: ['admin'],
        permissions: ['*:*:*'],
      },
    })
  }),

  // 获取用户菜单
  http.get('/api/v1/oauth/menus/routes/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: [
        {
          path: '/system',
          name: 'System',
          component: 'Layout',
          children: [
            {
              path: '/system/users',
              name: 'Users',
              component: '/system/users/index',
            },
          ],
        },
      ],
    })
  }),

  // 验证码
  http.get('/api/v1/oauth/captcha/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        uuid: 'mock-uuid-12345',
        image: 'data:image/png;base64,mock-image-data',
      },
    })
  }),

  // 用户列表
  http.get('/api/v1/system/users/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        results: [
          {
            id: 1,
            username: 'admin',
            name: '管理员',
            email: 'admin@example.com',
            status: 1,
          },
        ],
        total: 1,
      },
    })
  }),

  // 用户详情
  http.get('/api/v1/system/users/:id/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        id: 1,
        username: 'admin',
        name: '管理员',
        email: 'admin@example.com',
        status: 1,
      },
    })
  }),

  // 创建用户
  http.post('/api/v1/system/users/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: { id: 2 },
    })
  }),

  // 更新用户
  http.put('/api/v1/system/users/:id/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
    })
  }),

  // 删除用户
  http.delete('/api/v1/system/users/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
    })
  }),

  // 用户下拉选项
  http.get('/api/v1/system/users/options/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: [
        { label: '管理员', value: 1 },
        { label: '普通用户', value: 2 },
      ],
    })
  }),

  // 角色列表
  http.get('/api/v1/system/roles/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        results: [
          { id: 1, name: '管理员', code: 'admin', status: 1 },
        ],
        total: 1,
      },
    })
  }),

  // 角色下拉选项
  http.get('/api/v1/system/roles/options/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: [
        { label: '管理员', value: 1 },
        { label: '普通角色', value: 2 },
      ],
    })
  }),

  // 菜单列表
  http.get('/api/v1/system/menus/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: [
        { id: 1, name: '系统管理', path: '/system', type: 'MENU' },
      ],
    })
  }),

  // 菜单下拉选项
  http.get('/api/v1/system/menus/options/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: [
        { label: '系统管理', value: 1 },
      ],
    })
  }),

  // 部门列表
  http.get('/api/v1/system/departments/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: [
        { id: 1, name: '总部', parentId: null },
      ],
    })
  }),

  // 部门下拉选项
  http.get('/api/v1/system/departments/options/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: [
        { label: '总部', value: 1 },
      ],
    })
  }),

  // 字典列表
  http.get('/api/v1/system/dicts/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        results: [
          { id: 1, name: '用户状态', code: 'user_status' },
        ],
        total: 1,
      },
    })
  }),

  // 字典项列表
  http.get('/api/v1/system/dict-items/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        results: [
          { id: 1, dictId: 1, label: '启用', value: '1' },
          { id: 2, dictId: 1, label: '禁用', value: '0' },
        ],
        total: 2,
      },
    })
  }),

  // 通知列表
  http.get('/api/v1/system/notices/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        results: [
          { id: 1, title: '系统通知', status: 1 },
        ],
        total: 1,
      },
    })
  }),

  // 个人中心 - 获取信息
  http.get('/api/v1/information/profile/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
      data: {
        id: 1,
        username: 'admin',
        name: '管理员',
        email: 'admin@example.com',
      },
    })
  }),

  // 个人中心 - 更新信息
  http.put('/api/v1/information/profile/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
    })
  }),

  // 个人中心 - 修改密码
  http.put('/api/v1/information/change-password/', () => {
    return HttpResponse.json({
      code: 20000,
      msg: 'success',
    })
  }),
]
