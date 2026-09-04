import {
  expect,
  test,
  type APIRequestContext,
  type APIResponse,
  type Page,
  type Response,
} from "@playwright/test";

const backendName = requireEnv("REAL_BACKEND_NAME");
const username = requireEnv("REAL_BACKEND_USERNAME");
const password = requireEnv("REAL_BACKEND_PASSWORD");
const noticeTitle = requireEnv("REAL_BACKEND_NOTICE_TITLE");
const noticeContent = requireEnv("REAL_BACKEND_NOTICE_CONTENT");
const rbacUsername = requireEnv("REAL_BACKEND_RBAC_USERNAME");
const rbacPassword = requireEnv("REAL_BACKEND_RBAC_PASSWORD");
const rbacRoleId = requireIntegerEnv("REAL_BACKEND_RBAC_ROLE_ID");
const rbacBasePermissionIds = requireIntegerListEnv("REAL_BACKEND_RBAC_BASE_PERMISSION_IDS");
const rbacGrantedPermissionIds = requireIntegerListEnv("REAL_BACKEND_RBAC_GRANTED_PERMISSION_IDS");
const lifecycleRoleName = requireEnv("REAL_BACKEND_LIFECYCLE_ROLE_NAME");
const lifecycleDeptName = requireEnv("REAL_BACKEND_LIFECYCLE_DEPT_NAME");
const updatedName = `${backendName} E2E 用户`;
const lifecycleUsername = `${backendName.toLowerCase()}_lifecycle`;
const lifecycleInitialName = `${backendName} 生命周期用户`;
const lifecycleUpdatedName = `${backendName} 生命周期已更新`;
const lifecyclePassword = "LifecyclePass456";
const apiBasePath = "/dev-api/api/v1";
const accessTokenStorageKey = "vea:auth:access_token";
const menuCatalogRouteName = "RuntimeContract";
const menuWriteRouteName = "RuntimeMenuWriteContract";
const menuWriteRoutePath = "menu-write-contract";
const menuWriteInitialName = `${backendName} 菜单写入`;
const menuWriteUpdatedName = `${backendName} 菜单已更新`;
const menuWritePermissionName = `${backendName} 用户查询权限`;

interface MenuTreeItem {
  id: number | string;
  name: string;
  routeName?: string;
  routePath?: string;
  component?: string;
  perm?: string;
  type?: string;
  parentId?: number | string | null;
  children?: MenuTreeItem[];
}

interface UploadedFileInfo {
  name: string;
  url: string;
  path: string;
}

interface UserPageItem {
  id: number | string;
  username: string;
  name?: string;
  isActive?: number;
}

interface UserPageResult {
  list: UserPageItem[];
  total: number;
}

test.describe(`前端连接真实 ${backendName} 后端`, () => {
  test("完成个人中心、用户管理和通知公告代表页闭环", async ({ page }) => {
    const failedApiResponses = collectFailedApiResponses(page);

    await page.goto("/login?redirect=%2Fprofile");
    await page.getByLabel("用户名").fill(username);
    await page.getByLabel("密码").fill(password);

    const loginBootstrap = Promise.all([
      waitForApiResponse(page, "/api/v1/oauth/login/", "POST"),
      waitForApiResponse(page, "/api/v1/oauth/info/", "GET"),
      waitForApiResponse(page, "/api/v1/oauth/menus/routes/", "GET"),
      waitForApiResponse(page, "/api/v1/information/profile/", "GET"),
    ]);
    await page.getByRole("button", { name: /登\s*录|Login/i }).click();
    await loginBootstrap;

    await expect(page).toHaveURL(/\/profile$/);
    await expect(page.locator(".user-profile__name")).toHaveText(username);
    await expect(page.locator(".ff-profile-user__display-name")).toBeVisible();

    await page.locator(".ff-profile-user__edit").click();
    const profileDialog = page.getByRole("dialog", { name: "账号资料" });
    await profileDialog.locator("input").first().fill(updatedName);
    const updateProfileResponse = waitForApiResponse(page, "/api/v1/information/profile/", "PUT");
    await profileDialog.getByRole("button", { name: /确\s*定/ }).click();
    await updateProfileResponse;
    await expect(page.getByText("账号资料修改成功")).toBeVisible();
    await expect(page.locator(".ff-profile-user__display-name")).toHaveText(updatedName);

    const avatarResponse = waitForApiResponse(page, "/api/v1/information/change-avatar/", "POST");
    await page.locator('.ff-profile-user input[type="file"]').setInputFiles({
      name: "playwright-avatar.gif",
      mimeType: "image/gif",
      buffer: Buffer.from("R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=", "base64"),
    });
    await avatarResponse;
    const avatarImage = page.locator(".ff-profile-user__avatar img");
    await expect(avatarImage).toHaveAttribute("src", /\/media\/avatar\//);
    await expect
      .poll(() => avatarImage.evaluate((image: HTMLImageElement) => image.naturalWidth))
      .toBeGreaterThan(0);

    await page.goto("/my-notice");
    const noticeRow = page.locator(".el-table__row", { hasText: noticeTitle });
    await expect(noticeRow).toBeVisible();
    await noticeRow.getByRole("button", { name: "查看" }).click();
    const noticeDialog = page.getByRole("dialog", { name: noticeTitle });
    await expect(noticeDialog).toContainText(noticeContent);
    await page.keyboard.press("Escape");
    await expect(noticeDialog).toBeHidden();

    await page.reload();
    await expect(page.locator(".el-table__row", { hasText: noticeTitle })).toContainText("已读");

    const userPageResponse = waitForApiResponse(page, "/api/v1/system/users/", "GET");
    await page.goto("/runtime-contract/user");
    await userPageResponse;
    await expect(page).toHaveURL(/\/runtime-contract\/user$/);
    const userTable = page.locator(".ff-user-page .ff-table");
    await expect(userTable.getByText(username, { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "新增用户" })).toBeVisible();
    await expect(page.getByRole("button", { name: "导入用户" })).toBeVisible();
    await expect(page.getByRole("button", { name: "导出用户" })).toBeVisible();
    await page.getByRole("button", { name: "新增用户" }).click();
    const userDrawer = page.locator(".el-drawer", { hasText: "新增用户" });
    await expect(userDrawer).toBeVisible();
    await userDrawer.getByRole("button", { name: /取\s*消/ }).click();

    const noticePageResponse = waitForApiResponse(page, "/api/v1/system/notices/page", "GET");
    await page.locator(".layout__sidebar .el-menu-item", { hasText: "通知公告" }).click();
    await noticePageResponse;
    await expect(page).toHaveURL(/\/runtime-contract\/notices$/);
    const managementRow = page.locator(".ff-notice-page .el-table__row", {
      hasText: noticeTitle,
    });
    await expect(managementRow).toContainText("已发布");
    await expect(managementRow.getByRole("button", { name: "撤回" })).toBeVisible();
    await managementRow.getByRole("button", { name: "查看" }).click();
    const managementDialog = page.locator(".ff-notice-detail-dialog");
    await expect(managementDialog).toContainText(noticeContent);
    await managementDialog.getByRole("button", { name: "关闭通知详情" }).click();

    await page.getByRole("button", { name: "新增通知" }).click();
    const noticeDrawer = page.locator(".el-drawer", { hasText: "新增公告" });
    await expect(noticeDrawer).toBeVisible();
    await noticeDrawer.getByRole("button", { name: /取\s*消/ }).click();
    expect(failedApiResponses).toEqual([]);
  });

  test("用户创建、编辑、密码重置、禁用和删除形成真实闭环", async ({ browser, page }) => {
    const failedApiResponses = collectFailedApiResponses(page);
    const apiRequest = page.request;

    await loginWithRoutes(page, username, password, "/runtime-contract/user");
    await expect(page).toHaveURL(/\/runtime-contract\/user$/);
    const adminToken = await readAccessToken(page);

    await page.getByRole("button", { name: "新增用户" }).click();
    const createDrawer = page.locator(".el-drawer", { hasText: "新增用户" });
    await expect(createDrawer).toBeVisible();
    await createDrawer.getByPlaceholder("请输入用户名").fill(lifecycleUsername);
    await createDrawer.getByPlaceholder("请输入用户昵称").fill(lifecycleInitialName);
    await createDrawer
      .locator(".el-form-item", { hasText: "所属部门" })
      .locator(".el-select__wrapper")
      .click();
    await page.getByRole("option", { name: lifecycleDeptName, exact: true }).click();
    await createDrawer
      .locator(".el-form-item", { hasText: "角色" })
      .locator(".el-select__wrapper")
      .click();
    await page.getByRole("option", { name: lifecycleRoleName, exact: true }).click();
    await page.keyboard.press("Escape");

    const createResponse = waitForApiResponse(page, "/api/v1/system/users/", "POST");
    await createDrawer.getByRole("button", { name: /确\s*定/ }).click();
    await createResponse;
    await expect(page.getByText("新增用户成功", { exact: true }).last()).toBeVisible();
    await searchUser(page, lifecycleUsername);
    await expect(userTableRow(page, lifecycleUsername)).toContainText(lifecycleInitialName);

    const createdUsersResponse = await apiRequest.get(`${apiBasePath}/system/users/`, {
      headers: { Authorization: `Bearer ${adminToken}` },
      params: { pageNum: 1, pageSize: 10, search: lifecycleUsername },
    });
    const createdUsers = await expectApiSuccess<UserPageResult>(createdUsersResponse);
    const createdUser = createdUsers.list.find((user) => user.username === lifecycleUsername);
    expect(createdUser).toBeDefined();
    if (!createdUser) {
      throw new Error("真实后端未返回刚创建的生命周期用户");
    }

    await userTableRow(page, lifecycleUsername)
      .getByRole("button", { name: "编辑", exact: true })
      .click();
    const editDrawer = page.locator(".el-drawer", { hasText: "修改用户" });
    await expect(editDrawer.getByPlaceholder("请输入用户昵称")).toHaveValue(lifecycleInitialName);
    await editDrawer.getByPlaceholder("请输入用户昵称").fill(lifecycleUpdatedName);
    const updateResponse = waitForApiResponse(
      page,
      `/api/v1/system/users/${createdUser.id}/`,
      "PUT"
    );
    await editDrawer.getByRole("button", { name: /确\s*定/ }).click();
    await updateResponse;
    await expect(page.getByText("修改用户成功", { exact: true }).last()).toBeVisible();
    await expect(userTableRow(page, lifecycleUsername)).toContainText(lifecycleUpdatedName);

    await userTableRow(page, lifecycleUsername)
      .getByRole("button", { name: "重置密码", exact: true })
      .click();
    const resetDialog = page.getByRole("dialog", { name: "重置密码" });
    await resetDialog.locator("input").fill(lifecyclePassword);
    const resetResponse = waitForApiResponse(
      page,
      `/api/v1/system/users/${createdUser.id}/password/reset/`,
      "PUT"
    );
    await resetDialog.getByRole("button", { name: "确定", exact: true }).click();
    await resetResponse;
    await expect(page.getByText(/密码重置成功/).last()).toBeVisible();

    const frontendBaseUrl = new URL(page.url()).origin;
    const lifecycleContext = await browser.newContext({ baseURL: frontendBaseUrl });
    const lifecyclePage = await lifecycleContext.newPage();
    const lifecycleFailures = collectFailedApiResponses(lifecyclePage);
    await loginWithRoutes(
      lifecyclePage,
      lifecycleUsername,
      lifecyclePassword,
      "/runtime-contract/user"
    );
    await expect(lifecyclePage).toHaveURL(/\/runtime-contract\/user$/);
    await expect(userTableRow(lifecyclePage, lifecycleUsername)).toContainText(
      lifecycleUpdatedName
    );
    expect(lifecycleFailures).toEqual([]);
    await lifecycleContext.close();

    await userTableRow(page, lifecycleUsername)
      .getByRole("button", { name: "编辑", exact: true })
      .click();
    const disableDrawer = page.locator(".el-drawer", { hasText: "修改用户" });
    const statusSwitch = disableDrawer.getByRole("switch");
    const statusSwitchControl = disableDrawer
      .locator(".el-form-item", { hasText: "状态" })
      .locator(".el-switch__core");
    await expect(statusSwitch).toHaveAttribute("aria-checked", "true");
    await statusSwitchControl.click();
    await expect(statusSwitch).toHaveAttribute("aria-checked", "false");
    const disableResponse = waitForApiResponse(
      page,
      `/api/v1/system/users/${createdUser.id}/`,
      "PUT"
    );
    await disableDrawer.getByRole("button", { name: /确\s*定/ }).click();
    await disableResponse;
    await expect(
      userTableRow(page, lifecycleUsername).getByText("禁用", { exact: true })
    ).toBeVisible();

    await expectLoginRejected(apiRequest, lifecycleUsername, lifecyclePassword);

    await userTableRow(page, lifecycleUsername)
      .getByRole("button", { name: "删除", exact: true })
      .click();
    const deleteResponse = waitForApiResponse(page, "/api/v1/system/users/", "DELETE");
    await page.getByRole("button", { name: "确定", exact: true }).click();
    await deleteResponse;
    await expect(page.getByText("删除成功，共 1 条", { exact: true }).last()).toBeVisible();
    await expect(userTableRow(page, lifecycleUsername)).toHaveCount(0);

    const deletedDetailResponse = await apiRequest.get(
      `${apiBasePath}/system/users/${createdUser.id}/`,
      { headers: { Authorization: `Bearer ${adminToken}` } }
    );
    expect(deletedDetailResponse.status()).toBe(404);
    await expectLoginRejected(apiRequest, lifecycleUsername, lifecyclePassword);
    expect(failedApiResponses).toEqual([]);
  });

  test("角色授权与撤权后同步动态菜单、按钮和接口权限", async ({ browser, page }) => {
    const failedApiResponses = collectFailedApiResponses(page);
    const apiRequest = page.request;

    const adminLoginResponse = await apiRequest.post(`${apiBasePath}/oauth/login/`, {
      data: { username, password },
    });
    const adminLoginData = await expectApiSuccess<{ accessToken: string }>(adminLoginResponse);
    const adminToken = adminLoginData.accessToken;

    const grantResponse = await apiRequest.put(`${apiBasePath}/system/roles/${rbacRoleId}/menus/`, {
      headers: { Authorization: `Bearer ${adminToken}` },
      data: { menuIds: rbacGrantedPermissionIds },
    });
    await expectApiSuccess(grantResponse);

    await loginWithRoutes(page, rbacUsername, rbacPassword, "/runtime-contract/user");
    await expect(page).toHaveURL(/\/runtime-contract\/user$/);
    await expect(
      page.locator(".layout__sidebar .el-menu-item", { hasText: "用户管理" })
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "新增用户" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "导入用户" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "导出用户" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: "批量删除" })).toHaveCount(0);

    const rbacToken = await readAccessToken(page);
    const allowedUsersResponse = await apiRequest.get(`${apiBasePath}/system/users/`, {
      headers: { Authorization: `Bearer ${rbacToken}` },
      params: { pageNum: 1, pageSize: 10 },
    });
    await expectApiSuccess(allowedUsersResponse);

    const frontendBaseUrl = new URL(page.url()).origin;
    await page.close();

    const revokeResponse = await apiRequest.put(
      `${apiBasePath}/system/roles/${rbacRoleId}/menus/`,
      {
        headers: { Authorization: `Bearer ${adminToken}` },
        data: { menuIds: rbacBasePermissionIds },
      }
    );
    await expectApiSuccess(revokeResponse);

    const revokedContext = await browser.newContext({ baseURL: frontendBaseUrl });
    const revokedPage = await revokedContext.newPage();
    const revokedFailedApiResponses = collectFailedApiResponses(revokedPage);
    await loginWithRoutes(revokedPage, rbacUsername, rbacPassword, "/dashboard");
    await expect(
      revokedPage.locator(".layout__sidebar .el-menu-item", { hasText: "用户管理" })
    ).toHaveCount(0);

    const revokedToken = await readAccessToken(revokedPage);
    const forbiddenUsersResponse = await apiRequest.get(`${apiBasePath}/system/users/`, {
      headers: { Authorization: `Bearer ${revokedToken}` },
      params: { pageNum: 1, pageSize: 10 },
    });
    expect(forbiddenUsersResponse.status()).toBe(403);
    expect(failedApiResponses).toEqual([]);
    expect(revokedFailedApiResponses).toEqual([]);
    await revokedContext.close();
  });

  test("文件上传、越权删除拒绝和所有者删除形成真实闭环", async ({ page }) => {
    const failedApiResponses = collectFailedApiResponses(page);
    const apiRequest = page.request;
    const fileName = `${backendName.toLowerCase()}-ownership.txt`;
    const fileContent = `${backendName} real file ownership smoke`;

    await loginWithRoutes(page, username, password, "/runtime-contract/upload");
    await expect(page).toHaveURL(/\/runtime-contract\/upload$/);
    const fileUploadFormItem = page.locator(".el-form-item", { hasText: "文件上传" });
    await expect(fileUploadFormItem.getByRole("button", { name: "上传文件" })).toBeVisible();

    const uploadResponsePromise = waitForApiResponse(page, "/api/v1/files/", "POST");
    await fileUploadFormItem.locator('input[type="file"]').setInputFiles({
      name: fileName,
      mimeType: "text/plain",
      buffer: Buffer.from(fileContent),
    });
    const uploadResponse = await uploadResponsePromise;
    const uploadedFile = await expectPageApiSuccess<UploadedFileInfo>(uploadResponse);
    expect(uploadedFile).toMatchObject({ name: fileName });
    expect(uploadedFile.path).toMatch(/^files\/\d+\/[^/]+\.txt$/);
    expect(uploadedFile.url).toContain(`/media/${uploadedFile.path}`);

    const uploadedRow = fileUploadFormItem
      .locator(".el-upload-list__item")
      .filter({ hasText: fileName });
    await expect(uploadedRow).toBeVisible();

    const mediaBeforeDelete = await apiRequest.get(uploadedFile.url);
    expect(mediaBeforeDelete.status()).toBe(200);
    expect((await mediaBeforeDelete.body()).toString()).toBe(fileContent);

    const otherLoginResponse = await apiRequest.post(`${apiBasePath}/oauth/login/`, {
      data: { username: rbacUsername, password: rbacPassword },
    });
    const otherLoginData = await expectApiSuccess<{ accessToken: string }>(otherLoginResponse);
    const forbiddenDeleteResponse = await apiRequest.delete(`${apiBasePath}/files/`, {
      headers: { Authorization: `Bearer ${otherLoginData.accessToken}` },
      params: { filePath: uploadedFile.path },
    });
    expect(forbiddenDeleteResponse.status()).toBe(403);
    const forbiddenPayload = (await forbiddenDeleteResponse.json()) as { code?: number };
    expect(forbiddenPayload.code).not.toBe(20000);

    const mediaAfterForbiddenDelete = await apiRequest.get(uploadedFile.url);
    expect(mediaAfterForbiddenDelete.status()).toBe(200);

    const deleteResponsePromise = waitForApiResponse(page, "/api/v1/files/", "DELETE");
    await uploadedRow.hover();
    await uploadedRow.locator(".el-icon--close").click();
    await expectPageApiSuccess(await deleteResponsePromise);
    await expect(fileUploadFormItem.getByText(fileName)).toHaveCount(0);

    const mediaAfterOwnerDelete = await apiRequest.get(uploadedFile.url);
    expect(mediaAfterOwnerDelete.status()).toBe(404);
    expect(failedApiResponses).toEqual([]);
  });

  test("菜单创建、编辑、授权和删除同步动态路由", async ({ browser, page }) => {
    const failedApiResponses = collectFailedApiResponses(page);
    const apiRequest = page.request;

    await loginWithRoutes(page, username, password, "/runtime-contract/menus");
    await expect(page).toHaveURL(/\/runtime-contract\/menus$/);
    await expect(page.getByText("菜单数据", { exact: true })).toBeVisible();
    const adminToken = await readAccessToken(page);

    const catalogRow = menuTableRow(page, "契约目录");
    await expect(catalogRow).toBeVisible();
    await catalogRow.getByRole("button", { name: "新增", exact: true }).click();

    const createDrawer = page.locator(".el-drawer", { hasText: "新增菜单" });
    await expect(createDrawer).toBeVisible();
    await createDrawer.getByPlaceholder("请输入菜单名称").fill(menuWriteInitialName);
    await createDrawer.getByRole("textbox", { name: "* 路由名称" }).fill(menuWriteRouteName);
    await createDrawer.getByRole("textbox", { name: "* 路由路径" }).fill(menuWriteRoutePath);
    await createDrawer.getByRole("textbox", { name: "* 组件路径" }).fill("system/user/index");

    const createResponse = waitForApiResponse(page, "/api/v1/system/menus/", "POST");
    await createDrawer.getByRole("button", { name: /确\s*定/ }).click();
    await createResponse;
    await expect(page.getByText("新增成功", { exact: true }).last()).toBeVisible();
    await expandMenuTableRow(page, "契约目录");
    await expect(menuTableRow(page, menuWriteInitialName)).toBeVisible();

    const menuTreeResponse = await apiRequest.get(`${apiBasePath}/system/menus/`, {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    const menuTree = await expectApiSuccess<MenuTreeItem[]>(menuTreeResponse);
    const catalog = findMenuByRouteName(menuTree, menuCatalogRouteName);
    const createdMenu = findMenuByRouteName(menuTree, menuWriteRouteName);
    expect(catalog).toBeDefined();
    expect(createdMenu).toMatchObject({
      name: menuWriteInitialName,
      routePath: menuWriteRoutePath,
      component: "system/user/index",
    });
    if (!catalog || !createdMenu) {
      throw new Error("创建的菜单或父目录未出现在真实菜单树中");
    }
    expect(Number(createdMenu.parentId)).toBe(Number(catalog.id));

    await menuTableRow(page, menuWriteInitialName)
      .getByRole("button", { name: "新增", exact: true })
      .click();
    const permissionDrawer = page.locator(".el-drawer", { hasText: "新增菜单" });
    await expect(permissionDrawer).toBeVisible();
    await permissionDrawer.getByPlaceholder("请输入菜单名称").fill(menuWritePermissionName);
    await permissionDrawer.locator(".el-radio", { hasText: "按钮" }).click();
    await permissionDrawer.getByPlaceholder("sys:user:add").fill("system:users:query");

    const createPermissionResponse = waitForApiResponse(page, "/api/v1/system/menus/", "POST");
    await permissionDrawer.getByRole("button", { name: /确\s*定/ }).click();
    await createPermissionResponse;
    await expect(page.getByText("新增成功", { exact: true }).last()).toBeVisible();

    const permissionTreeResponse = await apiRequest.get(`${apiBasePath}/system/menus/`, {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    const permissionTree = await expectApiSuccess<MenuTreeItem[]>(permissionTreeResponse);
    const createdPermission = findMenuByName(permissionTree, menuWritePermissionName);
    expect(createdPermission).toMatchObject({
      type: "BUTTON",
      perm: "system:users:query",
    });
    if (!createdPermission) {
      throw new Error("创建的按钮权限未出现在真实菜单树中");
    }
    expect(Number(createdPermission.parentId)).toBe(Number(createdMenu.id));

    const grantResponse = await apiRequest.put(`${apiBasePath}/system/roles/${rbacRoleId}/menus/`, {
      headers: { Authorization: `Bearer ${adminToken}` },
      data: {
        menuIds: [
          ...rbacBasePermissionIds,
          Number(catalog.id),
          Number(createdMenu.id),
          Number(createdPermission.id),
        ],
      },
    });
    await expectApiSuccess(grantResponse);

    const frontendBaseUrl = new URL(page.url()).origin;
    const initialUserContext = await browser.newContext({ baseURL: frontendBaseUrl });
    const initialUserPage = await initialUserContext.newPage();
    const initialUserFailures = collectFailedApiResponses(initialUserPage);
    await loginWithRoutes(
      initialUserPage,
      rbacUsername,
      rbacPassword,
      `/runtime-contract/${menuWriteRoutePath}`
    );
    await expect(initialUserPage).toHaveURL(new RegExp(`/runtime-contract/${menuWriteRoutePath}$`));
    await expect(sidebarMenuItem(initialUserPage, menuWriteInitialName)).toBeVisible();
    expect(initialUserFailures).toEqual([]);
    await initialUserContext.close();

    const initialRow = menuTableRow(page, menuWriteInitialName);
    await initialRow.getByRole("button", { name: "编辑", exact: true }).click();
    const editDrawer = page.locator(".el-drawer", { hasText: "编辑菜单" });
    await expect(editDrawer).toBeVisible();
    await editDrawer.getByPlaceholder("请输入菜单名称").fill(menuWriteUpdatedName);
    const updateResponse = waitForApiResponse(
      page,
      `/api/v1/system/menus/${createdMenu.id}/`,
      "PUT"
    );
    await editDrawer.getByRole("button", { name: /确\s*定/ }).click();
    await updateResponse;
    await expect(page.getByText("修改成功", { exact: true }).last()).toBeVisible();
    await expandMenuTableRow(page, "契约目录");
    await expect(menuTableRow(page, menuWriteUpdatedName)).toBeVisible();

    const updatedUserContext = await browser.newContext({ baseURL: frontendBaseUrl });
    const updatedUserPage = await updatedUserContext.newPage();
    const updatedUserFailures = collectFailedApiResponses(updatedUserPage);
    await loginWithRoutes(updatedUserPage, rbacUsername, rbacPassword, "/dashboard");
    await expect(sidebarMenuItem(updatedUserPage, menuWriteUpdatedName)).toBeVisible();
    await expect(sidebarMenuItem(updatedUserPage, menuWriteInitialName)).toHaveCount(0);
    expect(updatedUserFailures).toEqual([]);
    await updatedUserContext.close();

    await expandMenuTableRow(page, menuWriteUpdatedName);
    const permissionRow = menuTableRow(page, menuWritePermissionName);
    await permissionRow.getByRole("button", { name: "删除", exact: true }).click();
    const deletePermissionResponse = waitForApiResponse(
      page,
      `/api/v1/system/menus/${createdPermission.id}/`,
      "DELETE"
    );
    await page.getByRole("button", { name: "确定", exact: true }).click();
    await deletePermissionResponse;
    await expect(page.getByText("删除成功", { exact: true }).last()).toBeVisible();

    await expandMenuTableRow(page, "契约目录");
    const updatedRow = menuTableRow(page, menuWriteUpdatedName);
    await updatedRow.getByRole("button", { name: "删除", exact: true }).click();
    const deleteResponse = waitForApiResponse(
      page,
      `/api/v1/system/menus/${createdMenu.id}/`,
      "DELETE"
    );
    await page.getByRole("button", { name: "确定", exact: true }).click();
    await deleteResponse;
    await expect(page.getByText("删除成功", { exact: true }).last()).toBeVisible();
    await expect(menuTableRow(page, menuWriteUpdatedName)).toHaveCount(0);

    const deletedUserContext = await browser.newContext({ baseURL: frontendBaseUrl });
    const deletedUserPage = await deletedUserContext.newPage();
    const deletedUserFailures = collectFailedApiResponses(deletedUserPage);
    await loginWithRoutes(deletedUserPage, rbacUsername, rbacPassword, "/dashboard");
    await expect(sidebarMenuItem(deletedUserPage, menuWriteUpdatedName)).toHaveCount(0);
    const deletedUserToken = await readAccessToken(deletedUserPage);
    const forbiddenUsersResponse = await apiRequest.get(`${apiBasePath}/system/users/`, {
      headers: { Authorization: `Bearer ${deletedUserToken}` },
      params: { pageNum: 1, pageSize: 10 },
    });
    expect(forbiddenUsersResponse.status()).toBe(403);
    expect(failedApiResponses).toEqual([]);
    expect(deletedUserFailures).toEqual([]);
    await deletedUserContext.close();
  });
});

function menuTableRow(page: Page, name: string) {
  return page
    .locator(".ff-menu-page .el-table__row")
    .filter({ has: page.getByText(name, { exact: true }) })
    .first();
}

function userTableRow(page: Page, usernameToFind: string) {
  return page
    .locator(".ff-user-page .el-table__row")
    .filter({ has: page.getByText(usernameToFind, { exact: true }) })
    .first();
}

async function searchUser(page: Page, usernameToFind: string): Promise<void> {
  await page.getByPlaceholder("用户名/昵称/手机号").fill(usernameToFind);
  const searchResponse = waitForApiResponse(page, "/api/v1/system/users/", "GET");
  await page.getByRole("button", { name: "搜索", exact: true }).click();
  await searchResponse;
}

async function expandMenuTableRow(page: Page, name: string) {
  const expandButton = menuTableRow(page, name).locator(".el-table__expand-icon");
  await expect(expandButton).toBeVisible();
  if (!(await expandButton.getAttribute("class"))?.includes("el-table__expand-icon--expanded")) {
    await expandButton.click();
  }
}

function sidebarMenuItem(page: Page, name: string) {
  return page.locator(".layout__sidebar .el-menu-item", { hasText: name });
}

function findMenuByRouteName(menus: MenuTreeItem[], routeName: string): MenuTreeItem | undefined {
  for (const menu of menus) {
    if (menu.routeName === routeName) return menu;
    const child = findMenuByRouteName(menu.children ?? [], routeName);
    if (child) return child;
  }
  return undefined;
}

function findMenuByName(menus: MenuTreeItem[], name: string): MenuTreeItem | undefined {
  for (const menu of menus) {
    if (menu.name === name) return menu;
    const child = findMenuByName(menu.children ?? [], name);
    if (child) return child;
  }
  return undefined;
}

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required for the real backend Playwright smoke`);
  }
  return value;
}

function requireIntegerEnv(name: string): number {
  const value = Number(requireEnv(name));
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error(`${name} must be a positive integer`);
  }
  return value;
}

function requireIntegerListEnv(name: string): number[] {
  const values = requireEnv(name)
    .split(",")
    .map((value) => Number(value));
  if (values.length === 0 || values.some((value) => !Number.isInteger(value) || value <= 0)) {
    throw new Error(`${name} must be a comma-separated list of positive integers`);
  }
  return values;
}

async function loginWithRoutes(
  page: Page,
  loginUsername: string,
  loginPassword: string,
  redirect: string
): Promise<void> {
  await page.goto(`/login?redirect=${encodeURIComponent(redirect)}`);
  await page.getByLabel("用户名").fill(loginUsername);
  await page.getByLabel("密码").fill(loginPassword);

  const loginBootstrap = Promise.all([
    waitForApiResponse(page, "/api/v1/oauth/login/", "POST"),
    waitForApiResponse(page, "/api/v1/oauth/info/", "GET"),
    waitForApiResponse(page, "/api/v1/oauth/menus/routes/", "GET"),
  ]);
  await page.getByRole("button", { name: /登\s*录|Login/i }).click();
  await loginBootstrap;
}

async function readAccessToken(page: Page): Promise<string> {
  const token = await page.evaluate((storageKey) => {
    const rawValue = sessionStorage.getItem(storageKey) ?? localStorage.getItem(storageKey);
    if (!rawValue) return "";
    try {
      const value: unknown = JSON.parse(rawValue);
      return typeof value === "string" ? value : "";
    } catch {
      return rawValue;
    }
  }, accessTokenStorageKey);
  expect(token).not.toBe("");
  return token;
}

async function expectApiSuccess<T = unknown>(response: APIResponse): Promise<T> {
  expect(response.status(), await response.text()).toBe(200);
  const payload = (await response.json()) as { code?: number; data?: T };
  expect(payload.code).toBe(20000);
  return payload.data as T;
}

async function expectPageApiSuccess<T = unknown>(response: Response): Promise<T> {
  expect(response.status(), await response.text()).toBe(200);
  const payload = (await response.json()) as { code?: number; data?: T };
  expect(payload.code).toBe(20000);
  return payload.data as T;
}

async function expectLoginRejected(
  apiRequest: APIRequestContext,
  loginUsername: string,
  loginPassword: string
): Promise<void> {
  const response = await apiRequest.post(`${apiBasePath}/oauth/login/`, {
    data: { username: loginUsername, password: loginPassword },
  });
  expect(response.status()).toBeGreaterThanOrEqual(400);
  const payload = (await response.json()) as { code?: number };
  expect(payload.code).not.toBe(20000);
}

function waitForApiResponse(page: Page, path: string, method: string): Promise<Response> {
  return page.waitForResponse(
    (response) =>
      response.url().includes(path) &&
      response.request().method() === method &&
      response.status() >= 200 &&
      response.status() < 300
  );
}

function collectFailedApiResponses(page: Page): string[] {
  const failures: string[] = [];
  page.on("response", (response) => {
    if (response.url().includes("/dev-api/api/v1/") && response.status() >= 400) {
      failures.push(`${response.status()} ${response.request().method()} ${response.url()}`);
    }
  });
  return failures;
}
