<template>
  <div class="dialog-footer">
    <div class="ctrl-k-hint">
      <span class="ctrl-k-text">Ctrl+K 快速打开</span>
    </div>
    <div class="shortcuts-group">
      <div class="key-box">
        <div class="key-btn">选择</div>
      </div>
      <div class="arrow-box">
        <div class="arrow-up-down">
          <div class="key-btn">
            <div class="i-svg:up" />
          </div>
          <div class="key-btn ml-1">
            <div class="i-svg:down" />
          </div>
        </div>
        <span class="key-text">切换</span>
      </div>
      <div class="key-box">
        <div class="key-btn esc-btn">ESC</div>
        <span class="key-text">关闭</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.shortcuts-group {
  display: flex;
  gap: 15px;
  align-items: center;
}

.key-box,
.arrow-box,
.arrow-up-down,
.ctrl-k-hint {
  display: flex;
  align-items: center;
}

.key-box,
.arrow-box {
  gap: 5px;
}

.arrow-up-down {
  gap: 2px;
}

.key-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 20px;
  padding: 0 4px;
  font-size: 12px;
  color: var(--el-text-color-regular);
  background-color: var(--el-fill-color-blank);
  border: 1px solid var(--el-border-color);
  border-radius: 3px;
  box-shadow:
    inset 0 -2px 0 0 var(--el-border-color),
    inset 0 0 1px 1px var(--el-color-white),
    0 1px 2px rgba(30, 35, 90, 0.2);

  &::before {
    position: absolute;
    top: 1px;
    right: 1px;
    left: 1px;
    height: 50%;
    pointer-events: none;
    content: "";
    background: linear-gradient(to bottom, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0));
    border-radius: 2px 2px 0 0;
  }
}

.esc-btn {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 11px;
}

.key-text,
.ctrl-k-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

:global(html.dark) {
  .key-btn::before {
    background: linear-gradient(to bottom, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0));
  }
}
</style>
