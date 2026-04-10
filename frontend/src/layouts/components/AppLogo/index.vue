<template>
  <div class="sidebar-logo-container" :class="{ collapse: collapse }">
    <transition name="sidebarLogoFade">
      <router-link v-if="collapse" key="collapse" class="sidebar-logo-link" to="/">
        <div class="cyber-logo-mini">
          <div class="logo-glow"></div>
          <div class="logo-glass"><span class="logo-letter">D</span></div>
        </div>
      </router-link>
      
      <router-link v-else key="expand" class="sidebar-logo-link" to="/">
        <div class="cyber-logo-mini">
          <div class="logo-glow"></div>
          <div class="logo-glass"><span class="logo-letter">DV</span></div>
        </div>
        <h1 class="sidebar-title">DV Admin</h1>
      </router-link>
    </transition>
  </div>
</template>

<script lang="ts" setup>
defineProps({
  collapse: {
    type: Boolean,
    required: true,
  },
});
</script>

<style lang="scss" scoped>
/* ============================================
   左上角：迷你全息玻璃态 Logo
   ============================================ */
.cyber-logo-mini {
  position: relative;
  width: 32px;
  height: 32px;
  margin-right: 12px;
  display: flex;
  justify-content: center;
  align-items: center;

  /* 底层呼吸光晕 */
  .logo-glow {
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    border-radius: 10px; /* 柔和的小圆角 */
    transform: rotate(-15deg);
    filter: blur(6px);
    opacity: 0.8;
    animation: pulseGlowMini 4s ease-in-out infinite alternate;
  }

  /* 顶层玻璃晶体 */
  .logo-glass {
    position: relative;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, rgba(255, 255, 255, 0.05) 100%);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.6);
    box-shadow: inset 0 0 8px rgba(255, 255, 255, 0.3), 0 4px 12px rgba(0, 0, 0, 0.05);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1;

    /* 内部金属白字 */
    .logo-letter {
      font-size: 14px;
      font-weight: 900;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
  }
}

@keyframes pulseGlowMini {
  0% { transform: rotate(-15deg) scale(0.95); opacity: 0.6; }
  100% { transform: rotate(-5deg) scale(1.05); opacity: 1; }
}

/* ============================================
   赛博渐变平台标题
   ============================================ */
.sidebar-title {
  font-size: 18px; /* 根据实际视觉微调 */
  font-weight: 800;
  margin: 0;
  letter-spacing: 0.5px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  
  /* 类似钛金属的冷蓝灰渐变 */
  background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  
  /* 防止在折叠动画时闪烁 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ============================================
   Logo 容器和链接样式
   ============================================ */
.sidebar-logo-container {
  width: 100%;
  height: $navbar-height;
  display: flex;
  align-items: center;
  padding: 0 16px;
  background-color: $sidebar-logo-background;
  transition: all 0.3s ease;

  &.collapse {
    justify-content: center;
    padding: 0;
  }
}

.sidebar-logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  width: 100%;
  height: 100%;
}

/* 过渡动画 */
.sidebarLogoFade-enter-active,
.sidebarLogoFade-leave-active {
  transition: opacity 0.3s;
}

.sidebarLogoFade-enter-from,
.sidebarLogoFade-leave-to {
  opacity: 0;
}

/* ============================================
   全局深色模式适配 (Dark Mode)
   ============================================ */
:global(html.dark) .sidebar-title {
  /* 深色模式下的文字亮蓝白渐变 */
  background: linear-gradient(135deg, #f8fafc 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

:global(html.dark) .cyber-logo-mini .logo-glass {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.02) 100%);
  border-color: rgba(255, 255, 255, 0.2);
}
</style>

<style lang="scss">
// 顶部布局和混合布局的特殊处理
.layout-top,
.layout-mix {
  .sidebar-logo-container {
    background-color: transparent !important;
  }
}

// 宽屏时：openSidebar 状态下显示完整Logo+文字
.openSidebar {
  &.layout-top .layout__header-left .sidebar-logo-container,
  &.layout-mix .layout__header-logo .sidebar-logo-container {
    width: $sidebar-width; // 210px，显示logo+文字
  }
}

// 窄屏时：hideSidebar 状态下只显示Logo图标
.hideSidebar {
  &.layout-top .layout__header-left .sidebar-logo-container,
  &.layout-mix .layout__header-logo .sidebar-logo-container {
    width: $sidebar-width-collapsed; // 54px，只显示logo
  }

  // 隐藏文字，只显示图标
  .sidebar-logo-container .sidebar-title {
    display: none;
  }
}
</style>
