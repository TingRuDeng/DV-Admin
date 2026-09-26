/**
 * 菜单布局枚举
 */
export const enum LayoutMode {
  /**
   * 左侧菜单布局
   */
  LEFT = "left",
  /**
   * 顶部菜单布局
   */
  TOP = "top",

  /**
   * 混合菜单布局
   */
  MIX = "mix",

  /**
   * 双列布局：左侧一级菜单图标栏 + 第二列子菜单（移动端退化为左侧布局）
   */
  DOUBLE = "double",
}

/**
 * 侧边栏状态枚举
 */
export const enum SidebarStatus {
  /**
   * 展开
   */
  OPENED = "opened",

  /**
   * 关闭
   */
  CLOSED = "closed",
}

/**
 * 组件尺寸枚举
 */
export const enum ComponentSize {
  /**
   * 默认
   */
  DEFAULT = "default",

  /**
   * 大型
   */
  LARGE = "large",

  /**
   * 小型
   */
  SMALL = "small",
}
