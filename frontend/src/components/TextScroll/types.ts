export interface TextScrollProps {
  /** 滚动文本内容（必填） */
  text: string;
  /** 滚动速度，数值越小滚动越慢 */
  speed?: number;
  /** 滚动方向：左侧或右侧 */
  direction?: "left" | "right";
  /** 样式类型 */
  type?: "default" | "success" | "warning" | "danger" | "info";
  /** 是否显示关闭按钮 */
  showClose?: boolean;
  /** 是否启用打字机效果 */
  typewriter?: boolean;
  /** 打字机效果的速度，数值越小打字越快 */
  typewriterSpeed?: number;
}
