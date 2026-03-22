# 前端单元测试

## 概述

本文档介绍 DV-Admin 前端的单元测试配置和使用方法。

## 技术栈

- 测试框架: Vitest
- 组件测试: @vue/test-utils
- DOM 环境: happy-dom
- Mock: Vitest 内置 mock

## 测试结果

```
11 tests passed
```

## 目录结构

```
frontend/
├── vitest.config.ts              # 测试配置
├── src/
│   └── utils/
│       └── __tests__/
│           ├── basic.test.ts     # 基础测试
│           └── storage.test.ts   # 存储工具测试
```

## 安装依赖

测试依赖已安装：

```bash
pnpm add -D vitest @vue/test-utils jsdom @testing-library/vue happy-dom
```

## 测试配置

`vitest.config.ts`:

```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    include: ['src/**/*.{test,spec}.{js,ts}'],
    exclude: ['node_modules', 'dist', 'e2e', 'src/store/**', 'src/router/**'],
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
})
```

## 运行测试

### 运行所有测试

```bash
cd frontend
pnpm test
```

### 运行测试（单次）

```bash
pnpm test:run
```

### 运行测试（UI 模式）

```bash
pnpm test:ui
```

### 运行覆盖率

```bash
pnpm test:coverage
```

## 测试覆盖

| 模块 | 测试用例 |
|------|----------|
| 基础测试 | 字符串、数组、对象操作 |
| 存储工具 | 设置、获取、删除、清空存储 |

## 注意事项

### API 测试

由于前端 API 模块依赖于 `request` 工具函数，该函数内部使用了大量全局状态和配置（如 baseURL、拦截器等），在测试环境中难以完整模拟。建议采用以下方式进行 API 测试：

1. **E2E 测试**: 使用 Playwright/Cypress 进行端到端测试
2. **手动测试**: 在开发环境中通过接口调试工具验证
3. **Mock 服务**: 使用 MSW (Mock Service Worker) 进行 API 拦截测试

### 当前测试状态

- ✅ 工具函数测试: 11 个测试通过
- ⚠️ API 测试: 需要更复杂的 Mock 配置，建议使用 E2E 测试框架

## 添加新测试

### 创建测试文件

```typescript
// src/utils/__tests__/example.test.ts
import { describe, it, expect } from 'vitest'

describe('example', () => {
  it('should pass', () => {
    expect(1 + 1).toBe(2)
  })
})
```

### 组件测试示例

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('renders correctly', () => {
    const wrapper = mount(MyComponent, {
      props: {
        msg: 'Hello'
      }
    })
    expect(wrapper.text()).toContain('Hello')
  })
})
```

## 常见问题

### 1. 导入失败

**问题**: `__APP_INFO__ is not defined`

**解决**: 排除依赖 store/router 的测试文件，或使用 mock

### 2. Store 导入失败

**问题**: Pinia store 导入失败

**解决**: 在 `vitest.config.ts` 中排除 store 目录

```typescript
exclude: ['node_modules', 'dist', 'e2e', 'src/store/**']
```

### 3. Router 导入失败

**问题**: Vue Router 导入失败

**解决**: 排除 router 目录

```typescript
exclude: ['node_modules', 'dist', 'e2e', 'src/store/**', 'src/router/**']
```

## 测试最佳实践

1. **文件命名**: 使用 `{name}.test.ts` 或 `{name}.spec.ts`
2. **测试位置**: 放在 `__tests__` 目录中
3. **描述性命名**: 使用清晰的测试描述
4. **独立性**: 每个测试应该独立运行
5. **Mock 依赖**: 避免导入复杂的 store/router 模块

## 扩展测试

### 添加 API 测试

```typescript
import { describe, it, expect, vi } from 'vitest'
import axios from 'axios'

vi.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('api', () => {
  it('should fetch users', async () => {
    mockedAxios.get.mockResolvedValue({ data: [] })
    const result = await axios.get('/api/users')
    expect(result.data).toEqual([])
  })
})
```

### 添加 Vue 组件测试

```typescript
import { describe, it, expect, shallowMount } from '@vitest/vue'
import MyButton from './MyButton.vue'

describe('MyButton', () => {
  it('emits click event', () => {
    const wrapper = shallowMount(MyButton)
    wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```
