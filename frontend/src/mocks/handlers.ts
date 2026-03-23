import { rest } from "msw";

export const handlers = [
  rest.post("/api/v1/oauth/login/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          accessToken: "mock-access-token",
          refreshToken: "mock-refresh-token",
          expiresIn: 7200,
        },
      })
    );
  }),

  rest.post("/api/v1/oauth/logout/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
      })
    );
  }),

  rest.get("/api/v1/oauth/info/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          id: 1,
          username: "admin",
          name: "管理员",
          avatar: "",
          email: "admin@example.com",
          phone: "",
          roles: ["admin"],
          permissions: ["*:*:*"],
        },
      })
    );
  }),

  rest.get("/api/v1/oauth/menus/routes/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: [
          {
            path: "/system",
            name: "System",
            component: "Layout",
            children: [
              {
                path: "/system/users",
                name: "Users",
                component: "/system/users/index",
              },
            ],
          },
        ],
      })
    );
  }),

  rest.get("/api/v1/oauth/captcha/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          uuid: "mock-uuid-12345",
          image: "data:image/png;base64,mock-image-data",
        },
      })
    );
  }),

  rest.get("/api/v1/system/users/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          list: [
            {
              id: 1,
              username: "admin",
              name: "管理员",
              email: "admin@example.com",
              status: 1,
            },
          ],
          total: 1,
        },
      })
    );
  }),

  rest.get("/api/v1/system/users/:id/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          id: 1,
          username: "admin",
          name: "管理员",
          email: "admin@example.com",
          status: 1,
        },
      })
    );
  }),

  rest.post("/api/v1/system/users/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: { id: 2 },
      })
    );
  }),

  rest.put("/api/v1/system/users/:id/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
      })
    );
  }),

  rest.delete("/api/v1/system/users/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
      })
    );
  }),

  rest.get("/api/v1/system/users/options/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: [
          { label: "管理员", value: 1 },
          { label: "普通用户", value: 2 },
        ],
      })
    );
  }),

  rest.get("/api/v1/system/roles/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          list: [{ id: 1, name: "管理员", code: "admin", status: 1 }],
          total: 1,
        },
      })
    );
  }),

  rest.get("/api/v1/system/roles/options/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: [
          { label: "管理员", value: 1 },
          { label: "普通角色", value: 2 },
        ],
      })
    );
  }),

  rest.get("/api/v1/system/menus/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: [{ id: 1, name: "系统管理", path: "/system", type: "MENU" }],
      })
    );
  }),

  rest.get("/api/v1/system/menus/options/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: [{ label: "系统管理", value: 1 }],
      })
    );
  }),

  rest.get("/api/v1/system/departments/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: [{ id: 1, name: "总部", parentId: null }],
      })
    );
  }),

  rest.get("/api/v1/system/departments/options/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: [{ label: "总部", value: 1 }],
      })
    );
  }),

  rest.get("/api/v1/system/dicts/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          list: [{ id: 1, name: "用户状态", code: "user_status" }],
          total: 1,
        },
      })
    );
  }),

  rest.get("/api/v1/system/dict-items/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          list: [
            { id: 1, dictId: 1, label: "启用", value: "1" },
            { id: 2, dictId: 1, label: "禁用", value: "0" },
          ],
          total: 2,
        },
      })
    );
  }),

  rest.get("/api/v1/system/notices/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          list: [{ id: 1, title: "系统通知", status: 1 }],
          total: 1,
        },
      })
    );
  }),

  rest.get("/api/v1/information/profile/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
        data: {
          id: 1,
          username: "admin",
          name: "管理员",
          email: "admin@example.com",
        },
      })
    );
  }),

  rest.put("/api/v1/information/profile/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
      })
    );
  }),

  rest.put("/api/v1/information/change-password/", (_req, res, ctx) => {
    return res(
      ctx.json({
        code: 20000,
        msg: "success",
      })
    );
  }),
];
