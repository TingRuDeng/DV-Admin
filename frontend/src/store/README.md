# 前端状态管理模块

> 本模块管理前端全局状态，是前端架构的核心部分。

---

## 模块概述

使用 Pinia 进行状态管理，采用 Composition API 风格。

**位置：** `frontend/src/store/`

---

## Store 列表

| Store | 文件 | 用途 |
|-------|------|------|
| User | `modules/user-store.ts` | 用户认证和信息 |
| Permission | `modules/permission-store.ts` | 权限和动态路由 |
| Dict | `modules/dict-store.ts` | 字典数据缓存 |
| Settings | `modules/settings-store.ts` | 系统设置 |
| App | `modules/app-store.ts` | 应用状态 |
| TagsView | `modules/tags-view-store.ts` | 标签视图 |

---

## User Store

**文件：** `modules/user-store.ts`

**状态：**
- `userInfo`: 用户信息对象
- `rememberMe`: 记住我状态

**方法：**
- `login(LoginFormData)`: 登录
- `logout()`: 登出
- `getUserInfo()`: 获取用户信息
- `refreshToken()`: 刷新 Token
- `resetAllState()`: 重置所有状态

**使用示例：**
```typescript
import { useUserStoreHook } from '@/store/modules/user-store'

// 登录
await useUserStoreHook().login({ username, password })

// 获取用户信息
const userInfo = await useUserStoreHook().getUserInfo()

// 登出
await useUserStoreHook().logout()
```

**注意事项：**
- 登出时会自动清理所有相关状态
- Token 存储在 `AuthStorage` 中，不在 Store 中

---

## Permission Store

**文件：** `modules/permission-store.ts`

**状态：**
- `routes`: 动态路由列表
- `addRoutes`: 已添加的路由

**方法：**
- `generateRoutes()`: 生成动态路由
- `resetRouter()`: 重置路由

**使用示例：**
```typescript
import { usePermissionStoreHook } from '@/store/modules/permission-store'

// 生成路由
const routes = await usePermissionStoreHook().generateRoutes()

// 重置路由
usePermissionStoreHook().resetRouter()
```

**注意事项：**
- 路由数据从后端获取
- 登出时必须调用 `resetRouter()`

---

## Dict Store

**文件：** `modules/dict-store.ts`

**状态：**
- `dictCache`: 字典缓存对象

**方法：**
- `getDictItems(dictCode)`: 获取字典项
- `getDictLabel(dictCode, value)`: 获取字典标签
- `clearDictCache()`: 清除缓存

**使用示例：**
```typescript
import { useDictStoreHook } from '@/store/modules/dict-store'

// 获取字典项
const items = await useDictStoreHook().getDictItems('status')

// 获取标签
const label = useDictStoreHook().getDictLabel('status', '1')
```

**注意事项：**
- 字典数据会缓存
- 支持 WebSocket 实时同步

---

## 修改指南

### 新增 Store

1. 在 `modules/` 目录创建新文件
2. 使用 `defineStore` 定义 Store
3. 在 `index.ts` 中导出
4. 更新本 README

### 修改 Store

1. 阅读现有代码，理解状态结构
2. 修改时考虑副作用
3. 确保登出时正确清理状态
4. 更新相关文档

---

## 常见陷阱

### 陷阱 1：在组件外使用 Store

**错误：**
```typescript
// 直接使用 useUserStore() 会在组件外报错
const store = useUserStore()
```

**正确：**
```typescript
// 使用 Hook 函数
import { useUserStoreHook } from '@/store/modules/user-store'
const store = useUserStoreHook()
```

### 陷阱 2：状态未清理

**问题：** 登出后状态残留

**解决：** 在 `resetAllState()` 中调用各 Store 的重置方法

---

**最后更新：** 2026-03-23
